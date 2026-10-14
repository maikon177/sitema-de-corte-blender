"""
Instagram Poster — ponto de entrada principal.

Uso:
  python main.py               → posta fotos novas de cada conta + atualiza métricas
  python main.py --so-analise  → só analisa métricas, sem postar
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from editor    import processar_para_feed, processar_para_stories
from uploader  import subir_imagem
from legenda   import gerar_legenda, avaliar_performance
from instagram import postar_feed, postar_stories
from rascunhos import save_draft_payload
from metricas  import (
    salvar_historico,
    atualizar_metricas_historico,
    imprimir_relatorio,
)

PASTA_FOTOS      = Path("fotos")
PASTA_PUBLICADAS = Path("publicadas")
EXTENSOES        = {".jpg", ".jpeg", ".png", ".webp"}
TMP_FEED         = Path("_tmp_feed.jpg")
TMP_STORIES      = Path("_tmp_stories.jpg")
PASTA_DADOS      = Path("dados")

# Configuração por conta — lê do .env (quantas contas houver: _1, _2, _3, ...)
def _carregar_contas():
    contas = {}
    i = 1
    while os.getenv(f"IG_PASTA_{i}") or os.getenv(f"IG_USER_ID_{i}"):
        contas[i] = {
            "pasta": os.getenv(f"IG_PASTA_{i}", f"conta{i}"),
            "nicho": os.getenv(f"IG_NICHO_{i}", "lifestyle"),
        }
        i += 1
    if not contas:
        contas[1] = {"pasta": os.getenv("IG_PASTA_1", "conta1"), "nicho": os.getenv("IG_NICHO_1", "lifestyle")}
    return contas

CONTAS = _carregar_contas()
CONTAS_ATIVAS = [int(x) for x in os.getenv("CONTAS_ATIVAS", "1").split(",") if x.strip()]


def _limpar_tmp():
    for f in [TMP_FEED, TMP_STORIES]:
        if f.exists():
            f.unlink()


def postar_foto(foto: Path, conta: int, nicho: str):
    print(f"\n[main] Conta {conta} — processando: {foto.name}")

    # 1. Editar imagem
    processar_para_feed(str(foto), str(TMP_FEED))
    processar_para_stories(str(foto), str(TMP_STORIES))

    # 2. Gerar legenda analisando a imagem editada (feed)
    legenda = gerar_legenda(foto.stem, contexto_extra=nicho, caminho_imagem=str(TMP_FEED))

    # 3. Subir imagens
    url_feed    = subir_imagem(str(TMP_FEED))
    url_stories = subir_imagem(str(TMP_STORIES))

    # 4. Postar
    try:
        media_id_feed    = postar_feed(url_feed, legenda, conta)
        media_id_stories = postar_stories(url_stories, conta)

        salvar_historico({
            "arquivo":          foto.name,
            "conta":            conta,
            "nicho":            nicho,
            "legenda":          legenda,
            "media_id_feed":    media_id_feed,
            "media_id_stories": media_id_stories,
            "reach":            0,
            "likes":            0,
            "saved":            0,
            "comments":         0,
            "shares":           0,
        })
    except Exception as e:
        print(f"[main] ERRO ao postar conta {conta}: {e}")
        return

    # 5. Mover foto para publicadas/nome_da_pasta/
    destino_dir = PASTA_PUBLICADAS / CONTAS[conta]["pasta"]
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / foto.name
    if destino.exists():
        destino = destino_dir / f"{foto.stem}_2{foto.suffix}"
    foto.rename(destino)
    print(f"[main] Foto movida para publicadas/{CONTAS[conta]['pasta']}/")


def modo_postar():
    alguma_foto = False

    for numero, cfg in CONTAS.items():
        if numero not in CONTAS_ATIVAS:
            continue

        pasta_conta = PASTA_FOTOS / cfg["pasta"]
        if not pasta_conta.exists():
            print(f"[main] Pasta não encontrada: {pasta_conta} — criando...")
            pasta_conta.mkdir(parents=True, exist_ok=True)
            continue

        fotos = sorted([f for f in pasta_conta.iterdir() if f.suffix.lower() in EXTENSOES])
        if not fotos:
            print(f"[main] Nenhuma foto em {pasta_conta}")
            continue

        alguma_foto = True
        foto = fotos[0]  # 1 foto por execução
        print(f"\n[main] {len(fotos)} foto(s) em fila. Postando: {foto.name}")

        try:
            postar_foto(foto, numero, cfg["nicho"])
        except Exception as e:
            print(f"[main] ERRO em {foto.name}: {e}")
        finally:
            _limpar_tmp()

    if not alguma_foto:
        print("\n[main] Nenhuma foto encontrada.")
        print(f"[main] Coloque fotos nas pastas:")
        for numero, cfg in CONTAS.items():
            if numero in CONTAS_ATIVAS:
                print(f"       fotos/{cfg['pasta']}/")
        return

    # Atualiza métricas dos posts anteriores
    print("\n[main] Atualizando métricas de posts anteriores...")
    for numero in CONTAS_ATIVAS:
        atualizar_metricas_historico(numero)
        imprimir_relatorio(numero)


def modo_analise():
    print("\n[main] ===== MODO ANÁLISE =====")
    for numero in CONTAS_ATIVAS:
        cfg = CONTAS[numero]
        print(f"\n[main] Conta {numero} — {cfg['pasta']}")
        historico = atualizar_metricas_historico(numero)
        imprimir_relatorio(numero)

        posts_da_conta = [p for p in historico if p.get("conta") == numero]
        if posts_da_conta:
            print("\n[main] Análise da IA:\n")
            print(avaliar_performance(posts_da_conta))


def modo_gerar_rascunhos():
    print("\n[main] ===== MODO RASCUNHOS =====")
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)

    gerou_algum = False
    for numero, cfg in CONTAS.items():
        if numero not in CONTAS_ATIVAS:
            continue

        pasta_conta = PASTA_FOTOS / cfg["pasta"]
        if not pasta_conta.exists():
            print(f"[main] Pasta nÃ£o encontrada para rascunhos: {pasta_conta}")
            continue

        arquivo_saida = PASTA_DADOS / f"rascunhos_{cfg['pasta']}.json"
        save_draft_payload(pasta_conta, arquivo_saida, profile="@pata3d")
        gerou_algum = True
        print(f"[main] Rascunhos salvos: {arquivo_saida}")

    if not gerou_algum:
        print("[main] Nenhuma pasta ativa disponÃ­vel para gerar rascunhos.")


if __name__ == "__main__":
    PASTA_FOTOS.mkdir(exist_ok=True)

    if "--gerar-rascunhos" in sys.argv:
        modo_gerar_rascunhos()
    elif "--so-analise" in sys.argv:
        modo_analise()
    else:
        modo_postar()
