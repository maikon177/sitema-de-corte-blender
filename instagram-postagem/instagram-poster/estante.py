"""
Pipeline da Estante Imaginária: imagem 2D (personagem/desenho) -> estátua 3D colecionável.
Usa o Gemini (modelo de imagem) com a imagem de referência + o prompt de dados/prompt_estante.txt.
NÃO posta nada — só gera o arquivo de saída.
"""
import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
PROMPT_PATH = BASE / "dados" / "prompt_estante.txt"

# modelo de geração de imagem do Gemini (editável via .env)
# gemini-3-pro-image = "Nano Banana Pro" (alta qualidade). Flash é mais fraco/barato.
MODELO_IMAGEM = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image")

# Qwen (Token Plan) — imagem é assíncrona no endpoint dedicado.
QWEN_BASE = "https://token-plan.maas.qwencloudapi.com"
QWEN_MODELO = os.getenv("QWEN_IMAGE_MODEL", "qwen-image-3.0-pro")
NEGATIVO = "flat 2d drawing, illustration, cropped, half body cut off"


def carregar_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8").strip()
    return "Create a physical 3D collectible resin statue of the character in the reference image."


def _mime(caminho: str) -> str:
    c = caminho.lower()
    if c.endswith(".png"):
        return "image/png"
    if c.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def gerar_3d(caminho_ref: str, destino: str, prompt: str | None = None,
             modelo: str | None = None) -> str:
    """Gera a versão 3D da imagem de referência e salva em `destino`. Retorna o caminho."""
    prompt = prompt or carregar_prompt()
    cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    img_bytes = Path(caminho_ref).read_bytes()

    resposta = cliente.models.generate_content(
        model=modelo or MODELO_IMAGEM,
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type=_mime(caminho_ref)),
            prompt,
        ],
    )

    cand = (resposta.candidates or [None])[0]
    if not cand or not cand.content or not cand.content.parts:
        raise RuntimeError("Gemini não retornou conteúdo")

    for part in cand.content.parts:
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            out = Path(destino)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(inline.data)
            return str(out)

    # se não veio imagem, tenta mostrar o texto do modelo (ajuda a depurar)
    txts = [getattr(p, "text", "") for p in cand.content.parts if getattr(p, "text", "")]
    raise RuntimeError("Gemini não retornou imagem" + (f": {' '.join(txts)[:200]}" if txts else ""))


def gerar_qwen(caminho_ref: str, destino: str, prompt: str | None = None,
               modelo: str | None = None) -> str:
    """Gera via Qwen (qwen-image / wan), assíncrono. Precisa de QWEN_API_KEY + ImgBB."""
    prompt = prompt or carregar_prompt()
    key = os.getenv("QWEN_API_KEY", "").strip()
    if not key:
        raise RuntimeError("QWEN_API_KEY não está no .env")

    from uploader import subir_imagem
    ref_url = subir_imagem(caminho_ref)  # Qwen precisa de URL pública

    head = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    body = {
        "model": modelo or QWEN_MODELO,
        "input": {"messages": [{"role": "user", "content": [
            {"image": ref_url}, {"text": prompt},
        ]}]},
        "parameters": {"prompt_extend": True, "negative_prompt": NEGATIVO},
    }
    r = requests.post(f"{QWEN_BASE}/api/v1/services/aigc/image-generation/generation",
                      headers={**head, "X-DashScope-Async": "enable"},
                      data=json.dumps(body), timeout=60)
    j = r.json()
    task_id = (j.get("output") or {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"Qwen não criou tarefa: {j}")

    t0 = time.time()
    while True:
        tr = requests.get(f"{QWEN_BASE}/api/v1/tasks/{task_id}", headers=head, timeout=30).json()
        st = (tr.get("output") or {}).get("task_status")
        if st in ("SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN") or time.time() - t0 > 300:
            j = tr
            break
        time.sleep(5)

    urls = []
    def _achar(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("url", "image") and isinstance(v, str) and v.startswith("http"):
                    urls.append(v)
                else:
                    _achar(v)
        elif isinstance(o, list):
            for v in o:
                _achar(v)
    _achar(j)
    if not urls:
        raise RuntimeError(f"Qwen não retornou imagem: {str(j)[:300]}")

    out = Path(destino)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(requests.get(urls[0], timeout=120).content)
    return str(out)


# modelos de imagem permitidos (o app escolhe um destes)
MODELOS_GEMINI = ["gemini-3-pro-image", "gemini-3.1-flash-image",
                  "gemini-3.1-flash-lite-image", "gemini-2.5-flash-image"]
MODELOS_QWEN = ["qwen-image-3.0-pro", "wan2.7-image-pro", "wan2.7-image"]
MODELOS_OK = set(MODELOS_GEMINI + MODELOS_QWEN)


def gerar(caminho_ref: str, destino: str, engine: str = "gemini",
          prompt: str | None = None, tentativas: int = 3,
          modelo: str | None = None) -> str:
    """Gera a estátua 3D com retry.
    engine: 'gemini' ou 'qwen'. modelo: id específico (opcional, deve estar na lista)."""
    if modelo and modelo not in MODELOS_OK:
        raise RuntimeError(f"modelo não permitido: {modelo}")
    # deduz o engine pelo modelo, se possível
    if modelo in MODELOS_QWEN:
        engine = "qwen"
    elif modelo in MODELOS_GEMINI:
        engine = "gemini"

    def _call():
        if engine == "qwen":
            return gerar_qwen(caminho_ref, destino, prompt, modelo=modelo)
        return gerar_3d(caminho_ref, destino, prompt, modelo=modelo)

    ultimo = None
    for t in range(1, tentativas + 1):
        try:
            return _call()
        except Exception as e:
            ultimo = e
            print(f"[estante] {engine}/{modelo} tentativa {t} falhou: {str(e)[:100]}")
            time.sleep(3)
    raise RuntimeError(f"Falhou após {tentativas} tentativas: {ultimo}")


if __name__ == "__main__":
    import sys
    ref = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "saida_3d.png"
    eng = sys.argv[3] if len(sys.argv) > 3 else "gemini"
    print("engine:", eng, "modelo:", MODELO_IMAGEM if eng == "gemini" else QWEN_MODELO)
    print("gerado:", gerar(ref, dst, engine=eng))
