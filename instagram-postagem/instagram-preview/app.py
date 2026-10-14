from __future__ import annotations

import html
import hashlib
import json
import mimetypes
import posixpath
import socket
import sys
import urllib.parse
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

POSTER_DIR = Path(r"D:\intagram postagem\instagram-poster").resolve()
if str(POSTER_DIR) not in sys.path:
    sys.path.insert(0, str(POSTER_DIR))

from rascunhos import build_draft_payload

ROOT_MEDIA_DIR = Path(r"D:\intagram postagem\instagram-poster\fotos\pata3d_cortadores").resolve()
HOST = "127.0.0.1"
PORT = 8787
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Instagram Preview Pata3D</title>
  <style>
    :root {
      --bg: #fafafa;
      --panel: #ffffff;
      --border: #dbdbdb;
      --muted: #737373;
      --text: #121212;
      --accent: #0095f6;
      --heart: #ff3040;
      --shadow: 0 10px 30px rgba(0,0,0,0.08);
      --radius: 18px;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Tahoma, sans-serif;
    }

    .app {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 250px minmax(0, 1fr) 340px;
      gap: 24px;
      padding: 24px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: var(--shadow);
    }

    .sidebar {
      padding: 22px;
      position: sticky;
      top: 24px;
      height: fit-content;
    }

    .logo {
      font-size: 1.45rem;
      font-weight: 800;
      margin-bottom: 20px;
      letter-spacing: -0.02em;
    }

    .profile {
      display: flex;
      gap: 14px;
      align-items: center;
      margin-bottom: 20px;
    }

    .avatar {
      width: 62px;
      height: 62px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ffb5cb, #9fdcf8);
      display: grid;
      place-items: center;
      font-weight: 800;
      color: #5a2a3c;
    }

    .muted { color: var(--muted); }
    .tiny { font-size: 0.86rem; }

    .stats {
      display: grid;
      gap: 10px;
      margin: 22px 0;
    }

    .stat {
      display: flex;
      justify-content: space-between;
      padding: 10px 12px;
      border-radius: 14px;
      background: #fafafa;
      border: 1px solid #efefef;
      font-size: 0.92rem;
    }

    .actions {
      display: grid;
      gap: 10px;
    }

    .button {
      border: 0;
      border-radius: 14px;
      padding: 12px 14px;
      font-weight: 700;
      background: var(--accent);
      color: white;
      cursor: pointer;
      text-decoration: none;
      text-align: center;
    }

    .button.secondary {
      background: #efefef;
      color: #121212;
    }

    .main {
      display: grid;
      gap: 16px;
    }

    .topbar {
      padding: 18px 20px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }

    .tabs {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .tab {
      border: 1px solid var(--border);
      background: white;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
    }

    .tab.active {
      background: #111;
      color: white;
      border-color: #111;
    }

    .feed-list {
      display: grid;
      gap: 22px;
    }

    .post-card {
      background: white;
      border: 1px solid var(--border);
      border-radius: 24px;
      overflow: hidden;
    }

    .post-header, .post-footer {
      padding: 14px 16px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
    }

    .post-user {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .post-user .mini-avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ffd8e5, #ccefff);
      display: grid;
      place-items: center;
      font-size: 0.85rem;
      font-weight: 800;
      color: #5e2946;
    }

    .post-media {
      position: relative;
      background: #f5f5f5;
    }

    .post-media img, .post-media video {
      width: 100%;
      display: block;
      max-height: 760px;
      object-fit: cover;
    }

    .media-flag {
      position: absolute;
      top: 14px;
      right: 14px;
      padding: 8px 10px;
      background: rgba(0,0,0,0.65);
      color: white;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
    }

    .carousel-dots {
      position: absolute;
      left: 50%;
      bottom: 14px;
      transform: translateX(-50%);
      display: flex;
      gap: 6px;
    }

    .carousel-dots span {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: rgba(255,255,255,0.55);
    }

    .carousel-dots span.active { background: white; }

    .post-footer {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }

    .icon-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }

    .icon-group {
      display: flex;
      gap: 14px;
      font-size: 1.25rem;
    }

    .likes {
      font-weight: 700;
      font-size: 0.94rem;
    }

    .caption {
      font-size: 0.96rem;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .hashtags {
      color: #00376b;
      font-size: 0.92rem;
      line-height: 1.4;
    }

    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 0.86rem;
      color: var(--muted);
    }

    .reels-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 16px;
    }

    .reel-card {
      background: white;
      border: 1px solid var(--border);
      border-radius: 26px;
      overflow: hidden;
      cursor: pointer;
    }

    .reel-thumb {
      aspect-ratio: 9 / 16;
      position: relative;
      background: linear-gradient(180deg, #2a2a2a, #111);
      overflow: hidden;
    }

    .reel-thumb img, .reel-thumb video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: scale(1.02);
    }

    .reel-gradient {
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(0,0,0,0.18), rgba(0,0,0,0.0) 26%, rgba(0,0,0,0.0) 58%, rgba(0,0,0,0.82)),
        radial-gradient(circle at top right, rgba(255,93,133,0.16), transparent 34%);
    }

    .reel-overlay {
      position: absolute;
      left: 14px;
      right: 14px;
      bottom: 18px;
      color: white;
    }

    .reel-caption-pill {
      display: inline-block;
      max-width: 84%;
      padding: 7px 10px;
      border-radius: 10px;
      background: rgba(0,0,0,0.84);
      border: 1px solid rgba(255,255,255,0.08);
      font-size: 0.76rem;
      line-height: 1.2;
      font-weight: 600;
      letter-spacing: -0.01em;
      box-shadow: 0 6px 18px rgba(0,0,0,0.25);
    }

    .reel-meta-line {
      margin-top: 8px;
      font-size: 0.72rem;
      color: rgba(255,255,255,0.82);
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }

    .reel-edit-badge {
      position: absolute;
      top: 14px;
      left: 14px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(0,0,0,0.6);
      color: rgba(255,255,255,0.95);
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .reel-caption-floating {
      position: absolute;
      left: 16px;
      right: 16px;
      top: 54%;
      display: flex;
      justify-content: flex-start;
      pointer-events: none;
    }

    .reel-meta-line .dot {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: rgba(255,255,255,0.7);
      display: inline-block;
    }

    .planner {
      padding: 20px;
      display: grid;
      gap: 12px;
    }

    .plan-card {
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 14px;
      background: #fff;
    }

    .detail {
      padding: 20px;
      position: sticky;
      top: 24px;
      height: fit-content;
      display: grid;
      gap: 14px;
    }

    .detail h3 { margin: 0; }

    .detail-preview {
      border-radius: 20px;
      overflow: hidden;
      border: 1px solid var(--border);
      background: #f6f6f6;
    }

    .detail-preview img, .detail-preview video {
      width: 100%;
      display: block;
      max-height: 280px;
      object-fit: cover;
    }

    .detail-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .chip {
      border-radius: 999px;
      padding: 8px 10px;
      font-size: 0.82rem;
      background: #f4f4f4;
      border: 1px solid #ececec;
    }

    .hidden { display: none !important; }

    @media (max-width: 1200px) {
      .app {
        grid-template-columns: 220px 1fr;
      }

      .detail {
        grid-column: 1 / -1;
        position: static;
      }
    }

    @media (max-width: 880px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar, .detail {
        position: static;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="panel sidebar">
      <div class="logo">Instagram Preview</div>
      <div class="profile">
        <div class="avatar">P3D</div>
        <div>
          <div><strong>@pata3d</strong></div>
          <div class="muted tiny">Prévia local das postagens</div>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><span>Rascunhos</span><strong id="stat-posts">0</strong></div>
        <div class="stat"><span>Reels</span><strong id="stat-reels">0</strong></div>
        <div class="stat"><span>Carrosséis</span><strong id="stat-carousels">0</strong></div>
      </div>
      <div class="actions">
        <a class="button" href="/refresh">Atualizar rascunhos</a>
        <a class="button secondary" href="/raw-data">Ver JSON gerado</a>
      </div>
      <p class="muted tiny" style="margin-top:18px;">Fonte: <code>__ROOT_MEDIA_DIR__</code></p>
    </aside>

    <main class="main">
      <section class="panel topbar">
        <div>
          <strong>Prévia local inspirada no Instagram</strong>
          <div class="muted tiny">Feed, carrossel, legenda, hashtags e planejamento antes de postar de verdade.</div>
        </div>
        <div class="tabs">
          <button class="tab active" data-view="feed">Feed</button>
          <button class="tab" data-view="reels">Reels</button>
          <button class="tab" data-view="planner">Planejamento</button>
        </div>
      </section>

      <section id="feed-view" class="feed-list"></section>
      <section id="reels-view" class="reels-grid hidden"></section>
      <section id="planner-view" class="panel planner hidden"></section>
    </main>

    <aside class="panel detail">
      <h3>Post selecionado</h3>
      <div class="muted tiny">Clique em um post ou reel para ver a prévia detalhada.</div>
      <div id="detail-preview" class="detail-preview"></div>
      <div id="detail-content" class="caption muted">Nenhum post selecionado ainda.</div>
      <div id="detail-tags" class="detail-tags"></div>
    </aside>
  </div>

  <script>
    const PREVIEW_DATA = __JSON_DATA__;

    const feedView = document.getElementById('feed-view');
    const reelsView = document.getElementById('reels-view');
    const plannerView = document.getElementById('planner-view');
    const detailPreview = document.getElementById('detail-preview');
    const detailContent = document.getElementById('detail-content');
    const detailTags = document.getElementById('detail-tags');

    document.getElementById('stat-posts').textContent = PREVIEW_DATA.posts.length;
    document.getElementById('stat-reels').textContent = PREVIEW_DATA.posts.filter(p => p.preview_type === 'reel').length;
    document.getElementById('stat-carousels').textContent = PREVIEW_DATA.posts.filter(p => p.post_type === 'carousel').length;

    function mediaTag(post, media, extraClass = '') {
      const src = media.preview_url;
      if (media.kind === 'video') {
        return `<video class="${extraClass}" src="${src}" controls muted playsinline preload="metadata"></video>`;
      }
      return `<img class="${extraClass}" src="${src}" alt="${escapeHtml(post.title)}">`;
    }

    function escapeHtml(text) {
      return text.replace(/[&<>"']/g, function(ch) {
        return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'":'&#39;'})[ch];
      });
    }

    function renderFeed(posts) {
      feedView.innerHTML = posts.map(post => {
        const media = post.media[0];
        const dots = post.media.length > 1
          ? `<div class="carousel-dots">${post.media.map((_, i) => `<span class="${i === 0 ? 'active' : ''}"></span>`).join('')}</div>`
          : '';
        const flag = post.post_type === 'carousel'
          ? '<div class="media-flag">Carrossel</div>'
          : post.preview_type === 'reel'
            ? '<div class="media-flag">Reel</div>'
            : '';
        return `
          <article class="post-card" data-post-id="${post.id}">
            <div class="post-header">
              <div class="post-user">
                <div class="mini-avatar">P3D</div>
                <div>
                  <div><strong>@pata3d</strong></div>
                  <div class="muted tiny">${escapeHtml(post.schedule_label)}</div>
                </div>
              </div>
              <div class="muted">•••</div>
            </div>
            <div class="post-media">
              ${mediaTag(post, media)}
              ${flag}
              ${dots}
            </div>
            <div class="post-footer">
              <div class="icon-row">
                <div class="icon-group"><span>♡</span><span>💬</span><span>✈</span></div>
                <div class="icon-group"><span>🔖</span></div>
              </div>
              <div class="likes">${post.mock_likes} curtidas</div>
              <div class="caption"><strong>@pata3d</strong> ${escapeHtml(post.caption)}</div>
              <div class="hashtags">${post.hashtags.map(tag => `#${escapeHtml(tag)}`).join(' ')}</div>
              <div class="meta-bar">
                <span>${escapeHtml(post.post_type_label)}</span>
                <span>${escapeHtml(post.source_label)}</span>
                <span>${post.media.length} mídia(s)</span>
              </div>
            </div>
          </article>
        `;
      }).join('');
    }

    function renderReels(posts) {
      reelsView.innerHTML = posts.map(post => {
        const media = post.media[0];
        return `
          <article class="reel-card" data-post-id="${post.id}">
            <div class="reel-thumb">
              ${mediaTag(post, media)}
              <div class="reel-gradient"></div>
              <div class="reel-edit-badge">REEL TESTE</div>
              <div class="reel-caption-floating">
                <div class="reel-caption-pill">${escapeHtml(post.reel_overlay_text || post.overlay_text)}</div>
              </div>
              <div class="reel-overlay">
                <div class="reel-meta-line">
                  <span>@pata3d</span>
                  <span class="dot"></span>
                  <span>${escapeHtml(post.schedule_label)}</span>
                </div>
              </div>
            </div>
          </article>
        `;
      }).join('');
    }

    function renderPlanner(posts) {
      plannerView.innerHTML = posts.map(post => `
        <div class="plan-card" data-post-id="${post.id}">
          <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
            <strong>${escapeHtml(post.title)}</strong>
            <span class="chip">${escapeHtml(post.schedule_label)}</span>
          </div>
          <div class="muted tiny" style="margin-top:6px;">${escapeHtml(post.post_type_label)} • ${escapeHtml(post.source_label)}</div>
          <div class="caption" style="margin-top:10px;">${escapeHtml(post.overlay_text)}</div>
          <div class="hashtags" style="margin-top:10px;">${post.hashtags.map(tag => `#${escapeHtml(tag)}`).join(' ')}</div>
        </div>
      `).join('');
    }

    function selectPost(postId) {
      const post = PREVIEW_DATA.posts.find(p => p.id === postId);
      if (!post) return;
      const firstMedia = post.media[0];
      detailPreview.innerHTML = mediaTag(post, firstMedia);
      detailContent.innerHTML = `
        <div><strong>${escapeHtml(post.title)}</strong></div>
        <div class="muted tiny" style="margin:6px 0 12px;">${escapeHtml(post.schedule_label)} • ${escapeHtml(post.post_type_label)}</div>
        <div style="margin-bottom:10px;"><strong>Texto na imagem:</strong> ${escapeHtml(post.overlay_text)}</div>
        <div style="margin-bottom:10px;"><strong>Legenda:</strong><br>${escapeHtml(post.caption)}</div>
        <div><strong>Fonte:</strong> ${escapeHtml(post.source_label)}</div>
      `;
      detailTags.innerHTML = [
        ...post.hashtags.map(tag => `<span class="chip">#${escapeHtml(tag)}</span>`),
        `<span class="chip">${post.media.length} mídia(s)</span>`
      ].join('');
    }

    function bindSelection(container) {
      container.querySelectorAll('[data-post-id]').forEach(element => {
        element.addEventListener('click', () => selectPost(element.getAttribute('data-post-id')));
      });
    }

    function switchView(view) {
      feedView.classList.toggle('hidden', view !== 'feed');
      reelsView.classList.toggle('hidden', view !== 'reels');
      plannerView.classList.toggle('hidden', view !== 'planner');
      document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === view);
      });
    }

    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => switchView(tab.dataset.view));
    });

    renderFeed(PREVIEW_DATA.posts);
    renderReels(PREVIEW_DATA.posts.filter(post => post.preview_type === 'reel' || post.post_type === 'carousel'));
    renderPlanner(PREVIEW_DATA.posts);
    bindSelection(feedView);
    bindSelection(reelsView);
    bindSelection(plannerView);

    if (PREVIEW_DATA.posts[0]) {
      selectPost(PREVIEW_DATA.posts[0].id);
    }
  </script>
</body>
</html>
"""


@dataclass
class MediaItem:
    path: Path
    kind: str


def make_schedule(index: int) -> tuple[str, str]:
    slots = [
        ("manha", "08:12 • Bom dia / leve"),
        ("tarde", "14:40 • Post principal"),
        ("noite", "20:18 • Reel / destaque"),
    ]
    return slots[index % len(slots)]


def hashtags_for_text(source_label: str, is_encomenda: bool) -> list[str]:
    base = ["pata3d", "confeitaria", "docespersonalizados", "biscoitosdecorados"]
    if is_encomenda:
        base += ["encomenda", "feitoComCarinho", "detalhesqueencantam"]
    if "grupo" in source_label.lower():
        base += ["carrossel", "colecao", "modelinhos"]
    else:
        base += ["cortadores", "carimbo", "ejetor"]
    return base


def infer_tags_from_name(name: str) -> set[str]:
    text = name.lower()
    tags: set[str] = set()
    if any(word in text for word in ["flor", "flower", "margarida"]):
        tags.add("floral")
    if any(word in text for word in ["laco", "laço", "bow"]):
        tags.add("laco")
    if any(word in text for word in ["arco", "rainbow"]):
        tags.add("arco")
    if any(word in text for word in ["cereja", "cherry"]):
        tags.add("fruta")
    if any(word in text for word in ["coelho", "bunny", "pascoa", "páscoa"]):
        tags.add("pascoa")
    if any(word in text for word in ["embal", "saquinho", "pedido", "encomenda"]):
        tags.add("embalado")
    if any(word in text for word in ["fofo", "urso", "boneco", "personagem"]):
        tags.add("fofo")
    return tags


def infer_tags_from_media(media_files: list[Path]) -> set[str]:
    tags: set[str] = set()
    for path in media_files:
        tags.update(infer_tags_from_name(path.stem))
    return tags


def choose_variant(options: list[str], seed_text: str) -> str:
    if not options:
        return ""
    digest = hashlib.sha1(seed_text.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    return options[seed % len(options)]


def title_for_post(source_label: str, tags: set[str], media_count: int) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return "Carrossel de encomenda"
        if "fofo" in tags:
            return "Carrossel de modelinhos"
        return "Carrossel de produtos"

    if "floral" in tags:
        return "Modelinho floral"
    if "laco" in tags:
        return "Modelinho com laço"
    if "arco" in tags:
        return "Modelinho de arco"
    if "fruta" in tags:
        return "Modelinho delicado"
    return source_label


def overlay_for_post(source_label: str, media_count: int, is_encomenda: bool) -> str:
    label = source_label.lower()
    if is_encomenda and media_count > 1:
        return "Encomenda linda por aqui 💖"
    if is_encomenda:
        return "Mais um pedido feito com carinho ✨"
    if "grupo" in label:
        return "Um modelinho mais lindo que o outro ✨"
    return "Passando pra mostrar essa lindeza 😍"


def overlay_for_context(schedule_slot: str, media_count: int, is_encomenda: bool, tags: set[str]) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return "Olha essa encomenda 😍"
        if "fofo" in tags:
            return "Um modelinho mais lindo que o outro ✨"
        return "Passando pra mostrar essa coleção 💖"

    if schedule_slot == "manha":
        if "fofo" in tags:
            return "Bom dia com fofura por aqui ✨"
        return "Bom dia com inspiração doce ✨"
    if "floral" in tags:
        return "Delicadeza em cada detalhe 🌸"
    if "laco" in tags:
        return "Olha esse charme 🎀"
    if "arco" in tags:
        return "Mais um modelinho encantador 🌈"
    if "fruta" in tags:
        return "Detalhes que encantam 🍒"
    if is_encomenda:
        return "Mais um pedido feito com carinho 💖"
    return "Passando pra mostrar essa lindeza 😍"


def reel_overlay_text(source_label: str, tags: set[str], is_encomenda: bool, seed_text: str) -> str:
    if "embalado" in tags:
        return choose_variant(
            [
                "encomenda passando na sua tela \U0001f979",
                "olha esse pedido prontinho \U0001f495",
                "mais uma entrega linda por aqui \u2728",
                "detalhe simples mas faz diferen\u00e7a \U0001f979",
            ],
            seed_text,
        )
    if "floral" in tags:
        return choose_variant(
            [
                "esse detalhe floral ficou um charme \U0001f338",
                "bem delicadinho do jeitinho que amamos \u2728",
                "florzinha linda pra dar destaque \U0001f497",
                "s\u00f3 um toque e j\u00e1 mudou tudo \U0001f979",
            ],
            seed_text,
        )
    if "laco" in tags:
        return choose_variant(
            [
                "um lacinho e pronto: ficou lindo \U0001f380",
                "la\u00e7o fofo pra dar aquele charme \U0001f495",
                "detalhe pequeno mas faz diferen\u00e7a \u2728",
                "essa legendinha aqui \u00e9 s\u00f3 pra dar destaque \U0001f979",
            ],
            seed_text,
        )
    if "arco" in tags:
        return choose_variant(
            [
                "esse modelinho alegra qualquer produ\u00e7\u00e3o \U0001f308",
                "olha esse charme bem delicadinho \U0001f979",
                "pequeno destaque que muda tudo \u2728",
                "bem bobinha mas ficou fofa \U0001f495",
            ],
            seed_text,
        )
    if is_encomenda:
        return choose_variant(
            [
                "mais uma encomenda linda por aqui \U0001f495",
                "feito com carinho pra encantar \u2728",
                "esses detalhes fazem toda diferen\u00e7a \U0001f979",
                "legendinha curta s\u00f3 pra dar destaque \U0001f495",
            ],
            seed_text,
        )
    return choose_variant(
        [
            "olha essa delicadeza \u2728",
            "bem pequenininho e cheio de charme \U0001f495",
            "s\u00f3 pra dar aquele destaque \U0001f979",
            "uma bobinha s\u00f3 pra destacar \u2728",
        ],
        seed_text,
    )


def caption_for_post(source_label: str, media_count: int, is_encomenda: bool, tags: set[str], schedule_slot: str, seed_text: str) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return choose_variant(
                [
                    "Passando pra mostrar uma encomenda cheia de detalhes lindos. Esses modelinhos ficam perfeitos para valorizar ainda mais suas produções 💖",
                    "Esses modelinhos foram juntos para uma encomenda especial e o resultado ficou um encanto. Perfeito para deixar a produção ainda mais delicada ✨",
                    "Tem encomenda que merece aparecer por aqui, e essa é uma delas. Vários detalhes lindos para inspirar produções cheias de carinho 🌸",
                ],
                seed_text,
            )
        if "fofo" in tags:
            return choose_variant(
                [
                    "Quando os modelinhos conversam entre si, a produção fica ainda mais encantadora. Ótima inspiração para quem ama variedade com delicadeza ✨",
                    "Esses modelinhos juntos deixam qualquer produção com mais personalidade. Uma combinação linda para encantar nas encomendas 💕",
                    "Separei esses modelinhos porque a combinação deles ficou uma graça. Perfeito para quem gosta de variar sem perder delicadeza 🥹",
                ],
                seed_text,
            )
        return choose_variant(
            [
                "Separei esses modelinhos juntos porque eles combinam super bem entre si. Perfeito para compor produções cheias de personalidade 🌸",
                "Quando a gente junta modelinhos que conversam entre si, a produção ganha outro charme. Uma ótima inspiração para encomendas delicadas ✨",
                "Essas combinações deixam a produção mais rica e mais bonita visualmente. Ideia linda para quem ama caprichar nos detalhes 💖",
            ],
            seed_text,
        )

    if "floral" in tags:
        return choose_variant(
            [
                "Esse modelinho floral é daquele tipo que deixa qualquer produção mais delicada. Uma graça para doces que pedem acabamento especial 🌸",
                "Detalhes florais sempre trazem um charme extra para a produção. Um modelinho lindo para quem ama delicadeza 🌼",
                "Tem modelinho que já transmite delicadeza só de olhar. Esse floral é perfeito para produções com toque mais romântico 🌸",
            ],
            seed_text,
        )
    if "laco" in tags:
        return choose_variant(
            [
                "Laço é aquele detalhe que transforma a produção e deixa tudo com mais charme. Perfeito para encomendas delicadas e cheias de carinho 🎀",
                "Esse modelinho com laço é uma graça para deixar a produção mais delicada e com acabamento encantador 🎀",
                "Tem detalhe que faz toda a diferença na produção, e o laço é um deles. Fica lindo em encomendas fofas e caprichadas 💖",
            ],
            seed_text,
        )
    if "arco" in tags:
        return choose_variant(
            [
                "Tem modelinho que já chama atenção só de bater o olho, e esse é um deles. Lindo para produções alegres e cheias de encanto 🌈",
                "Esse modelinho traz um ar alegre e delicado para a produção. Uma graça para doces com proposta mais leve e encantadora ✨",
                "Quando a ideia é deixar a produção mais fofa e marcante, esse tipo de modelinho faz toda diferença 🌈",
            ],
            seed_text,
        )
    if "fruta" in tags:
        return choose_variant(
            [
                "Os detalhes pequenos fazem toda diferença no resultado final. Esse modelinho é uma graça para deixar a produção ainda mais especial 🍒",
                "Um detalhezinho assim já muda a cara da produção e deixa tudo mais encantador. Lindo para doces delicados 🍒",
                "Esse modelinho é daquele tipo que traz charme sem pesar. Ótimo para composições leves e cheias de carinho ✨",
            ],
            seed_text,
        )
    if schedule_slot == "manha":
        return choose_variant(
            [
                "Começando o dia com uma inspiração linda por aqui. Porque até os pequenos detalhes fazem diferença na hora de encantar 💕",
                "Bom dia com um modelinho que é pura delicadeza. Ideia linda para inspirar produções cheias de carinho ✨",
                "Passando cedo por aqui para deixar uma inspiração doce no feed. Pequenos detalhes fazem toda diferença 🥹",
            ],
            seed_text,
        )
    if is_encomenda:
        return choose_variant(
            [
                "Mais uma encomenda feita com carinho e pensada para deixar cada doce ainda mais especial. É esse tipo de detalhe que valoriza a produção ✨",
                "Essa peça entrou em uma encomenda linda por aqui e ficou um charme. Detalhes assim fazem a produção ganhar ainda mais valor 💖",
                "Passando pra mostrar mais um modelinho de encomenda que ficou uma graça. É esse cuidado nos detalhes que encanta o cliente final 🌸",
            ],
            seed_text,
        )
    return choose_variant(
        [
            "Olha só esse modelinho passando no feed. Ideal para quem ama produzir com mais personalidade e deixar cada doce ainda mais especial 💕",
            "Esse modelinho é uma inspiração linda para quem gosta de caprichar na produção e encantar nos detalhes ✨",
            "Tem peça que já chama atenção pela delicadeza. Essa é uma daquelas ideias que deixam a produção ainda mais bonita 🌸",
        ],
        seed_text,
    )


def media_kind(path: Path) -> str:
    return "video" if path.suffix.lower() in VIDEO_EXTENSIONS else "image"


def all_media_files(folder: Path) -> list[Path]:
    return sorted(
        [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS],
        key=lambda p: p.name.lower(),
    )


def safe_media_url(path: Path) -> str:
    relative = path.relative_to(ROOT_MEDIA_DIR).as_posix()
    return "/media?" + urllib.parse.urlencode({"path": relative})


def generate_posts() -> dict[str, object]:
    posts: list[dict[str, object]] = []
    post_index = 0

    root_files = all_media_files(ROOT_MEDIA_DIR)
    for media_path in root_files:
        slot, schedule_label = make_schedule(post_index)
        source_label = "pata3d_cortadores"
        is_encomenda = True
        tags = infer_tags_from_name(media_path.stem)
        posts.append(
            {
                "id": f"post-{post_index}",
                "title": title_for_post(media_path.stem, tags, 1),
                "post_type": "single",
                "post_type_label": "Post único",
                "preview_type": "feed",
                "schedule_slot": slot,
                "schedule_label": schedule_label,
                "overlay_text": overlay_for_context(slot, 1, is_encomenda, tags),
                "reel_overlay_text": reel_overlay_text(source_label, tags, is_encomenda, f"{media_path.stem}-{post_index}-reel"),
                "caption": caption_for_post(source_label, 1, is_encomenda, tags, slot, f"{media_path.stem}-{post_index}"),
                "hashtags": hashtags_for_text(source_label, is_encomenda),
                "source_label": source_label,
                "mock_likes": 108 + post_index * 13,
                "media": [
                    {
                        "name": media_path.name,
                        "kind": media_kind(media_path),
                        "preview_url": safe_media_url(media_path),
                    }
                ],
            }
        )
        post_index += 1

    for folder in sorted([path for path in ROOT_MEDIA_DIR.iterdir() if path.is_dir()], key=lambda p: p.name.lower()):
        media_files = all_media_files(folder)
        if not media_files:
            continue

        slot, schedule_label = make_schedule(post_index)
        source_label = folder.name
        is_encomenda = True
        tags = infer_tags_from_media(media_files)
        preview_type = "reel" if any(path.suffix.lower() in VIDEO_EXTENSIONS for path in media_files) else "feed"
        posts.append(
            {
                "id": f"post-{post_index}",
                "title": title_for_post(folder.name, tags, len(media_files)),
                "post_type": "carousel" if len(media_files) > 1 else "single",
                "post_type_label": "Carrossel" if len(media_files) > 1 else "Post único",
                "preview_type": preview_type,
                "schedule_slot": slot,
                "schedule_label": schedule_label,
                "overlay_text": overlay_for_context(slot, len(media_files), is_encomenda, tags),
                "reel_overlay_text": reel_overlay_text(source_label, tags, is_encomenda, f"{folder.name}-{post_index}-reel"),
                "caption": caption_for_post(source_label, len(media_files), is_encomenda, tags, slot, f"{folder.name}-{post_index}"),
                "hashtags": hashtags_for_text(source_label, is_encomenda),
                "source_label": source_label,
                "mock_likes": 172 + post_index * 17,
                "media": [
                    {
                        "name": path.name,
                        "kind": media_kind(path),
                        "preview_url": safe_media_url(path),
                    }
                    for path in media_files
                ],
            }
        )
        post_index += 1

    preview_posts = list(posts)
    extra_reels: list[dict[str, object]] = []
    reel_candidates = preview_posts[:]
    for source_post in reel_candidates:
        if len(extra_reels) >= 8:
            break
        if not source_post["media"]:
            continue
        first_media = source_post["media"][0]
        reel_id = f"{source_post['id']}-reel"
        extra_reels.append(
            {
                "id": reel_id,
                "title": f"Reel • {source_post['title']}",
                "post_type": "reel_mock",
                "post_type_label": "Reel de teste",
                "preview_type": "reel",
                "schedule_slot": source_post["schedule_slot"],
                "schedule_label": source_post["schedule_label"],
                "overlay_text": source_post["overlay_text"],
                "reel_overlay_text": source_post.get("reel_overlay_text", source_post["overlay_text"]),
                "caption": source_post["caption"],
                "hashtags": source_post["hashtags"],
                "source_label": source_post["source_label"],
                "mock_likes": source_post["mock_likes"],
                "media": [first_media],
            }
        )

    posts.extend(extra_reels)

    return {
        "profile": "@pata3d",
        "posts": posts,
    }


def _previewify_payload(payload: dict[str, object]) -> dict[str, object]:
    preview_posts: list[dict[str, object]] = []
    for post in payload.get("posts", []):
        post_copy = dict(post)
        preview_media = []
        for media in post.get("media", []):
            media_copy = dict(media)
            relative = media_copy.pop("relative_path", "")
            media_copy["preview_url"] = "/media?" + urllib.parse.urlencode({"path": relative})
            preview_media.append(media_copy)
        post_copy["media"] = preview_media
        preview_posts.append(post_copy)

    return {
        "profile": payload.get("profile", "@pata3d"),
        "root_media_dir": payload.get("root_media_dir", str(ROOT_MEDIA_DIR)),
        "posts": preview_posts,
    }


def generate_posts() -> dict[str, object]:
    return _previewify_payload(build_draft_payload(ROOT_MEDIA_DIR))


class PreviewHandler(BaseHTTPRequestHandler):
    server_version = "Pata3DPreview/1.0"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        route = posixpath.normpath(parsed.path)
        params = urllib.parse.parse_qs(parsed.query)

        if route == "/media":
            self.handle_media(params)
            return
        if route == "/raw-data":
            self.handle_raw_data()
            return
        if route == "/refresh":
            self.redirect("/")
            return
        if route in {"/", "."}:
            self.handle_index()
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Rota não encontrada.")

    def handle_index(self) -> None:
        payload = generate_posts()
        page_html = (
            HTML_TEMPLATE
            .replace("__ROOT_MEDIA_DIR__", html.escape(str(ROOT_MEDIA_DIR)))
            .replace("__JSON_DATA__", json.dumps(payload, ensure_ascii=False))
        )
        page = page_html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def handle_raw_data(self) -> None:
        payload = json.dumps(generate_posts(), ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def handle_media(self, params: dict[str, list[str]]) -> None:
        relative = params.get("path", [""])[0].strip().replace("\\", "/").strip("/")
        media_path = (ROOT_MEDIA_DIR / relative).resolve()
        if ROOT_MEDIA_DIR != media_path and ROOT_MEDIA_DIR not in media_path.parents:
            self.send_error(HTTPStatus.BAD_REQUEST, "Caminho inválido.")
            return
        if not media_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo não encontrado.")
            return

        content_type = mimetypes.guess_type(media_path.name)[0] or "application/octet-stream"
        data = media_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stdout.write("[instagram-preview] " + fmt % args + "\n")


def main() -> None:
    ROOT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), PreviewHandler)
    print("=" * 72)
    print("Instagram Preview local iniciado.")
    print(f"Fonte de mídia: {ROOT_MEDIA_DIR}")
    print(f"Acesse: http://{HOST}:{PORT}")
    print("=" * 72)
    server.serve_forever()


if __name__ == "__main__":
    main()
