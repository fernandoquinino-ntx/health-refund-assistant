const FIELDS = ["mode", "dtIni", "dtFim", "chunkMonths", "delayMin", "delayMax", "maxItems", "useLM", "lmUrl", "lmModel", "lmPrompt"];
const $ = (id) => document.getElementById(id);
const statusEl = $("status");

function readCfg() {
  const cfg = {};
  for (const f of FIELDS) {
    const el = $(f);
    cfg[f] = el.type === "checkbox" ? el.checked : el.type === "number" ? Number(el.value) : el.value.trim();
  }
  return cfg;
}

function render(state) {
  if (!state) return;
  statusEl.classList.toggle("err", !!state.error);
  statusEl.textContent = state.error ? "Erro: " + state.error : state.text || (state.running ? "Coletando…" : "Pronto.");
  $("start").disabled = !!state.running;
}

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

(async () => {
  const { cpCfg, cpState } = await chrome.storage.local.get(["cpCfg", "cpState"]);
  if (cpCfg) for (const f of FIELDS) {
    if (cpCfg[f] === undefined) continue;
    const el = $(f);
    if (el.type === "checkbox") el.checked = cpCfg[f]; else el.value = cpCfg[f];
  }
  render(cpState);
})();

chrome.storage.onChanged.addListener((ch) => { if (ch.cpState) render(ch.cpState.newValue); });

$("start").addEventListener("click", async () => {
  const tab = await activeTab();
  const cfg = readCfg();
  if ((cfg.dtIni && !cfg.dtFim) || (!cfg.dtIni && cfg.dtFim)) {
    render({ error: "Preencha as duas datas ou deixe ambas em branco." });
    return;
  }
  render({ running: true, text: "Abrindo Consultar Reembolsos…" });
  const res = await chrome.runtime.sendMessage({ type: "start", tabId: tab && tab.id, cfg });
  if (res && !res.ok) render({ error: res.error });
});

$("stop").addEventListener("click", async () => {
  const tab = await activeTab();
  if (tab) chrome.runtime.sendMessage({ type: "stop", tabId: tab.id });
});
