// Roda no mundo MAIN da página consultaReembolso.aspx (acesso a jQuery, DataTables e passo1/2/3 do portal).
(() => {
  if (window.__cpCollector) return;

  const $ = window.jQuery;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const post = (kind, payload) => window.postMessage({ source: "cp-collector", kind, payload }, "*");

  let stopFlag = false;
  let overlay;

  // ---------- UI de progresso na página ----------
  function ui(text) {
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.style.cssText =
        "position:fixed;right:16px;bottom:16px;z-index:2147483647;background:#0b3d6e;color:#fff;" +
        "font:13px/1.4 system-ui,sans-serif;padding:12px 14px;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,.3);max-width:340px";
      document.body.appendChild(overlay);
    }
    overlay.textContent = "Coletor de Reembolsos — " + text;
  }

  // ---------- helpers ----------
  const visible = (sel) => {
    const el = document.querySelector(sel);
    return !!el && getComputedStyle(el).display !== "none";
  };

  async function waitFor(pred, timeout = 25000, step = 200) {
    const t0 = Date.now();
    while (Date.now() - t0 < timeout) {
      if (stopFlag) throw new Error("Interrompido pelo usuário");
      try { if (pred()) return true; } catch (_) {}
      await sleep(step);
    }
    throw new Error("Tempo esgotado aguardando o portal");
  }

  const idle = () => !visible("#cobreTela");

  async function pause(cfg) {
    const min = Math.max(0, Number(cfg.delayMin) || 1500);
    const max = Math.max(min, Number(cfg.delayMax) || 3000);
    await sleep(min + Math.random() * (max - min));
  }

  const toBR = (iso) => { const [y, m, d] = iso.split("-"); return `${d}/${m}/${y}`; };
  const fromISO = (iso) => { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); };
  const toISO = (dt) => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
  const normalizeDate = (value) => {
    const text = String(value || "").trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
    const match = text.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    return match ? `${match[3]}-${match[2]}-${match[1]}` : null;
  };

  function readScreenPeriod() {
    const inicio = normalizeDate($("#body_content_txtDtInicial").val());
    const fim = normalizeDate($("#body_content_txtDtFinal").val());
    return inicio && fim ? { de: toBR(inicio), ate: toBR(fim) } : null;
  }

  function splitWindows(ini, fim, months) {
    const out = [];
    let a = fromISO(ini);
    const end = fromISO(fim);
    while (a <= end) {
      let b = new Date(a.getFullYear(), a.getMonth() + months, a.getDate() - 1);
      if (b > end) b = end;
      out.push([toBR(toISO(a)), toBR(toISO(b))]);
      a = new Date(b.getFullYear(), b.getMonth(), b.getDate() + 1);
    }
    return out;
  }

  const parseMoney = (s) => {
    if (!s) return null;
    const m = String(s).replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
    const n = parseFloat(m);
    return isNaN(n) ? null : n;
  };

  const cellTexts = (tr) => [...tr.cells].map((td) => td.innerText.trim());
  const passoOf = (tr) => ((tr.getAttribute("onclick") || "").match(/passo(\d)/) || [])[1];

  // ---------- passo 1: listagem ----------
  // Lê as pessoas da lista "Selecione abaixo o nome do beneficiário" (#lstBeneficiarios).
  function readPeople() {
    return [...document.querySelectorAll("#lstBeneficiarios a")]
      .map((a) => {
        const m = (a.getAttribute("onclick") || a.getAttribute("href") || "").match(/passo1\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*"([^"]*)"/);
        return m ? { codsub: m[1].trim(), codseg: m[2].trim(), seq: m[3].trim(), nome: m[4], rotulo: a.innerText.trim() } : null;
      })
      .filter(Boolean);
  }

  // person = null -> grupo familiar inteiro (seq 99)
  async function loadList(person, win) {
    if (win) {
      $("#body_content_txtDtInicial").val(win[0]);
      $("#body_content_txtDtFinal").val(win[1]);
    }
    $("#divDadosPasso1").empty();
    if (person) window.passo1(person.codsub, person.codseg, person.seq, person.nome, true, "0", false);
    else window.passo1($("#body_content_hdfCodSub").val(), $("#body_content_hdfCodSeg").val(), 99, "", true, "0", false);
    await waitFor(() => idle() && document.querySelector("#divDadosPasso1").innerHTML.trim().length > 0);
    await sleep(300);
    const tbl = document.querySelector("#tblAut1");
    if (!tbl) return [];
    const nodes = $.fn.dataTable.isDataTable(tbl) ? $(tbl).DataTable().rows().nodes().toArray() : [...tbl.querySelectorAll("tbody tr")];
    return nodes.filter((tr) => passoOf(tr));
  }

  // ---------- passo 2: sub-itens ----------
  async function loadSubItems(tr) {
    $("#divDadosPasso2").empty();
    tr.click();
    await waitFor(() => idle() && document.querySelector("#tblAut2"));
    await sleep(300);
    const tbl = document.querySelector("#tblAut2");
    const nodes = $.fn.dataTable.isDataTable(tbl) ? $(tbl).DataTable().rows().nodes().toArray() : [...tbl.querySelectorAll("tbody tr")];
    return nodes.filter((n) => passoOf(n));
  }

  // ---------- passo 3: detalhe ----------
  const KEYMAP = {
    "Número do Sinistro": "numeroSinistro",
    "Nome do(a) Beneficiário(a)": "beneficiario",
    "Status da Solicitação": "status",
    "Prestador/Profissional Solicitante": "prestador",
    "Cobertura": "cobertura",
    "Data da Solicitação do Reembolso": "dataSolicitacao",
    "Data da Realização do Procedimento": "dataRealizacao",
    "Data de Pagamento do Reembolso": "dataPagamento",
    "Origem do Documento Enviado": "origemDocumento",
    "Valor Solicitado pelo(a) Beneficiário(a)": "valorSolicitado",
    "Valor de Coparticipação Aplicada": "valorCoparticipacao",
    "Valor Final Reembolsado": "valorFinalReembolsado",
    "Descrição": "descricao",
    "Forma de Pagamento do Reembolso": "formaPagamento",
    "Procedimento Realizado": "procedimento",
    "Informação Adicional": "informacaoAdicional",
  };
  const SKIP = /^(Dúvida sobre esse Reembolso|Data atual|Beneficiário)$/;

  function parseDetail() {
    const root = document.querySelector("#divDadosPasso3");
    const campos = {};
    root.querySelectorAll(".row").forEach((row) => {
      const cols = [...row.children].filter((c) => c.tagName === "DIV");
      if (cols.length < 2) return;
      const label = cols[0].innerText.trim().replace(/\s*\*?\s*:?\s*$/, "").replace(/\s*\*$/, "").trim();
      const value = cols[1].innerText.trim();
      if (!label || SKIP.test(label)) return;
      if (label in campos) {
        campos[label] = [].concat(campos[label], value);
      } else campos[label] = value;
    });
    const r = {};
    for (const [label, val] of Object.entries(campos)) {
      const key = KEYMAP[label];
      if (key) r[key] = val;
    }
    for (const k of ["valorSolicitado", "valorCoparticipacao", "valorFinalReembolsado"]) {
      if (r[k] != null) r[k + "Num"] = parseMoney(Array.isArray(r[k]) ? r[k][0] : r[k]);
    }
    r.camposBrutos = campos;
    return r;
  }

  async function openDetail(tr) {
    $("#divDadosPasso3").empty();
    tr.click();
    await waitFor(() => idle() && /Número do Sinistro/.test(document.querySelector("#divDadosPasso3").innerText));
    await sleep(200);
    return parseDetail();
  }

  async function withRetry(fn, tries = 2) {
    let err;
    for (let i = 0; i < tries; i++) {
      try { return await fn(); } catch (e) {
        err = e;
        if (stopFlag) throw e;
        await sleep(2500);
      }
    }
    throw err;
  }

  // ---------- orquestração ----------
  async function start(cfg) {
    stopFlag = false;
    try {
      await waitFor(() => $ && typeof window.passo1 === "function" && document.querySelector("#divReembolsoBeneficiario, #lstBeneficiarios"), 20000);
    } catch (_) {
      post("error", { message: "Tela Consultar Reembolsos não carregou (verifique se está logado)." });
      return;
    }
    const startedAt = new Date().toISOString();
    const windows = cfg.dtIni && cfg.dtFim ? splitWindows(cfg.dtIni, cfg.dtFim, Number(cfg.chunkMonths) || 6) : [null];
    const period = cfg.dtIni && cfg.dtFim
      ? { de: toBR(cfg.dtIni), ate: toBR(cfg.dtFim) }
      : readScreenPeriod();
    const found = readPeople();
    // modo "pessoa": uma consulta por beneficiário; modo "grupo" (ou sem lista): grupo familiar inteiro
    const people = cfg.mode === "grupo" || !found.length ? [null] : found;
    const results = [];
    const errors = [];
    const seen = new Set();
    const porPessoa = {};
    let done = 0;

    try {
      for (const [pi, person] of people.entries()) {
        const pessoa = person ? person.nome : "Grupo familiar";
        let donePessoa = 0;
        porPessoa[pessoa] = 0;

        for (const [wi, win] of windows.entries()) {
          if (cfg.maxItems && donePessoa >= cfg.maxItems) break;
          const label = win ? `${win[0]} a ${win[1]}` : "período atual da tela";
          ui(`${pessoa} (${pi + 1}/${people.length}) — carregando lista (${label})…`);
          post("progress", { done, text: `${pessoa} (${pi + 1}/${people.length}) · janela ${wi + 1}/${windows.length}` });

          const rows = await withRetry(() => loadList(person, win));
          await pause(cfg);

          for (const [ri, tr] of rows.entries()) {
            if (stopFlag) throw new Error("Interrompido pelo usuário");
            if (cfg.maxItems && donePessoa >= cfg.maxItems) break;
            const c = cellTexts(tr);
            const lista = { beneficiario: c[0], cobertura: c[2], dataProtocolo: c[3], valorTotalSolicitado: c[4] };
            const tick = () => {
              done++; donePessoa++;
              ui(`${pessoa} (${pi + 1}/${people.length}) — ${donePessoa} detalhes (linha ${ri + 1}/${rows.length}) · total ${done}`);
              post("progress", { done, text: `${pessoa}: ${donePessoa} · total ${done}` });
            };

            try {
              const items = [];
              if (passoOf(tr) === "2") {
                const subs = await withRetry(() => loadSubItems(tr));
                await pause(cfg);
                for (const sub of subs) {
                  if (stopFlag) throw new Error("Interrompido pelo usuário");
                  if (cfg.maxItems && donePessoa >= cfg.maxItems) break;
                  const sc = cellTexts(sub);
                  const det = await withRetry(() => openDetail(sub));
                  items.push({ ...det, itemLista: { prestador: sc[1], dataEvento: sc[2], valorSolicitado: sc[3], status: sc[4] } });
                  tick();
                  await pause(cfg);
                }
              } else {
                items.push(await withRetry(() => openDetail(tr)));
                tick();
                await pause(cfg);
              }
              for (const it of items) {
                const key = [it.numeroSinistro, it.dataRealizacao, it.valorSolicitado, it.procedimento || it.descricao].join("|");
                if (seen.has(key)) continue;
                seen.add(key);
                porPessoa[pessoa]++;
                results.push({ pessoaConsultada: pessoa, ...it, linhaLista: lista, janela: win ? { de: win[0], ate: win[1] } : null });
              }
            } catch (e) {
              if (stopFlag) throw e;
              errors.push({ pessoa, linha: ri + 1, janela: label, lista, erro: String(e.message || e) });
            }
          }
        }
      }
    } catch (e) {
      errors.push({ erro: String(e.message || e) });
    }

    // volta a tela para a listagem
    try { if (typeof window.voltar === "function") window.voltar(1); } catch (_) {}

    const payload = {
      fonte: location.origin + location.pathname,
      coletadoEm: new Date().toISOString(),
      iniciadoEm: startedAt,
      periodo: period,
      total: results.length,
      totalPorPessoa: porPessoa,
      pessoas: people.map((p) => (p ? p.rotulo : "Grupo familiar")),
      reembolsos: results,
      erros: errors,
    };
    ui(`concluído: ${results.length} reembolsos${errors.length ? `, ${errors.length} erro(s)` : ""}.`);
    setTimeout(() => { if (overlay) { overlay.remove(); overlay = null; } }, 8000);
    post("done", payload);
  }

  window.__cpCollector = {
    start: (cfg) => { start(cfg || {}); return true; },
    stop: () => { stopFlag = true; return true; },
  };
})();
