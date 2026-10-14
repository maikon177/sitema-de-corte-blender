import requests
import json
import os
from pathlib import Path
from datetime import datetime

GRAPH        = "https://graph.instagram.com/v21.0"
DADOS_PATH   = Path("dados/historico.json")

def _carregar_contas():
    contas = {}
    i = 1
    while os.getenv(f"IG_USER_ID_{i}") or os.getenv(f"IG_ACCESS_TOKEN_{i}"):
        contas[i] = {"user_id": os.getenv(f"IG_USER_ID_{i}", ""), "token": os.getenv(f"IG_ACCESS_TOKEN_{i}", "")}
        i += 1
    return contas

CONTAS = _carregar_contas()


def _token(conta: int) -> str:
    return CONTAS[conta]["token"]


def buscar_insights_post(media_id: str, conta: int = 1) -> dict:
    """Busca métricas de um post específico pelo media_id."""
    r = requests.get(
        f"{GRAPH}/{media_id}/insights",
        params={
            "metric":       "likes,reach,impressions,saved,comments,shares,profile_visits,follows",
            "access_token": _token(conta),
        },
        timeout=30,
    )
    dados = r.json().get("data", [])
    return {item["name"]: item["values"][0]["value"] for item in dados}


def buscar_insights_conta(conta: int = 1, periodo: str = "week") -> dict:
    """Busca métricas gerais do perfil (alcance, impressões, seguidores)."""
    uid = CONTAS[conta]["user_id"]
    r = requests.get(
        f"{GRAPH}/{uid}/insights",
        params={
            "metric":       "reach,impressions,profile_views,follower_count",
            "period":       periodo,
            "access_token": _token(conta),
        },
        timeout=30,
    )
    dados = r.json().get("data", [])
    return {item["name"]: item["values"][-1]["value"] for item in dados}


def salvar_historico(entrada: dict):
    """Adiciona um registro de post ao histórico local (JSON)."""
    DADOS_PATH.parent.mkdir(exist_ok=True)
    historico = carregar_historico()
    entrada["registrado_em"] = datetime.now().isoformat()
    historico.append(entrada)
    DADOS_PATH.write_text(json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8")


def carregar_historico() -> list[dict]:
    """Carrega histórico de posts do arquivo local."""
    if not DADOS_PATH.exists():
        return []
    return json.loads(DADOS_PATH.read_text(encoding="utf-8"))


def atualizar_metricas_historico(conta: int = 1):
    """
    Percorre o histórico e atualiza as métricas dos posts que ainda
    não têm dados (posts recentes podem demorar horas para ter insights).
    """
    historico = carregar_historico()
    atualizados = 0

    for post in historico:
        if post.get("conta") != conta:
            continue
        if post.get("reach", 0) > 0:
            continue   # já tem métricas, pula

        media_id = post.get("media_id_feed")
        if not media_id:
            continue

        try:
            metricas = buscar_insights_post(media_id, conta)
            post.update(metricas)
            atualizados += 1
            print(f"[metricas] Atualizado: {post.get('arquivo')} — alcance {metricas.get('reach', 0)}")
        except Exception as e:
            print(f"[metricas] Não foi possível buscar insights de {media_id}: {e}")

    if atualizados:
        DADOS_PATH.write_text(json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8")

    return historico


def imprimir_relatorio(conta: int = 1):
    """Imprime um relatório resumido no terminal."""
    historico = [p for p in carregar_historico() if p.get("conta") == conta]
    if not historico:
        print("[metricas] Nenhum post registrado ainda.")
        return historico

    print(f"\n{'='*55}")
    print(f"  RELATÓRIO — Conta {conta}")
    print(f"{'='*55}")
    for p in historico[-10:]:   # últimos 10
        print(
            f"  {p.get('arquivo','?'):30s} | "
            f"Alcance {p.get('reach',0):>5} | "
            f"❤ {p.get('likes',0):>4} | "
            f"🔖 {p.get('saved',0):>3} | "
            f"💬 {p.get('comments',0):>3}"
        )
    print(f"{'='*55}\n")
    return historico
