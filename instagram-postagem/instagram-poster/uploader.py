import requests
import base64
import os
from pathlib import Path

IMGBB_KEY = os.getenv("IMGBB_API_KEY", "")


def subir_imagem(caminho_local: str) -> str:
    """
    Faz upload de uma imagem para o ImgBB e retorna a URL pública HTTPS.
    A URL é necessária para a Instagram Graph API.
    """
    if not IMGBB_KEY:
        raise ValueError("IMGBB_API_KEY não definida no .env")

    with open(caminho_local, "rb") as f:
        imagem_b64 = base64.b64encode(f.read()).decode("utf-8")

    resposta = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key":    IMGBB_KEY,
            "image":  imagem_b64,
            "name":   Path(caminho_local).stem,
            "expiration": 600,   # URL expira em 10 min — suficiente para a API do Instagram processar
        },
        timeout=30,
    )

    dados = resposta.json()
    if not dados.get("success"):
        raise RuntimeError(f"ImgBB erro: {dados}")

    url = dados["data"]["url"]
    print(f"[uploader] Imagem online: {url}")
    return url
