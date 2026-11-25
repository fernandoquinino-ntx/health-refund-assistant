// Mundo isolado: repassa mensagens do coletor (mundo MAIN da página) para o service worker.
window.addEventListener("message", (ev) => {
  if (ev.source !== window) return;
  const msg = ev.data;
  if (!msg || msg.source !== "cp-collector") return;
  chrome.runtime.sendMessage({ type: "cp-" + msg.kind, payload: msg.payload }).catch(() => {});
});
