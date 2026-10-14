from __future__ import annotations

import cgi
import html
import json
import mimetypes
import os
import posixpath
import socket
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from string import Template


ROOT_DIR = Path(r"D:\intagram postagem\instagram-poster\fotos").resolve()
HOST = "0.0.0.0"
PORT = 8765
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


PAGE_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Galeria Local Pata3D</title>
  <style>
    :root {
      --bg: #fff9f5;
      --panel: rgba(255,255,255,0.86);
      --line: #ead8cd;
      --text: #503236;
      --muted: #866a68;
      --accent: #ef8fa7;
      --accent-2: #9dcfe5;
      --accent-3: #f6d98d;
      --danger: #ca4b62;
      --shadow: 0 18px 40px rgba(113, 72, 57, 0.12);
      --radius: 24px;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(255, 215, 230, 0.9), transparent 30%),
        radial-gradient(circle at top right, rgba(181, 230, 247, 0.9), transparent 24%),
        linear-gradient(180deg, #fffdf9 0%, #fff6ef 100%);
      min-height: 100vh;
    }

    .shell {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 24px;
      padding: 24px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid rgba(255,255,255,0.8);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
    }

    .sidebar {
      padding: 22px;
      position: sticky;
      top: 24px;
      align-self: start;
    }

    h1, h2, h3, p { margin-top: 0; }
    h1 { font-size: 1.55rem; margin-bottom: 6px; }
    h2 { font-size: 1.02rem; margin-bottom: 10px; }
    .muted { color: var(--muted); }
    .small { font-size: 0.9rem; }

    .folder-list {
      display: grid;
      gap: 8px;
      margin: 18px 0 22px;
    }

    .folder-link {
      display: block;
      padding: 12px 14px;
      border-radius: 16px;
      text-decoration: none;
      color: var(--text);
      background: rgba(255,255,255,0.7);
      border: 1px solid transparent;
    }

    .folder-link.active {
      background: linear-gradient(135deg, rgba(239,143,167,0.2), rgba(157,207,229,0.2));
      border-color: rgba(239,143,167,0.4);
      font-weight: 700;
    }

    .main {
      display: grid;
      gap: 20px;
      align-content: start;
    }

    .hero {
      padding: 24px;
    }

    .hero-row {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }

    .pills {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }

    .pill {
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,0.78);
      border: 1px solid var(--line);
      font-size: 0.92rem;
    }

    .upload-card, .gallery-card {
      padding: 22px;
    }

    .upload-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 14px;
      align-items: end;
    }

    label {
      display: block;
      font-weight: 600;
      margin-bottom: 8px;
    }

    input[type="text"], select, input[type="file"] {
      width: 100%;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.85);
      color: var(--text);
    }

    button, .button-link {
      border: 0;
      border-radius: 16px;
      padding: 12px 16px;
      font-weight: 700;
      cursor: pointer;
      color: white;
      background: linear-gradient(135deg, var(--accent), #d96fa3);
      text-decoration: none;
    }

    button.secondary {
      background: linear-gradient(135deg, var(--accent-2), #7bb3d0);
    }

    button.danger {
      background: linear-gradient(135deg, var(--danger), #a53854);
    }

    .message {
      margin-top: 14px;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(255,255,255,0.76);
      border: 1px solid var(--line);
    }

    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 18px;
      margin-top: 18px;
    }

    .media-card {
      background: rgba(255,255,255,0.85);
      border: 1px solid rgba(255,255,255,0.9);
      border-radius: 22px;
      overflow: hidden;
      box-shadow: 0 12px 28px rgba(113, 72, 57, 0.08);
    }

    .thumb-wrap {
      aspect-ratio: 1 / 1;
      background: linear-gradient(180deg, rgba(157,207,229,0.18), rgba(239,143,167,0.14));
      display: grid;
      place-items: center;
      overflow: hidden;
    }

    .thumb-wrap img, .thumb-wrap video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .media-body {
      padding: 14px;
      display: grid;
      gap: 12px;
    }

    .media-name {
      font-weight: 700;
      word-break: break-word;
    }

    .media-meta {
      color: var(--muted);
      font-size: 0.88rem;
    }

    .actions {
      display: grid;
      gap: 10px;
    }

    .action-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
    }

    .empty {
      padding: 28px;
      border: 1px dashed var(--line);
      border-radius: 20px;
      text-align: center;
      color: var(--muted);
      background: rgba(255,255,255,0.55);
    }

    @media (max-width: 900px) {
      .shell {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: static;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="panel sidebar">
      <h1>Galeria Local</h1>
      <p class="muted small">Envie fotos do celular para o PC pela rede local e gerencie por pasta.</p>
      <div class="folder-list">
        $folder_links
      </div>
      <p class="small muted">Pasta base:</p>
      <p class="small"><code>$root_dir</code></p>
    </aside>

    <main class="main">
      <section class="panel hero">
        <div class="hero-row">
          <div>
            <h2>Pasta atual: $current_folder_label</h2>
            <p class="muted">Acesso do celular: <strong>$server_hint</strong></p>
          </div>
          <div class="pills">
            <span class="pill">$media_count midias</span>
            <span class="pill">$folder_count pastas</span>
          </div>
        </div>
        $message_html
      </section>

      <section class="panel upload-card">
        <h2>Enviar do celular</h2>
        <form method="post" action="/upload" enctype="multipart/form-data">
          <input type="hidden" name="current_folder" value="$current_folder">
          <div class="upload-grid">
            <div>
              <label for="files">Fotos ou videos</label>
              <input id="files" type="file" name="files" accept="image/*,video/*" multiple>
            </div>
            <div>
              <label for="target_folder">Pasta destino</label>
              <select id="target_folder" name="target_folder">
                $folder_options
              </select>
            </div>
            <div>
              <label for="new_folder">Ou crie uma nova pasta</label>
              <input id="new_folder" type="text" name="new_folder" placeholder="Ex.: pata3d_junina">
            </div>
            <div>
              <button type="submit">Enviar para o PC</button>
            </div>
          </div>
        </form>
      </section>

      <section class="panel gallery-card">
        <h2>Galeria / Gerenciador</h2>
        $gallery_html
      </section>
    </main>
  </div>
</body>
</html>
"""
)


def format_bytes(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{num} B"


def guess_local_ips() -> list[str]:
    ips: list[str] = []
    hostname = socket.gethostname()
    try:
        candidates = socket.gethostbyname_ex(hostname)[2]
    except OSError:
        candidates = []

    for ip in candidates:
        if ip.startswith("127."):
            continue
        if ip not in ips:
            ips.append(ip)
    return ips


def ensure_unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def sanitize_segment(segment: str) -> str:
    cleaned = "".join(ch for ch in segment.strip() if ch not in '<>:"|?*')
    cleaned = cleaned.replace("/", "_").replace("\\", "_")
    return cleaned.strip(" .")


def safe_folder_from_relative(relative: str) -> Path:
    relative = relative.strip().replace("\\", "/").strip("/")
    if not relative:
        return ROOT_DIR

    candidate = (ROOT_DIR / relative).resolve()
    if ROOT_DIR != candidate and ROOT_DIR not in candidate.parents:
        raise ValueError("Pasta fora da base permitida.")
    return candidate


def relative_to_root(path: Path) -> str:
    try:
        return path.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return ""


def list_all_folders() -> list[Path]:
    folders = [ROOT_DIR]
    for path in sorted(ROOT_DIR.rglob("*")):
        if path.is_dir():
            folders.append(path)
    return folders


def list_media(folder: Path) -> list[Path]:
    items = [
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS
    ]
    return sorted(items, key=lambda p: p.stat().st_mtime, reverse=True)


def media_item_payload(media_path: Path) -> dict[str, object]:
    rel_path = relative_to_root(media_path)
    suffix = media_path.suffix.lower()
    return {
        "name": media_path.name,
        "relativePath": rel_path,
        "folder": relative_to_root(media_path.parent),
        "type": "video" if suffix in VIDEO_EXTENSIONS else "image",
        "sizeBytes": media_path.stat().st_size,
        "mediaUrl": "/media?" + urllib.parse.urlencode({"path": rel_path}),
    }


def build_folder_links(current_relative: str) -> str:
    blocks = []
    for folder in list_all_folders():
        rel = relative_to_root(folder)
        label = rel or "raiz"
        active_class = " active" if rel == current_relative else ""
        href = "/?" + urllib.parse.urlencode({"folder": rel}) if rel else "/"
        blocks.append(
            f'<a class="folder-link{active_class}" href="{href}">{html.escape(label)}</a>'
        )
    return "\n".join(blocks)


def build_folder_options(selected_relative: str) -> str:
    options = []
    for folder in list_all_folders():
        rel = relative_to_root(folder)
        label = rel or "raiz"
        selected = " selected" if rel == selected_relative else ""
        options.append(
            f'<option value="{html.escape(rel)}"{selected}>{html.escape(label)}</option>'
        )
    return "\n".join(options)


def media_preview_tag(media_path: Path) -> str:
    rel_path = relative_to_root(media_path)
    media_url = "/media?" + urllib.parse.urlencode({"path": rel_path})
    if media_path.suffix.lower() in VIDEO_EXTENSIONS:
        return f'<video src="{media_url}" controls muted playsinline preload="metadata"></video>'
    return f'<img src="{media_url}" alt="{html.escape(media_path.name)}" loading="lazy">'


def build_gallery(folder: Path, current_relative: str) -> str:
    media_items = list_media(folder)
    if not media_items:
        return '<div class="empty">Nenhuma mídia nesta pasta ainda.</div>'

    cards = []
    folder_options = build_folder_options(current_relative)
    for media in media_items:
        rel = relative_to_root(media)
        preview = media_preview_tag(media)
        name = html.escape(media.name)
        meta = f"{format_bytes(media.stat().st_size)}"
        cards.append(
            f"""
            <article class="media-card">
              <div class="thumb-wrap">{preview}</div>
              <div class="media-body">
                <div>
                  <div class="media-name">{name}</div>
                  <div class="media-meta">{meta}</div>
                </div>
                <div class="actions">
                  <form method="post" action="/move">
                    <input type="hidden" name="media_path" value="{html.escape(rel)}">
                    <input type="hidden" name="current_folder" value="{html.escape(current_relative)}">
                    <div class="action-row">
                      <select name="destination_folder">{folder_options}</select>
                      <button class="secondary" type="submit">Mover</button>
                    </div>
                  </form>
                  <form method="post" action="/delete" onsubmit="return confirm('Excluir esta mídia?');">
                    <input type="hidden" name="media_path" value="{html.escape(rel)}">
                    <input type="hidden" name="current_folder" value="{html.escape(current_relative)}">
                    <button class="danger" type="submit">Excluir</button>
                  </form>
                </div>
              </div>
            </article>
            """
        )
    return '<div class="gallery-grid">' + "".join(cards) + "</div>"


class GalleryHandler(BaseHTTPRequestHandler):
    server_version = "Pata3DLocalGallery/1.0"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        route = posixpath.normpath(parsed.path)
        params = urllib.parse.parse_qs(parsed.query)

        if route == "/api/folders":
            self.handle_api_folders()
            return

        if route == "/api/media":
            self.handle_api_media(params)
            return

        if route == "/media":
            self.handle_media(params)
            return

        if route == "/" or route == ".":
            self.handle_index(params)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Rota não encontrada.")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        route = posixpath.normpath(parsed.path)

        if route == "/upload":
            self.handle_upload()
            return

        if route == "/move":
            self.handle_move()
            return

        if route == "/delete":
            self.handle_delete()
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Rota não encontrada.")

    def handle_index(self, params: dict[str, list[str]]) -> None:
        relative = params.get("folder", [""])[0]
        message = params.get("msg", [""])[0]
        try:
            current_folder = safe_folder_from_relative(relative)
        except ValueError:
            current_folder = ROOT_DIR
            relative = ""
            message = "Pasta inválida. Mostrando a raiz."

        media_items = list_media(current_folder)
        folder_links = build_folder_links(relative)
        folder_options = build_folder_options(relative)
        message_html = (
            f'<div class="message">{html.escape(message)}</div>' if message else ""
        )
        gallery_html = build_gallery(current_folder, relative)
        ips = guess_local_ips()
        server_hint = f"http://{ips[0] if ips else 'IP_DO_PC'}:{PORT}" if ips else f"http://IP_DO_PC:{PORT}"

        page = PAGE_TEMPLATE.substitute(
            folder_links=folder_links,
            root_dir=html.escape(str(ROOT_DIR)),
            current_folder_label=html.escape(relative or "raiz"),
            server_hint=html.escape(server_hint),
            media_count=str(len(media_items)),
            folder_count=str(len(list_all_folders())),
            message_html=message_html,
            current_folder=html.escape(relative),
            folder_options=folder_options,
            gallery_html=gallery_html,
        ).encode("utf-8")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def send_json(self, payload: dict[str, object] | list[object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_api_folders(self) -> None:
        payload = []
        for folder in list_all_folders():
            relative = relative_to_root(folder)
            payload.append(
                {
                    "name": relative or "raiz",
                    "relativePath": relative,
                    "mediaCount": len(list_media(folder)),
                }
            )
        self.send_json(
            {
                "rootDir": str(ROOT_DIR),
                "folders": payload,
            }
        )

    def handle_api_media(self, params: dict[str, list[str]]) -> None:
        relative = params.get("folder", [""])[0]
        try:
            folder = safe_folder_from_relative(relative)
        except ValueError:
            self.send_json({"error": "Pasta inválida."}, status=400)
            return

        if not folder.exists() or not folder.is_dir():
            self.send_json({"error": "Pasta não encontrada."}, status=404)
            return

        items = [media_item_payload(path) for path in list_media(folder)]
        self.send_json(
            {
                "folder": relative,
                "items": items,
            }
        )

    def handle_media(self, params: dict[str, list[str]]) -> None:
        relative = params.get("path", [""])[0]
        try:
            media_path = safe_folder_from_relative(relative)
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Caminho inválido.")
            return

        if not media_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Arquivo não encontrado.")
            return

        content_type = mimetypes.guess_type(media_path.name)[0] or "application/octet-stream"
        try:
            data = media_path.read_bytes()
        except OSError as exc:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Erro lendo arquivo: {exc}")
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def parse_multipart(self) -> cgi.FieldStorage:
        environ = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": self.headers.get("Content-Type", ""),
        }
        return cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ=environ,
            keep_blank_values=True,
        )

    def parse_urlencoded(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(raw, keep_blank_values=True)
        return {key: values[0] for key, values in parsed.items()}

    def redirect_with_message(self, folder: str, message: str) -> None:
        query = {"msg": message}
        if folder:
            query["folder"] = folder
        location = "/?" + urllib.parse.urlencode(query)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def resolve_target_folder(self, selected_folder: str, new_folder: str) -> tuple[Path, str]:
        if new_folder.strip():
            pieces = [sanitize_segment(piece) for piece in new_folder.replace("\\", "/").split("/")]
            pieces = [piece for piece in pieces if piece]
            if not pieces:
                raise ValueError("Nome da nova pasta inválido.")
            relative = "/".join(pieces)
            target = safe_folder_from_relative(relative)
            target.mkdir(parents=True, exist_ok=True)
            return target, relative

        target = safe_folder_from_relative(selected_folder)
        target.mkdir(parents=True, exist_ok=True)
        return target, selected_folder.strip().replace("\\", "/").strip("/")

    def handle_upload(self) -> None:
        form = self.parse_multipart()
        current_folder = form.getfirst("current_folder", "")
        selected_folder = form.getfirst("target_folder", "")
        new_folder = form.getfirst("new_folder", "")
        try:
            target_folder, target_relative = self.resolve_target_folder(selected_folder, new_folder)
        except ValueError as exc:
            self.redirect_with_message(current_folder, str(exc))
            return

        uploaded = form["files"] if "files" in form else []
        if not isinstance(uploaded, list):
            uploaded = [uploaded]

        saved = 0
        for item in uploaded:
            filename = sanitize_segment(Path(item.filename or "").name)
            if not filename:
                continue
            suffix = Path(filename).suffix.lower()
            if suffix not in MEDIA_EXTENSIONS:
                continue

            destination = ensure_unique_path(target_folder / filename)
            with destination.open("wb") as handle:
                data = item.file.read()
                handle.write(data)
            saved += 1

        accepts_json = "application/json" in (self.headers.get("Accept", "") or "")
        if saved == 0:
            if accepts_json:
                self.send_json({"ok": False, "message": "Nenhum arquivo válido foi enviado."}, status=400)
                return
            self.redirect_with_message(current_folder, "Nenhum arquivo válido foi enviado.")
            return

        if accepts_json:
            self.send_json(
                {
                    "ok": True,
                    "savedCount": saved,
                    "folder": target_relative,
                    "message": f"{saved} arquivo(s) enviado(s) com sucesso.",
                }
            )
            return

        self.redirect_with_message(target_relative, f"{saved} arquivo(s) enviado(s) com sucesso.")

    def handle_move(self) -> None:
        data = self.parse_urlencoded()
        current_folder = data.get("current_folder", "")
        media_path = data.get("media_path", "")
        destination_folder = data.get("destination_folder", "")

        try:
            source = safe_folder_from_relative(media_path)
            destination_dir = safe_folder_from_relative(destination_folder)
        except ValueError as exc:
            self.redirect_with_message(current_folder, str(exc))
            return

        if not source.is_file():
            self.redirect_with_message(current_folder, "Arquivo não encontrado para mover.")
            return

        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = ensure_unique_path(destination_dir / source.name)
        source.rename(destination)
        self.redirect_with_message(destination_folder, f"{source.name} movido com sucesso.")

    def handle_delete(self) -> None:
        data = self.parse_urlencoded()
        current_folder = data.get("current_folder", "")
        media_path = data.get("media_path", "")

        try:
            source = safe_folder_from_relative(media_path)
        except ValueError as exc:
            self.redirect_with_message(current_folder, str(exc))
            return

        if not source.is_file():
            self.redirect_with_message(current_folder, "Arquivo não encontrado para excluir.")
            return

        name = source.name
        source.unlink()
        self.redirect_with_message(current_folder, f"{name} excluído com sucesso.")

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stdout.write("[galeria-local] " + fmt % args + "\n")


def main() -> None:
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), GalleryHandler)
    ips = guess_local_ips()

    print("=" * 72)
    print("Galeria local da Pata3D iniciada.")
    print(f"Pasta base: {ROOT_DIR}")
    print(f"No PC: http://127.0.0.1:{PORT}")
    for ip in ips:
        print(f"No celular: http://{ip}:{PORT}")
    if not ips:
        print(f"No celular: http://IP_DO_PC:{PORT}")
    print("=" * 72)
    print("Use Ctrl+C para encerrar.")
    server.serve_forever()


if __name__ == "__main__":
    main()
