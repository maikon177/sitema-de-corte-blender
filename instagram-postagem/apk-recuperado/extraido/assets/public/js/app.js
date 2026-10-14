// ============================================================
// Pata3D Studio — app completo
// Telas: Início · Grade (canais) · Esteira · Calendário · Criar · Analytics · Contas · Detalhe
// ============================================================

const content = document.getElementById("content");

const LBL_FMT = { feed: "FEED", story: "STORY", reel: "REEL", carrossel: "CARROSSEL", x: "POST" };

// ---------- ícones SVG (nada de emoji) ----------
const IC = {
  clock: `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>`,
  grid: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>`,
  layers: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/></svg>`,
  cal: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/></svg>`,
  bolt: `<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M13 2L4.5 13.5H11l-1 8.5L19.5 10H13l0-8z"/></svg>`,
  back: `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>`,
  check: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>`,
  edit: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>`,
  send: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>`,
  robot: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V5M9 13h.01M15 13h.01"/><circle cx="12" cy="4" r="1.3"/></svg>`,
  sparkles: `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2l1.8 4.9L19 8.7l-4.9 1.8L12 15.4l-1.8-4.9L5 8.7l5.2-1.8L12 2z"/></svg>`,
  upload: `<svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/></svg>`,
  folder: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/></svg>`,
  video: `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`,
  rocket: `<svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="#c4b5fd" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 15c-1 1-1.5 3.5-1.5 5.5 2 0 4.5-.5 5.5-1.5"/><path d="M9 11a9 9 0 0 1 9-9c1 0 2 .2 2 .2s.2 1 .2 2a9 9 0 0 1-9 9l-2.2.5L8.5 13 9 11z"/><circle cx="14.5" cy="7.5" r="1.4" fill="#c4b5fd"/></svg>`,
};

// ---------- util ----------
function el(html) { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; }
function conta(id) { return contaPorId(id); }
function dotC(id) { const c = conta(id); return `<span class="dot" style="background:${c ? c.cor : "#888"}"></span>`; }
function nomeCurto(id) { const c = conta(id); return c ? c.nome.replace("Pata3D ", "").replace("no X", "X") : id; }
function pawSVG(s) { return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="#fff"><circle cx="7" cy="8" r="2.1"/><circle cx="12" cy="6" r="2.2"/><circle cx="17" cy="8" r="2.1"/><ellipse cx="12" cy="15.5" rx="4.6" ry="3.8"/></svg>`; }

function sparkline(data, color) {
  const w = 96, h = 30, max = Math.max(...data), min = Math.min(...data), rng = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / rng) * (h - 4) - 2}`).join(" ");
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" fill="none"><polyline points="${pts}" stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}
function donut(pct, color, track) {
  const r = 46, c = 2 * Math.PI * r, on = (pct / 100) * c;
  return `<svg width="110" height="110" viewBox="0 0 110 110"><circle cx="55" cy="55" r="${r}" stroke="${track}" stroke-width="12" fill="none"/><circle cx="55" cy="55" r="${r}" stroke="${color}" stroke-width="12" fill="none" stroke-linecap="round" stroke-dasharray="${on} ${c}" transform="rotate(-90 55 55)"/></svg>`;
}

// ============================================================
// INÍCIO (central de comando + atalhos)
// ============================================================
function renderInicio() {
  const r = DB.resumoHoje;
  let h = "";
  h += `<div class="status-card">
          <span class="rocket">${IC.rocket}</span>
          <div class="sc-top"><span class="dot" style="background:var(--ok)"></span> STATUS GERAL</div>
          <div class="sc-big">Tudo rodando</div>
          <div class="muted" style="margin-top:2px"><b style="color:var(--text);font-size:15px">${r.postsHoje}</b> posts hoje</div>
          <div class="sc-stats">
            <div class="sc-stat"><div class="l">Contas</div><div class="v">${r.contasAtivas}/5</div></div>
            <div class="sc-stat"><div class="l">Filas ativas</div><div class="v">3</div></div>
            <div class="sc-stat"><div class="l">Atualizado</div><div class="v">Agora</div></div>
          </div>
        </div>`;

  // atalhos para as visões extras
  h += `<div class="quick">
          <button class="quick-b" onclick="irPara('grade')">${IC.grid}<span>Grade</span></button>
          <button class="quick-b" onclick="irPara('esteira')">${IC.layers}<span>Esteira</span></button>
          <button class="quick-b" onclick="irPara('calendario')">${IC.cal}<span>Calendário</span></button>
          <button class="quick-b" onclick="irPara('conteudo')">${IC.folder}<span>Conteúdo</span></button>
        </div>`;

  h += `<div class="section-head"><h3>Próximos posts</h3><a onclick="irPara('calendario')">Ver todos</a></div>`;
  DB.proximos.slice(0, 3).forEach((p) => {
    const pill = p.status === "pronto" || p.status === "publicado" ? `<span class="pill pronto">Pronto</span>` : `<span class="pill aprovar">Aprovar</span>`;
    h += `<div class="mini-card" onclick="abrirDetalhe('${p.img}','${p.titulo}','${p.contaId}','${p.hora}','inicio')">
            <div class="mini-img" style="background-image:url('${p.img || ""}')"><span class="pc-fmt">${LBL_FMT[p.formato]}</span></div>
            <div class="mini-body"><div class="mb-main"><div class="mb-t">${p.titulo}</div><div class="mb-s">${nomeCurto(p.contaId)} · ${p.hora}</div></div>${pill}</div>
          </div>`;
  });
  content.innerHTML = h;
}

// ============================================================
// GRADE DE CANAIS (contas x dias)
// ============================================================
function renderGrade() {
  const g = DB.grade;
  let h = `<div class="view-title">Grade da semana</div><div class="view-sub">Cada linha é uma conta, como um canal de TV</div>`;
  h += `<div class="grade-scroll"><div class="grade" style="grid-template-columns:150px repeat(${g.dias.length},150px)">`;
  h += `<div></div>` + g.dias.map((d) => `<div class="g-day">${d}</div>`).join("");
  g.canais.forEach((c) => {
    h += `<div class="g-chan">
            <div class="g-av" style="background:${c.cor}">${pawSVG(26)}</div>
            <div class="g-ci"><div class="g-nm">${c.nome}</div><div class="g-plat">${c.plataforma}</div></div>
          </div>`;
    c.posts.forEach((p) => {
      if (!p.img) { h += `<div class="g-cell empty"><span>—</span></div>`; return; }
      h += `<div class="g-cell" style="background-image:url('${p.img}')" onclick="abrirDetalhe('${p.img}','${p.t}','${c.nome}','${p.hora}','grade')">
              <div class="g-ov"><div class="g-k" style="color:${c.cor}">${p.k}</div><div class="g-t">${p.t}</div></div>
              <div class="g-time">${IC.clock} ${p.hora}</div>
            </div>`;
    });
  });
  h += `</div></div>`;
  h += `<p class="muted" style="margin-top:12px">Arraste para o lado para ver todos os dias.</p>`;
  content.innerHTML = h;
}

// ============================================================
// ESTEIRA (kanban: 5 etapas cortadas)
// ============================================================
function renderEsteira() {
  let h = `<div class="view-title">Esteira de produção</div><div class="view-sub">Acompanhe o fluxo dos posts, do início à publicação</div>`;
  h += `<div class="kanban-scroll"><div class="kanban">`;
  DB.esteira.etapas.forEach((et) => {
    h += `<div class="k-col"><div class="k-head"><span class="dot" style="background:${et.cor}"></span> ${et.nome} <span class="k-count">${et.cards.length}</span></div><div class="k-cards">`;
    et.cards.forEach((c) => {
      const cor = conta(c.contaId).cor;
      h += `<div class="k-card" style="background-image:url('${c.img}')" onclick="abrirDetalhe('${c.img}','${c.titulo}','${c.contaId}','${c.hora}','esteira')">
              <div class="k-ov"><div class="k-title">${c.titulo}</div></div>
              <div class="k-foot"><span class="k-pawav" style="background:${cor}">${pawSVG(14)}</span><div class="k-fi"><div class="k-h">${c.handle}</div><div class="k-t">${IC.clock} ${c.hora}</div></div></div>
            </div>`;
    });
    h += `</div></div>`;
  });
  h += `</div></div>`;
  h += `<p class="muted" style="margin-top:12px;text-align:center">Toque num card para abrir e mover de etapa.</p>`;
  content.innerHTML = h;
}

// ============================================================
// DETALHE DO POST
// ============================================================
let detalheVoltar = "inicio";
function abrirDetalhe(img, titulo, contaId, hora, voltar) {
  detalheVoltar = voltar || "inicio";
  const c = conta(contaId);
  const nome = c ? c.nome : contaId;
  let h = `<div class="det-top"><button class="det-back" onclick="irPara('${detalheVoltar}')">${IC.back}</button><div class="det-ttl">Detalhe do post</div><div style="width:40px"></div></div>`;
  h += `<div class="det-img" style="background-image:url('${img}')"><div class="det-img-ov"><div class="det-img-t">${titulo}</div></div></div>`;
  h += `<div class="field-label">Etapa atual</div><select><option>Ideia</option><option>IA gerou</option><option>Aprovar</option><option>Agendado</option><option>Publicado</option></select>`;
  h += `<div class="field-label">Mover para</div><div class="mover">
          <button class="mv" onclick="toast('Movido: IA gerou')">${IC.robot}<span>IA gerou</span></button>
          <button class="mv" onclick="toast('Movido: Aprovar')">${IC.check}<span>Aprovar</span></button>
          <button class="mv" onclick="toast('Movido: Agendado')">${IC.cal}<span>Agendado</span></button>
          <button class="mv" onclick="toast('Movido: Publicado')">${IC.send}<span>Publicado</span></button>
        </div>`;
  h += `<div class="card" style="margin-top:14px"><div class="field-label" style="margin-top:0">Prévia da legenda</div>
          <div class="muted" style="color:var(--text);font-size:14px;line-height:1.5">${titulo} 🐾 feito em impressão 3D. Personalize o seu! #pata3d #impressao3d</div></div>`;
  h += `<div class="card" style="margin-top:12px;display:flex;align-items:center;gap:12px">${IC.cal}<div style="flex:1"><div style="font-weight:600">Agendar publicação</div><div class="muted">Escolha data e horário</div></div><span style="color:var(--text-2)">›</span></div>`;
  h += `<button class="btn grad block" style="margin-top:16px" onclick="toast('Post movido ✓')">Mover para a próxima etapa →</button>`;
  content.innerHTML = h;
  content.scrollTop = 0; window.scrollTo(0, 0);
}

// ============================================================
// CALENDÁRIO
// ============================================================
let diaSel = 2;
function renderCalendario() {
  const sem = DB.catalogoSemana;
  let h = `<div class="view-title">Calendário</div><div class="view-sub">Semana ${sem.semana}</div>`;
  h += `<div class="day-strip">`;
  sem.dias.forEach((d, i) => {
    const cor = d.posts.length ? conta(d.posts[0].contaId).cor : "var(--text-3)";
    h += `<div class="day-pick ${i === diaSel ? "on" : ""}" onclick="diaSel=${i};renderCalendario()"><div class="dp-d">${d.nome}</div><div class="dp-n">${d.data}</div><div class="dp-dot" style="background:${cor}"></div></div>`;
  });
  h += `</div>`;
  h += `<div class="week-strip">`;
  sem.dias.forEach((d) => { const p = d.posts[0]; if (!p) return; h += `<div class="ws-item"><div class="ws-thumb" style="background-image:url('${p.img}')"><span class="ws-time">${dotC(p.contaId)} ${p.hora}</span></div><div class="ws-day">${d.nome} ${d.data}</div></div>`; });
  h += `</div>`;
  const dia = sem.dias[diaSel];
  h += `<div class="day-label">${dia.nome}, ${dia.data} de outubro</div>`;
  dia.posts.forEach((p) => {
    const isReel = p.formato === "reel";
    const prim = p.status === "pronto" ? "✓ Pronto" : "✓ Aprovar";
    h += `<div class="post-card">
            <div class="pc-img" style="background-image:url('${p.img || ""}')"><span class="pc-time-ov">${dotC(p.contaId)} ${p.hora}</span></div>
            <div class="pc-body"><div class="pc-title">${p.titulo}</div><div class="pc-acct">${dotC(p.contaId)} ${nomeCurto(p.contaId)} · ${LBL_FMT[p.formato]}</div>
            <div class="pc-actions"><button class="btn grad flex small" onclick="toast('${prim}')">${prim}</button><button class="btn flex small" onclick="abrirDetalhe('${p.img}','${p.titulo}','${p.contaId}','${p.hora}','calendario')">${IC.edit} Editar</button></div></div>
          </div>`;
  });
  content.innerHTML = h;
}

// ============================================================
// CRIAR (estúdio IA)
// ============================================================
let criarConta = "cortadores", criarOpt = 0, alvoIG = true, alvoX = false;
function renderCriar() {
  const estilos = DB.estilosIA[criarConta] || [];
  let h = `<div class="view-title">Criar com IA</div><div class="view-sub">Envie, gere e publique</div>`;
  h += `<div class="dropzone">${IC.upload}<div style="margin-top:8px">Arraste ou toque para enviar foto/vídeo</div></div>`;
  h += `<label class="field-label">Conta</label><select onchange="criarConta=this.value;renderCriar()">`;
  DB.contas.forEach((c) => (h += `<option value="${c.id}" ${c.id === criarConta ? "selected" : ""}>${c.nome}</option>`));
  h += `</select>`;
  h += `<label class="field-label">Estilo da IA</label><select>` + estilos.map((s) => `<option>${s}</option>`).join("") + `</select>`;
  h += `<button class="btn grad block" style="margin-top:14px" onclick="toast('Gerando 3 opções…')">${IC.sparkles} Gerar imagem com IA</button>`;
  h += `<label class="field-label">Escolha uma opção (IA gerou 3)</label><div class="options-3">`;
  ["img/p1.jpg", "img/p2.jpg", "img/p7.jpg"].forEach((src, i) => (h += `<div class="opt ${i === criarOpt ? "sel" : ""}" style="background-image:url('${src}')" onclick="criarOpt=${i};renderCriar()"></div>`));
  h += `</div>`;
  h += `<label class="field-label">Legenda gerada por IA</label><textarea>Cortador de biscoito em formato de coração 🐾 feito em impressão 3D. Personalize o seu! #pata3d #cortadores #confeitaria</textarea>`;
  h += `<label class="field-label">Postar em</label><div class="targets"><div class="target ${alvoIG ? "on" : ""}" onclick="alvoIG=!alvoIG;renderCriar()">Instagram</div><div class="target ${alvoX ? "on" : ""}" onclick="alvoX=!alvoX;renderCriar()">X (Twitter)</div></div>`;
  h += `<div style="display:flex;gap:10px;margin-top:16px"><button class="btn flex" onclick="toast('Agendado!')">Agendar</button><button class="btn grad flex" onclick="toast('Postado agora!')">Postar agora</button></div>`;
  content.innerHTML = h;
}

// ============================================================
// ANALYTICS
// ============================================================
function renderAnalytics() {
  const dz = DB.desempenho;
  let h = `<div class="view-title">Analytics</div><div class="view-sub">Visão geral do desempenho</div>`;
  h += `<div class="card"><div class="cap">DESEMPENHO HOJE</div><div class="kpis" style="margin-top:14px">
          <div class="kpi"><div class="k-lab">Impressões</div><div class="k-val">128,7K</div><div class="k-up">↑ 18,4%</div>${sparkline([5,8,6,10,9,14,18], "#a78bfa")}</div>
          <div class="kpi"><div class="k-lab">Engajamento</div><div class="k-val">8,92K</div><div class="k-up">↑ 22,7%</div>${sparkline([4,5,7,6,9,11,13], "#a78bfa")}</div>
          <div class="kpi"><div class="k-lab">Cliques</div><div class="k-val">1,36K</div><div class="k-up">↑ 15,3%</div>${sparkline([3,4,4,6,5,8,9], "#a78bfa")}</div>
        </div></div>`;
  h += `<div class="card"><div class="cap">DISTRIBUIÇÃO POR PLATAFORMA</div><div class="donut-wrap" style="margin-top:12px">
          <div class="donut">${donut(58, "#8b5cf6", "#2a2a3a")}<div class="d-center"><div class="d-num">12</div><div class="d-lab">Posts</div></div></div>
          <div class="legend"><div class="legend-row"><span class="dot" style="background:#8b5cf6"></span><span class="lr-main">Instagram</span><span class="lr-val">7</span><span class="lr-pct">58%</span></div>
          <div class="legend-row"><span class="dot" style="background:#6a6a7a"></span><span class="lr-main">X (Twitter)</span><span class="lr-val">5</span><span class="lr-pct">42%</span></div></div>
        </div></div>`;
  h += `<div class="card"><div class="section-head" style="margin:0 0 6px"><h3>Últimos posts publicados</h3></div>`;
  dz.melhores.forEach((m) => { h += `<div class="pub-row"><div class="pub-thumb" style="background-image:url('${m.img}')"></div><div class="pub-main"><div class="pub-t">${m.titulo}</div><div class="pub-s">${nomeCurto(m.contaId)} · ${(m.alcance / 1000).toFixed(1)}k alcance</div></div><span class="pill publicado">✓ Publicado</span></div>`; });
  h += `</div><button class="btn grad block" style="margin-top:16px" onclick="irPara('criar')">＋ Criar novo post</button>`;
  content.innerHTML = h;
}

// ============================================================
// CONTEÚDO (galeria + gerenciador de pastas)
// ============================================================
function renderConteudo() {
  const b = DB.biblioteca;
  let h = `<div class="view-title">Conteúdo</div><div class="view-sub">Despeje tudo aqui e organize por pasta</div>`;
  h += `<div class="dropzone" onclick="toast('Selecionar arquivos…')">${IC.upload}<div style="margin-top:8px">Despejar fotos e vídeos aqui</div><div class="muted" style="margin-top:4px">depois arraste pra pasta certa</div></div>`;
  h += `<div class="section-head"><h3>Pastas</h3><span class="muted">${b.pastas.length}</span></div>`;
  h += `<div class="folders">`;
  b.pastas.forEach((p) => {
    const capa = p.itens[0] ? p.itens[0].img : "";
    h += `<div class="folder" onclick="abrirPasta('${p.id}')">
            <div class="folder-cover" style="background-image:url('${capa}')"><span class="folder-count">${p.itens.length}</span></div>
            <div class="folder-name"><span class="dot" style="background:${p.cor}"></span> ${p.nome}</div>
          </div>`;
  });
  h += `</div>`;
  content.innerHTML = h;
}

function abrirPasta(id) {
  const p = DB.biblioteca.pastas.find((x) => x.id === id);
  let h = `<div class="det-top"><button class="det-back" onclick="irPara('conteudo')">${IC.back}</button><div class="det-ttl">${p.nome}</div><div style="width:40px"></div></div>`;
  h += `<div class="muted" style="margin:-6px 0 14px">${p.itens.length} itens · toque e segure pra mover</div>`;
  h += `<div class="gallery">`;
  p.itens.forEach((it) => {
    h += `<div class="gi" style="background-image:url('${it.img}')" onclick="toast('Abrir item')">${it.tipo === "video" ? `<span class="gi-badge">${IC.video}</span>` : ""}</div>`;
  });
  // botão adicionar
  h += `<div class="gi gi-add" onclick="toast('Adicionar à pasta')">+</div>`;
  h += `</div>`;
  h += `<button class="btn grad block" style="margin-top:18px" onclick="toast('Enviar da Entrada pra ${p.nome}')">Enviar conteúdo da Entrada pra cá</button>`;
  content.innerHTML = h;
  content.scrollTop = 0; window.scrollTo(0, 0);
}

// ============================================================
// CONTAS
// ============================================================
function renderContas() {
  let h = `<div class="view-title">Contas</div><div class="view-sub">Automático, tokens e regras</div><div class="card">`;
  DB.contas.forEach((c, i) => {
    const t = c.token;
    const cor = t.estado === "morto" ? "var(--danger)" : t.estado === "expirando" ? "var(--warn)" : "var(--ok)";
    const txt = t.estado === "morto" ? "Token morto" : t.estado === "expirando" ? `Vence em ${t.diasRestantes}d` : `Token ok (${t.diasRestantes}d)`;
    const inicial = c.rede === "x" ? "X" : c.nome.charAt(7).toUpperCase();
    h += `<div class="conta-row"><div class="conta-av" style="background:${c.cor}">${inicial}</div><div class="conta-main"><div class="conta-t">${c.nome}</div><div class="conta-s" style="color:${cor}">● ${txt} · ${c.tema}</div></div><div class="switch ${c.automatico ? "on" : ""}" onclick="toggleAuto(${i}, this)"></div></div>`;
  });
  h += `</div><div class="section-head"><h3>Regras de postagem</h3></div><div class="card">
          <div class="rule-row"><div class="rule-main"><div class="rule-t">Ritmo humano</div><div class="rule-s">Máx. 2 posts/dia por conta</div></div><span class="pill publicado">Ativo</span></div>
          <div class="rule-row"><div class="rule-main"><div class="rule-t">Bloqueio de repetição</div><div class="rule-s">Não posta foto repetida</div></div><span class="pill publicado">Ativo</span></div>
          <div class="rule-row"><div class="rule-main"><div class="rule-t">Alerta de estoque</div><div class="rule-s">Avisa com 7 dias de antecedência</div></div><span class="pill publicado">Ativo</span></div>
        </div>`;
  content.innerHTML = h;
}
function toggleAuto(i, elm) { DB.contas[i].automatico = !DB.contas[i].automatico; elm.classList.toggle("on"); toast(`${DB.contas[i].nome}: automático ${DB.contas[i].automatico ? "ligado" : "desligado"}`); }

// ---------- toast ----------
function toast(msg) { const old = document.getElementById("toast"); if (old) old.remove(); const t = el(`<div id="toast">${msg}</div>`); document.body.appendChild(t); setTimeout(() => t.remove(), 1800); }

// ---------- arrastar para o lado (toca, segura e puxa) ----------
function enableDragScroll(elm) {
  let down = false, startX = 0, startLeft = 0, moved = false;
  elm.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "touch") return; // toque usa o scroll nativo
    down = true; moved = false; startX = e.clientX; startLeft = elm.scrollLeft;
    elm.setPointerCapture(e.pointerId); elm.classList.add("dragging");
  });
  elm.addEventListener("pointermove", (e) => {
    if (!down) return;
    const dx = e.clientX - startX;
    if (Math.abs(dx) > 4) moved = true;
    elm.scrollLeft = startLeft - dx;
  });
  const end = () => { down = false; elm.classList.remove("dragging"); };
  elm.addEventListener("pointerup", end);
  elm.addEventListener("pointercancel", end);
  // se arrastou, não dispara o clique do card
  elm.addEventListener("click", (e) => { if (moved) { e.stopPropagation(); e.preventDefault(); moved = false; } }, true);
}

// ============================================================
// NAVEGAÇÃO
// ============================================================
const RENDER = { inicio: renderInicio, grade: renderGrade, esteira: renderEsteira, calendario: renderCalendario, conteudo: renderConteudo, criar: renderCriar, analytics: renderAnalytics, contas: renderContas };
const NAV_VIEWS = ["inicio", "grade", "criar", "analytics", "contas"];
function irPara(view) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("is-active", b.dataset.view === view));
  content.scrollTop = 0; window.scrollTo(0, 0);
  (RENDER[view] || renderInicio)();
  document.querySelectorAll(".grade-scroll, .kanban-scroll").forEach(enableDragScroll);
}
document.getElementById("tabbar").addEventListener("click", (e) => { const b = e.target.closest(".tab"); if (b) irPara(b.dataset.view); });
document.getElementById("btnSino").addEventListener("click", () => toast("3 notificações"));

irPara("inicio");
