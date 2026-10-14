import requests
import os
import time

GRAPH = "https://graph.instagram.com/v21.0"

def _carregar_contas():
    contas = {}
    i = 1
    while os.getenv(f"IG_USER_ID_{i}") or os.getenv(f"IG_ACCESS_TOKEN_{i}"):
        contas[i] = {
            "user_id": os.getenv(f"IG_USER_ID_{i}", ""),
            "token":   os.getenv(f"IG_ACCESS_TOKEN_{i}", ""),
        }
        i += 1
    return contas

CONTAS = _carregar_contas()


def _conta(numero: int) -> tuple[str, str]:
    c = CONTAS.get(numero, {})
    uid   = c.get("user_id", "")
    token = c.get("token", "")
    if not uid or not token:
        raise ValueError(f"Credenciais da conta {numero} não configuradas no .env")
    return uid, token


def _criar_container(uid: str, token: str, url_imagem: str,
                     legenda: str, tipo: str) -> str:
    params: dict = {"image_url": url_imagem, "access_token": token}
    if tipo == "stories":
        params["media_type"] = "STORIES"
    else:
        params["caption"] = legenda

    r = requests.post(f"{GRAPH}/{uid}/media", params=params, timeout=30)
    dados = r.json()
    if "id" not in dados:
        raise RuntimeError(f"Erro ao criar container ({tipo}): {dados}")
    return dados["id"]


def _publicar_container(uid: str, token: str, creation_id: str) -> str:
    r = requests.post(
        f"{GRAPH}/{uid}/media_publish",
        params={"creation_id": creation_id, "access_token": token},
        timeout=30,
    )
    dados = r.json()
    if "id" not in dados:
        raise RuntimeError(f"Erro ao publicar container: {dados}")
    return dados["id"]


def postar_feed(url_imagem: str, legenda: str, conta: int = 1) -> str:
    """Posta no feed. Retorna o media_id para buscar métricas depois."""
    uid, token = _conta(conta)
    cid        = _criar_container(uid, token, url_imagem, legenda, "feed")
    time.sleep(3)   # Instagram pede uma pausa entre criar e publicar
    media_id   = _publicar_container(uid, token, cid)
    print(f"[instagram] Feed postado (conta {conta}) — media_id: {media_id}")
    return media_id


def postar_stories(url_imagem: str, conta: int = 1) -> str:
    """Posta nos stories. Retorna o media_id."""
    uid, token = _conta(conta)
    cid        = _criar_container(uid, token, url_imagem, "", "stories")
    time.sleep(3)
    media_id   = _publicar_container(uid, token, cid)
    print(f"[instagram] Stories postado (conta {conta}) — media_id: {media_id}")
    return media_id


def buscar_posts_recentes(conta: int = 1, limite: int = 10) -> list[dict]:
    """Retorna lista de posts recentes com id e timestamp."""
    uid, token = _conta(conta)
    r = requests.get(
        f"{GRAPH}/{uid}/media",
        params={
            "fields":       "id,timestamp,media_type,permalink",
            "limit":        limite,
            "access_token": token,
        },
        timeout=30,
    )
    return r.json().get("data", [])
