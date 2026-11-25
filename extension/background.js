// Service worker: injeta o coletor, guarda progresso, salva arquivos e fala com o LM Studio.

const setState = (patch) =>
  chrome.storage.local.get("cpState").then(({ cpState }) =>
    chrome.storage.local.set({ cpState: { ...(cpState || {}), ...patch, updatedAt: Date.now() } })
  );

const stamp = () => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
};

function download(content, filename, mime) {
  const url = `data:${mime};charset=utf-8,` + encodeURIComponent(content);
  return chrome.downloads.download({ url, filename, saveAs: false, conflictAction: "uniquify" });
}

async function sendToLMStudio(cfg, data) {
  const base = (cfg.lmUrl || "http://localhost:1235").replace(/\/+$/, "");
  const body = {
    model: cfg.lmModel || "qwen/qwen3.8-27b",
    temperature: 0.1,
    messages: [
      { role: "system", content: cfg.lmPrompt || "Você recebe um JSON de reembolsos de plano de saúde. Resuma por beneficiário e por status, some valores solicitados e reembolsados e aponte pendências." },
      { role: "user", content: JSON.stringify(data.reembolsos) },
    ],
  };
  const res = await fetch(base + "/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`LM Studio respondeu ${res.status}`);
  const json = await res.json();
  return json.choices?.[0]?.message?.content || JSON.stringify(json);
}

const CONSULTA_PATH = "/portal/portal/modulos/reembolso/consultaReembolso.aspx";
const CONSULTA_URL = "https://www8.careplus.com.br" + CONSULTA_PATH;

function waitTabComplete(tabId, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { chrome.tabs.onUpdated.removeListener(fn); reject(new Error("Portal demorou para carregar")); }, timeout);
    function fn(id, info, tab) {
      if (id === tabId && info.status === "complete") {
        clearTimeout(timer);
        chrome.tabs.onUpdated.removeListener(fn);
        resolve(tab);
      }
    }
    chrome.tabs.onUpdated.addListener(fn);
  });
}

// Garante que a aba está em Consultar Reembolsos (logado). Retorna o tabId a usar.
async function openConsulta(tabId) {
  let tab = tabId ? await chrome.tabs.get(tabId).catch(() => null) : null;
  const onCareplus = tab && /^https:\/\/[^/]*careplus\.com\.br\//i.test(tab.url || "");
  if (tab && onCareplus && (tab.url || "").includes(CONSULTA_PATH)) {
    // já está na tela: recarrega para começar do passo inicial (lista de beneficiários)
    const p = waitTabComplete(tab.id);
    await chrome.tabs.reload(tab.id);
    tab = await p;
  } else if (tab && onCareplus) {
    // dentro do portal: usa o mesmo item de menu do site (mp_acesso), com fallback para a URL direta
    const p = waitTabComplete(tab.id);
    const [{ result: viaMenu } = {}] = await chrome.scripting.executeScript({
      target: { tabId: tab.id }, world: "MAIN",
      func: (path) => { if (typeof window.mp_acesso === "function") { window.mp_acesso("38", path, "0"); return true; } return false; },
      args: [CONSULTA_PATH],
    });
    if (!viaMenu) await chrome.tabs.update(tab.id, { url: CONSULTA_URL });
    tab = await p;
  } else {
    // fora do portal: abre numa aba nova (a sessão/cookies do login são reaproveitados)
    tab = await chrome.tabs.create({ url: CONSULTA_URL, active: true });
    tab = await waitTabComplete(tab.id);
  }
  tab = await chrome.tabs.get(tab.id);
  if (!(tab.url || "").includes(CONSULTA_PATH)) {
    throw new Error("Não consegui abrir Consultar Reembolsos — faça login no portal Care Plus e tente de novo.");
  }
  return tab.id;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    if (msg.type === "start") {
      const { cfg } = msg;
      await chrome.storage.local.set({ cpCfg: cfg });
      await setState({ running: true, done: 0, text: "Abrindo Consultar Reembolsos…", error: null, result: null });
      const tabId = await openConsulta(msg.tabId);
      await chrome.scripting.executeScript({ target: { tabId }, world: "MAIN", files: ["collector.js"] });
      await chrome.scripting.executeScript({
        target: { tabId }, world: "MAIN",
        func: (c) => window.__cpCollector.start(c), args: [cfg],
      });
      sendResponse({ ok: true });
    } else if (msg.type === "stop") {
      await chrome.scripting.executeScript({
        target: { tabId: msg.tabId }, world: "MAIN",
        func: () => window.__cpCollector && window.__cpCollector.stop(),
      });
      await setState({ text: "Parando…" });
      sendResponse({ ok: true });
    } else if (msg.type === "cp-progress") {
      await setState({ running: true, ...msg.payload });
    } else if (msg.type === "cp-error") {
      await setState({ running: false, error: msg.payload.message });
    } else if (msg.type === "cp-done") {
      const data = msg.payload;
      const { cpCfg: cfg = {} } = await chrome.storage.local.get("cpCfg");
      const base = `careplus-reembolsos-${stamp()}`;
      await download(JSON.stringify(data, null, 2), base + ".json", "application/json");
      let lmStatus = null;
      if (cfg.useLM) {
        await setState({ text: "Enviando ao LM Studio…" });
        try {
          const answer = await sendToLMStudio(cfg, data);
          const summary = {
            schema_version: 1,
            generated_at: new Date().toISOString(),
            model: cfg.lmModel || null,
            content: answer,
          };
          await download(JSON.stringify(summary, null, 2), base + "-lmstudio.json", "application/json");
          lmStatus = "ok";
        } catch (e) {
          lmStatus = "falhou: " + e.message;
        }
      }
      await setState({
        running: false,
        text: `Concluído: ${data.total} reembolsos` + (data.erros.length ? ` (${data.erros.length} erro(s))` : "") + (lmStatus ? ` · LM Studio ${lmStatus}` : ""),
        result: { total: data.total, erros: data.erros.length },
      });
    }
  })().catch(async (e) => {
    await setState({ running: false, error: String(e.message || e) });
    try { sendResponse({ ok: false, error: String(e.message || e) }); } catch (_) {}
  });
  return true;
});
