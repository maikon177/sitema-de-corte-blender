// ============================================================
// API — ponte do app com o servidor (instagram-poster/api.py)
// Mesma origem quando servido pela API Flask. Fase 1: calendário + upload.
// ============================================================
const API = {
  base: "", // mesma origem (a API serve o app)
  _token: null,
  _headers() {
    const h = {};
    if (this._token) h["X-API-Token"] = this._token;
    return h;
  },
  async contas() {
    const r = await fetch(`${this.base}/api/contas`, { headers: this._headers() });
    if (!r.ok) throw new Error("contas");
    return r.json();
  },
  async calendario(de, ate) {
    const qs = new URLSearchParams();
    if (de) qs.set("de", de);
    if (ate) qs.set("ate", ate);
    const r = await fetch(`${this.base}/api/calendario?${qs}`, { headers: this._headers() });
    if (!r.ok) throw new Error("calendario");
    return r.json();
  },
  async cancelar(id) {
    const r = await fetch(`${this.base}/api/calendario/${id}/cancelar`, {
      method: "POST",
      headers: this._headers(),
    });
    if (!r.ok) throw new Error("cancelar");
    return r.json();
  },
  async notificacoes() {
    const r = await fetch(`${this.base}/api/notificacoes`, { headers: this._headers() });
    if (!r.ok) throw new Error("notificacoes");
    return r.json();
  },
  async biblioteca() {
    const r = await fetch(`${this.base}/api/biblioteca`, { headers: this._headers() });
    if (!r.ok) throw new Error("biblioteca");
    return r.json();
  },
  async mover(de, para, arquivo) {
    const r = await fetch(`${this.base}/api/conteudo/mover`, {
      method: "POST",
      headers: Object.assign({ "Content-Type": "application/json" }, this._headers()),
      body: JSON.stringify({ de, para, arquivo }),
    });
    if (!r.ok) throw new Error("mover");
    return r.json();
  },
  async instagramPosts(conta, limite) {
    const qs = limite ? `?limite=${limite}` : "";
    const r = await fetch(`${this.base}/api/instagram/${conta}${qs}`, { headers: this._headers() });
    if (!r.ok) throw new Error("instagram");
    return r.json();
  },
  async config() {
    const r = await fetch(`${this.base}/api/config`, { headers: this._headers() });
    if (!r.ok) throw new Error("config");
    return r.json();
  },
  async salvarConfig(body) {
    const r = await fetch(`${this.base}/api/config`, {
      method: "POST",
      headers: Object.assign({ "Content-Type": "application/json" }, this._headers()),
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error("salvarConfig");
    return r.json();
  },
  async historico(atualizar) {
    const qs = atualizar ? "?atualizar=1" : "";
    const r = await fetch(`${this.base}/api/historico${qs}`, { headers: this._headers() });
    if (!r.ok) throw new Error("historico");
    return r.json();
  },
  async novaLegenda(id) {
    const r = await fetch(`${this.base}/api/calendario/${id}/legenda`, {
      method: "POST",
      headers: this._headers(),
    });
    if (!r.ok) throw new Error("legenda");
    return r.json();
  },
  async upload(conta, arquivos) {
    const fd = new FormData();
    [...arquivos].forEach((f) => fd.append("fotos", f));
    const r = await fetch(`${this.base}/api/upload/${conta}`, {
      method: "POST",
      headers: this._headers(),
      body: fd,
    });
    if (!r.ok) throw new Error("upload");
    return r.json();
  },
};
