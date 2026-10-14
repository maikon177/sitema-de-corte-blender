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
function esc(s) { return (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
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
// Gráfico de barras simples — dados reais.
// color: uma cor (string) OU uma cor por barra (array). labels: texto por barra.
function barChart(vals, color, labels) {
  const w = 300, h = 104, n = vals.length, gap = 6, max = Math.max(1, ...vals);
  const bw = n ? (w - gap * (n - 1)) / n : w;
  const cor = (i) => Array.isArray(color) ? color[i] : color;
  const bars = vals.map((v, i) => {
    const bh = Math.max(3, (v / max) * (h - 30));
    const x = i * (bw + gap), y = h - bh - 18;
    const lab = labels ? labels[i] : (i + 1);
    return `<rect x="${x}" y="${y}" width="${bw}" height="${bh}" rx="3" fill="${cor(i)}" ${v > 0 ? "" : 'opacity="0.35"'}/>`
         + `<text x="${x + bw / 2}" y="${h - 4}" fill="var(--text-3)" font-size="9" text-anchor="middle">${lab}</text>`
         + `<text x="${x + bw / 2}" y="${y - 3}" fill="var(--text-2)" font-size="10" text-anchor="middle">${v}</text>`;
  }).join("");
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}" preserveAspectRatio="xMidYMid meet">${bars}</svg>`;
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
    const pill = p.status === "publicado" ? `<span class="pill publicado">Publicado</span>` : `<span class="pill pronto">Agendado</span>`;
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
  h += `<div class="field-label">Etapa atual</div><select><option>Ideia</option><option>IA gerou</option><option>Agendado</option><option>Publicado</option></select>`;
  h += `<div class="field-label">Mover para</div><div class="mover">
          <button class="mv" onclick="toast('Movido: IA gerou')">${IC.robot}<span>IA gerou</span></button>
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
// CALENDÁRIO  (LIGADO NA API — gerado automático da fila no servidor)
// Produto: posta sozinho; aqui só acompanho e CANCELO o que não gostar.
// ============================================================
let calData = null;     // último calendário recebido da API
let calDiaSel = null;   // data ISO do dia selecionado

async function renderCalendario() {
  content.innerHTML = `<div class="view-title">Calendário</div><div class="view-sub">Carregando do servidor…</div>`;
  try {
    calData = await API.calendario();
  } catch (e) {
    content.innerHTML = `<div class="view-title">Calendário</div>
      <div class="view-sub">Não consegui falar com o servidor</div>
      <div class="card" style="margin-top:12px">
        <div style="font-weight:600;margin-bottom:6px">Servidor offline</div>
        <div class="muted" style="font-size:13px;line-height:1.5">
          A API (instagram-poster/api.py) precisa estar rodando. Abra o app por ela
          (http://localhost:5000), não pelo arquivo direto.</div>
        <button class="btn grad block" style="margin-top:12px" onclick="renderCalendario()">Tentar de novo</button>
      </div>`;
    return;
  }

  const comPosts = calData.dias.filter((d) => d.posts.length);
  let h = `<div class="view-title">Calendário</div><div class="view-sub">Posta sozinho · cancele o que não quiser · máx. ${calData.maxPorDia}/dia</div>`;

  if (!comPosts.length) {
    h += `<div class="card" style="margin-top:12px">
            <div style="font-weight:600;margin-bottom:6px">Nada na fila</div>
            <div class="muted" style="font-size:13px;line-height:1.5">
              Envie fotos pela aba <b>Criar</b> ou <b>Conteúdo</b>. Assim que tiver fotos na fila,
              o servidor monta o calendário sozinho.</div>
          </div>`;
    content.innerHTML = h;
    return;
  }

  // seleção padrão = primeiro dia com posts
  if (!calDiaSel || !comPosts.some((d) => d.data === calDiaSel)) calDiaSel = comPosts[0].data;

  // tira de dias (só os que têm posts)
  h += `<div class="day-strip">`;
  comPosts.forEach((d) => {
    const cor = d.posts[0] ? d.posts[0].cor : "var(--text-3)";
    h += `<div class="day-pick ${d.data === calDiaSel ? "on" : ""}" onclick="calDiaSel='${d.data}';renderCalendario()">
            <div class="dp-d">${d.diaSem}</div><div class="dp-n">${d.diaNum}</div>
            <div class="dp-dot" style="background:${cor}"></div>
          </div>`;
  });
  h += `</div>`;

  const dia = comPosts.find((d) => d.data === calDiaSel) || comPosts[0];
  h += `<div class="day-label">${dia.diaSem}, ${dia.diaNum}</div>`;
  dia.posts.forEach((p) => {
    const cap = p.legenda
      ? esc(p.legenda)
      : `<span class="muted">Sem legenda ainda — toque em “Nova legenda”.</span>`;
    h += `<div class="post-card">
            <div class="pc-img" style="background-image:url('${p.img}')"><span class="pc-time-ov"><span class="dot" style="background:${p.cor}"></span> ${p.hora}</span></div>
            <div class="pc-body"><div class="pc-title">${p.arquivo}</div>
              <div class="pc-acct"><span class="dot" style="background:${p.cor}"></span> ${p.nome} · ${LBL_FMT[p.formato] || "FEED"}</div>
              <div class="pc-cap" id="cap_${p.id}" style="font-size:13px;line-height:1.5;white-space:pre-wrap;margin:8px 0 10px">${cap}</div>
              <div class="pc-actions">
                <button class="btn grad flex small" onclick="novaLegenda('${p.id}')">${IC.sparkles} Nova legenda</button>
                <button class="btn flex small" onclick="reprovarPost('${p.id}')">Reprovar</button>
              </div>
            </div>
          </div>`;
  });
  content.innerHTML = h;
}

// Reprovar = não gostei: a foto sai da fila (vai pra _canceladas no servidor)
async function reprovarPost(id) {
  try {
    await API.cancelar(id);
    toast("Reprovado — sai da fila ✓");
    await renderCalendario();
  } catch (e) {
    toast("Não consegui reprovar agora");
  }
}

// Nova legenda = pede ao servidor pra gerar outra legenda com IA pra essa foto
async function novaLegenda(id) {
  const cap = document.getElementById(`cap_${id}`);
  if (cap) cap.textContent = "Gerando legenda com IA…";
  try {
    const r = await API.novaLegenda(id);
    if (cap) cap.textContent = r.legenda;
    if (calData) calData.dias.forEach((d) => d.posts.forEach((p) => { if (p.id === id) p.legenda = r.legenda; }));
    toast("Legenda nova pronta ✓");
  } catch (e) {
    if (cap) cap.textContent = "Não consegui gerar agora — tente de novo.";
    toast("Falha ao gerar legenda");
  }
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
// ANALYTICS  (DESEMPENHO REAL — últimas publicações ao vivo do Instagram)
// ============================================================
let anContas = null;      // contas reais (/api/contas)
let anSel = null;         // slug da conta selecionada
const anCache = {};       // cache das publicações por conta

function anCabecalho() {
  let h = `<div class="view-title">Desempenho</div><div class="view-sub">Últimas publicações reais do Instagram, por conta</div>`;
  h += `<div class="day-strip">`;
  anContas.forEach((c) => {
    h += `<div class="day-pick ${c.slug === anSel ? "on" : ""}" onclick="anSel='${c.slug}';renderAnalytics()" style="min-width:auto;padding:8px 14px">
            <div class="dp-d" style="white-space:nowrap">${c.nome.replace("Pata3D ", "")}</div>
            <div class="dp-dot" style="background:${c.cor};margin:4px auto 0"></div>
          </div>`;
  });
  h += `</div>`;
  return h;
}

async function renderAnalytics(force) {
  content.innerHTML = `<div class="view-title">Desempenho</div><div class="view-sub">Carregando…</div>`;
  try {
    if (!anContas) anContas = await API.contas();
  } catch (e) {
    content.innerHTML = `<div class="view-title">Desempenho</div><div class="view-sub">Servidor offline</div>
      <div class="card" style="margin-top:12px"><div class="muted" style="font-size:13px">Abra o app por http://localhost:5000.</div>
      <button class="btn grad block" style="margin-top:12px" onclick="renderAnalytics()">Tentar de novo</button></div>`;
    return;
  }
  if (!anSel) { const a = anContas.find((c) => c.ativa) || anContas[0]; anSel = a ? a.slug : null; }

  const head = anCabecalho();

  // publicações ao vivo (cache por conta)
  let live = anCache[anSel];
  if (force || !live) {
    content.innerHTML = head + `<div class="card"><div class="muted" style="font-size:13px">Puxando as últimas publicações do Instagram… (leva alguns segundos)</div></div>`;
    try {
      live = await API.instagramPosts(anSel);
      anCache[anSel] = live;
      if (force) toast("Puxado do Instagram ✓");
    } catch (e) {
      content.innerHTML = head + `<div class="card" style="border-color:var(--warn)">
        <div style="font-size:13px;color:var(--text-2);line-height:1.5">Não consegui puxar do Instagram agora.</div>
        <button class="btn grad block" style="margin-top:10px" onclick="renderAnalytics(true)">Tentar de novo</button></div>`;
      return;
    }
  }

  let h = head;
  h += `<div class="card" style="border-color:var(--roxo)"><div style="font-size:12px;color:var(--text-2)">
          <b style="color:var(--text)">Fonte:</b> ${live.fonte} · ${live.total} publicação(ões)</div></div>`;

  const posts = live.posts || [];
  const soma = posts.reduce((a, p) => ({ reach: a.reach + (p.reach || 0), likes: a.likes + (p.likes || 0), comments: a.comments + (p.comments || 0) }), { reach: 0, likes: 0, comments: 0 });
  h += `<div class="card"><div class="cap">${live.nome.toUpperCase()}</div><div class="kpis" style="margin-top:14px">
          <div class="kpi"><div class="k-lab">Alcance</div><div class="k-val">${soma.reach.toLocaleString("pt-BR")}</div></div>
          <div class="kpi"><div class="k-lab">Curtidas</div><div class="k-val">${soma.likes.toLocaleString("pt-BR")}</div></div>
          <div class="kpi"><div class="k-lab">Comentários</div><div class="k-val">${soma.comments.toLocaleString("pt-BR")}</div></div>
        </div></div>`;

  if (!posts.length) {
    h += `<div class="card"><div class="muted" style="font-size:13px">Essa conta ainda não tem publicações no Instagram.</div></div>`;
  } else {
    const ordem = posts.slice().reverse(); // da mais antiga à mais recente
    const reaches = ordem.map((p) => p.reach || 0);
    h += `<div class="card"><div class="cap">ALCANCE POR PUBLICAÇÃO</div>
            <div style="margin-top:10px">${barChart(reaches, live.cor)}</div>
            <div class="muted" style="font-size:11px;margin-top:4px">da mais antiga (1) à mais recente${live.temAlcance ? "" : " · essa conta não libera alcance"}</div></div>`;

    h += `<div class="section-head"><h3>Últimas publicações</h3><span class="muted">${posts.length}</span></div>`;
    h += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">`;
    posts.forEach((p) => {
      const tipo = p.tipo === "VIDEO" ? "REEL" : p.tipo === "CAROUSEL_ALBUM" ? "ÁLBUM" : "FOTO";
      h += `<div style="background:var(--card2,#1b1b26);border:1px solid var(--line,#2a2a3a);border-radius:12px;overflow:hidden;cursor:pointer" onclick="window.open('${p.permalink}','_blank')">
              <div style="height:118px;background:#000 center/cover no-repeat;background-image:url('${p.thumb}');position:relative">
                <span style="position:absolute;top:6px;left:6px;background:rgba(0,0,0,.6);color:#fff;font-size:9px;padding:2px 6px;border-radius:6px">${tipo}</span>
              </div>
              <div class="muted" style="font-size:11px;padding:7px 9px">alcance ${p.reach} · ❤ ${p.likes} · 💬 ${p.comments}</div>
            </div>`;
    });
    h += `</div>`;
  }

  h += `<button class="btn grad block" style="margin-top:16px" onclick="renderAnalytics(true)">Atualizar do Instagram</button>`;
  content.innerHTML = h;
}

// ============================================================
// CONTEÚDO  (LIGADO NA API — pastas reais do servidor)
// Entrada 'ideias' + a fila de cada conta. Mover foto = mandar pra fila.
// ============================================================
let bibData = null;
let pastaSel = null;

async function renderConteudo() {
  content.innerHTML = `<div class="view-title">Conteúdo</div><div class="view-sub">Carregando do servidor…</div>`;
  try {
    bibData = await API.biblioteca();
  } catch (e) {
    content.innerHTML = `<div class="view-title">Conteúdo</div><div class="view-sub">Servidor offline</div>
      <div class="card" style="margin-top:12px"><div class="muted" style="font-size:13px">Abra o app por http://localhost:5000.</div>
      <button class="btn grad block" style="margin-top:12px" onclick="renderConteudo()">Tentar de novo</button></div>`;
    return;
  }

  let h = `<div class="view-title">Conteúdo</div><div class="view-sub">Suas fotos no servidor, por pasta</div>`;
  h += `<div class="dropzone" onclick="document.getElementById('bibFile').click()">${IC.upload}
          <div style="margin-top:8px">Despejar fotos aqui</div>
          <div class="muted" style="margin-top:4px">entram na Entrada; depois você manda pra fila de uma conta</div></div>
        <input id="bibFile" type="file" accept="image/*" multiple style="display:none" onchange="enviarParaIdeias(this.files)">`;

  h += `<div class="section-head"><h3>Pastas</h3><span class="muted">${bibData.pastas.length}</span></div>`;
  h += `<div class="folders">`;
  bibData.pastas.forEach((p) => {
    const capa = p.fotos[0] ? p.fotos[0].url : "";
    const tag = p.tipo === "inbox" ? "entrada" : "fila";
    h += `<div class="folder" onclick="abrirPasta('${p.id}')">
            <div class="folder-cover" style="background-image:url('${capa}')"><span class="folder-count">${p.total}</span></div>
            <div class="folder-name"><span class="dot" style="background:${p.cor}"></span> ${p.nome} <span class="muted" style="font-size:10px">· ${tag}</span></div>
          </div>`;
  });
  h += `</div>`;
  content.innerHTML = h;
}

async function enviarParaIdeias(files) {
  if (!files || !files.length) return;
  toast("Enviando…");
  try {
    await API.upload("ideias", files);
    toast("Fotos na Entrada ✓");
    await renderConteudo();
  } catch (e) {
    toast("Não consegui enviar");
  }
}

function abrirPasta(id) {
  pastaSel = id;
  const p = bibData.pastas.find((x) => x.id === id);
  if (!p) return irPara("conteudo");
  const destinos = bibData.contas.filter((c) => c.slug !== id); // pra onde dá pra mover
  let h = `<div class="det-top"><button class="det-back" onclick="irPara('conteudo')">${IC.back}</button><div class="det-ttl">${p.nome}</div><div style="width:40px"></div></div>`;

  if (!p.total) {
    h += `<div class="card"><div class="muted" style="font-size:13px">Pasta vazia.</div></div>`;
    content.innerHTML = h;
    return;
  }

  h += `<div class="muted" style="margin:-6px 0 14px">${p.total} foto(s) · toque numa conta embaixo da foto pra mandar pra fila dela</div>`;
  p.fotos.forEach((it) => {
    const botoes = destinos.map((c) =>
      `<button class="btn small" style="border-color:${c.cor}" onclick="moverFoto('${id}','${c.slug}','${esc(it.arquivo)}')">→ ${c.nome.replace("Pata3D ", "")}</button>`
    ).join("");
    const paraIdeias = id !== "ideias"
      ? `<button class="btn small" onclick="moverFoto('${id}','ideias','${esc(it.arquivo)}')">→ Ideias</button>`
      : "";
    h += `<div class="card" style="padding:10px">
            <div style="display:flex;gap:10px">
              <div style="width:84px;height:84px;border-radius:10px;flex:0 0 auto;background:#000 center/cover no-repeat;background-image:url('${it.url}')"></div>
              <div style="flex:1;min-width:0">
                <div style="font-size:12px;word-break:break-all">${esc(it.arquivo)}</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">${botoes}${paraIdeias}</div>
              </div>
            </div>
          </div>`;
  });
  content.innerHTML = h;
  content.scrollTop = 0; window.scrollTo(0, 0);
}

async function moverFoto(de, para, arquivo) {
  try {
    await API.mover(de, para, arquivo);
    toast("Movido ✓");
    bibData = await API.biblioteca(); // recarrega contagens/fotos
    abrirPasta(de);                    // continua na mesma pasta
  } catch (e) {
    toast("Não consegui mover");
  }
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

// ---------- notificações (avisos reais do servidor) ----------
async function abrirNotificacoes() {
  const old = document.getElementById("notif-overlay");
  if (old) old.remove();
  let dados;
  try {
    dados = await API.notificacoes();
  } catch (e) {
    toast("Não consegui buscar os avisos");
    return;
  }
  const cor = (n) => n === "alto" ? "var(--danger)" : n === "medio" ? "var(--warn)" : "var(--ok)";
  let itens = dados.avisos.map((a) =>
    `<div class="rule-row"><span class="dot" style="background:${cor(a.nivel)}"></span>
       <div class="rule-main" style="margin-left:8px"><div class="rule-t" style="font-size:13px">${esc(a.texto)}</div></div></div>`
  ).join("");
  const ov = el(`<div id="notif-overlay" style="position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:50;display:flex;align-items:flex-start;justify-content:center;padding:70px 16px 16px">
      <div style="width:100%;max-width:380px;background:var(--bg,#14141c);border:1px solid var(--line,#2a2a3a);border-radius:16px;padding:16px;max-height:80vh;overflow:auto">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
          <div style="font-weight:700;font-size:16px">Avisos${dados.total ? ` (${dados.total})` : ""}</div>
          <button class="icon-btn" onclick="document.getElementById('notif-overlay').remove()">✕</button>
        </div>
        ${itens}
      </div></div>`);
  ov.addEventListener("click", (e) => { if (e.target === ov) ov.remove(); });
  document.body.appendChild(ov);
  // atualiza o pontinho do sino
  const sino = document.getElementById("btnSino");
  if (sino) sino.classList.toggle("has-badge", dados.total > 0);
}

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
// CONFIGURAÇÕES  (LIGADO NO SERVIDOR — 3 contas reais)
// Chaves ficam no .env do servidor; aqui só o status + IA por conta + regras.
// ============================================================
let cfgData = null;

function cfgIaOptions(disp, sel, incluirVazio) {
  let o = incluirVazio ? `<option value="" ${!sel ? "selected" : ""}>— nenhuma —</option>` : "";
  o += Object.entries(disp).map(([k, v]) => `<option value="${k}" ${k === sel ? "selected" : ""}>${v}</option>`).join("");
  return o;
}

async function renderConfig() {
  content.innerHTML = `<div class="view-title">Configurações</div><div class="view-sub">Carregando do servidor…</div>`;
  try {
    cfgData = await API.config();
  } catch (e) {
    content.innerHTML = `<div class="view-title">Configurações</div>
      <div class="view-sub">Servidor offline</div>
      <div class="card" style="margin-top:12px"><div class="muted" style="font-size:13px;line-height:1.5">
        A API precisa estar rodando (abra por http://localhost:5000).</div>
        <button class="btn grad block" style="margin-top:12px" onclick="renderConfig()">Tentar de novo</button></div>`;
    return;
  }

  const disp = cfgData.iasDisponiveis;
  let h = `<div class="view-title">Configurações</div><div class="view-sub">IA por conta e regras — salvo no servidor</div>`;

  // 1) Status das chaves (read-only; valor nunca sai do servidor)
  const chip = (ok) => ok
    ? `<span class="pill publicado">configurada</span>`
    : `<span class="pill" style="background:var(--danger);color:#fff">falta no .env</span>`;
  h += `<div class="section-head"><h3>Chaves de API</h3></div><div class="card">
          <div class="rule-row"><div class="rule-main"><div class="rule-t">Gemini</div><div class="rule-s muted">legendas</div></div>${chip(cfgData.chavesStatus.gemini)}</div>
          <div class="rule-row"><div class="rule-main"><div class="rule-t">ImgBB</div><div class="rule-s muted">hospeda a imagem pra postar</div></div>${chip(cfgData.chavesStatus.imgbb)}</div>
          <div class="rule-row"><div class="rule-main"><div class="rule-t">Grok / xAI</div><div class="rule-s muted">opcional (pipeline IA)</div></div>${chip(cfgData.chavesStatus.grok)}</div>
          <div class="muted" style="font-size:12px;margin-top:8px">As chaves e os tokens das contas ficam no arquivo <b>.env</b> do servidor, por segurança. Aqui só mostro se estão presentes.</div>
        </div>`;

  // 2) IA por conta (contas reais)
  h += `<div class="section-head"><h3>IA por conta</h3><span class="muted">${cfgData.contas.length}</span></div>`;
  cfgData.contas.forEach((c) => {
    const badge = c.ativa ? `<span class="pill publicado">ativa</span>` : `<span class="pill">pausada</span>`;
    h += `<div class="card">
            <div class="conta-row" style="padding-top:0;border:none">
              <div class="conta-av" style="background:${c.cor}">${pawSVG(16)}</div>
              <div class="conta-main"><div class="conta-t">${c.nome}</div><div class="conta-s muted">${esc(c.nicho || "")}</div></div>
              ${badge}
            </div>
            <label class="field-label">Pipeline de imagem</label>
            <select id="cf_${c.slug}_pipeline">
              <option value="simples" ${c.pipeline === "simples" ? "selected" : ""}>Foto real + edição simples (contraste / fundo)</option>
              <option value="ia" ${c.pipeline === "ia" ? "selected" : ""}>IA: transforma 2D em conceito colecionável</option>
            </select>
            <label class="field-label">IA da legenda</label>
            <select id="cf_${c.slug}_iaLegenda">${cfgIaOptions(disp, c.iaLegenda, false)}</select>
            <label class="field-label">IA da imagem <span class="muted">(só quando pipeline = IA)</span></label>
            <select id="cf_${c.slug}_iaImagem">${cfgIaOptions(disp, c.iaImagem, true)}</select>
          </div>`;
  });

  // 3) Regras (valem pro calendário automático)
  const r = cfgData.regras;
  h += `<div class="section-head"><h3>Regras de postagem</h3></div><div class="card">`;
  h += `<label class="field-label" style="margin-top:0">Máximo de posts por dia (por conta)</label><input type="number" id="r_max" min="1" max="20" value="${r.maxPorDia}">`;
  h += `<label class="field-label">Horários do dia (separados por vírgula)</label><input id="r_horarios" placeholder="09:10, 14:00, 18:30" value="${(r.horarios || []).join(", ")}">`;
  h += `<div class="rule-row"><div class="rule-main"><div class="rule-t">Bloqueio de repetição</div><div class="rule-s muted">Não posta foto repetida</div></div><div class="switch ${r.bloqueioRepeticao ? "on" : ""}" id="r_rep" onclick="this.classList.toggle('on')"></div></div>`;
  h += `<label class="field-label">Alerta de estoque (dias de antecedência)</label><input type="number" id="r_alerta" min="1" max="60" value="${r.alertaEstoqueDias}">`;
  h += `</div>`;

  h += `<button class="btn grad block" style="margin-top:16px" onclick="salvarConfig()">Salvar no servidor</button>`;
  content.innerHTML = h;
  content.scrollTop = 0; window.scrollTo(0, 0);
}

async function salvarConfig() {
  const g = (id) => { const e = document.getElementById(id); return e ? e.value.trim() : ""; };
  const contas = {};
  (cfgData?.contas || []).forEach((c) => {
    contas[c.slug] = {
      pipeline:  g(`cf_${c.slug}_pipeline`),
      iaLegenda: g(`cf_${c.slug}_iaLegenda`),
      iaImagem:  g(`cf_${c.slug}_iaImagem`),
    };
  });
  const rep = document.getElementById("r_rep");
  const body = {
    regras: {
      maxPorDia:         parseInt(g("r_max"), 10) || 1,
      horarios:          g("r_horarios").split(",").map((s) => s.trim()).filter(Boolean),
      bloqueioRepeticao: rep ? rep.classList.contains("on") : true,
      alertaEstoqueDias: parseInt(g("r_alerta"), 10) || 7,
    },
    contas,
  };
  try {
    await API.salvarConfig(body);
    toast("Salvo no servidor ✓");
  } catch (e) {
    toast("Não consegui salvar no servidor");
  }
}

// ============================================================
// NAVEGAÇÃO
// ============================================================
const RENDER = { inicio: renderInicio, grade: renderGrade, esteira: renderEsteira, calendario: renderCalendario, conteudo: renderConteudo, criar: renderCriar, analytics: renderAnalytics, contas: renderContas, config: renderConfig };
const NAV_VIEWS = ["inicio", "grade", "criar", "analytics", "contas"];
function irPara(view) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("is-active", b.dataset.view === view));
  content.scrollTop = 0; window.scrollTo(0, 0);
  (RENDER[view] || renderInicio)();
  document.querySelectorAll(".grade-scroll, .kanban-scroll").forEach(enableDragScroll);
}
document.getElementById("tabbar").addEventListener("click", (e) => { const b = e.target.closest(".tab"); if (b) irPara(b.dataset.view); });
document.getElementById("btnSino").addEventListener("click", abrirNotificacoes);
document.getElementById("btnConfig").addEventListener("click", () => irPara("config"));

irPara("inicio");
