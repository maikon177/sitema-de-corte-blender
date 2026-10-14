"""
API do app Pata3D Studio — a ponte entre o celular (app) e o servidor.

Fase 1 (roda primeiro no PC, depois vai pra VPS):
  - serve o app (pasta pata3d-studio-recuperado)
  - POST /api/upload/<conta>          -> recebe fotos do app e salva na fila da conta
  - GET  /api/calendario?de=&ate=      -> o que vai ser postado em cada dia (gerado da fila)
  - POST /api/calendario/<id>/cancelar -> cancela um post (tira a foto da fila -> _canceladas)
  - GET  /api/contas                   -> contas reais (lidas do .env)
  - GET  /api/fila/<conta>             -> o que está na fila da conta
  - GET  /api/foto/<conta>/<arquivo>   -> serve a imagem da fila (prévia no app)
  - GET  /api/status                   -> resumo por conta (fila, estoque, token)

NÃO posta nada. Postagem automática é a Fase 2 (agendador).
Rodar:  python api.py      (http://localhost:5000)
"""

import os
import json
import time
import hashlib
import datetime as dt
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

APP_DIR          = (BASE_DIR / ".." / "pata3d-studio-recuperado").resolve()
PASTA_FOTOS      = BASE_DIR / "fotos"
PASTA_CANCELADAS = BASE_DIR / "fotos" / "_canceladas"
PASTA_DADOS      = BASE_DIR / "dados"
EXTENSOES        = {".jpg", ".jpeg", ".png", ".webp"}

# Segurança leve (Fase 5 = HTTPS + auth de verdade).
# Se APP_API_TOKEN estiver no .env, exige header X-API-Token nas rotas de escrita.
API_TOKEN = os.getenv("APP_API_TOKEN", "").strip()

# Horários padrão de postagem (usados até a aba Configurações mandar os reais).
HORARIOS_PADRAO = ["09:10", "14:00", "18:30", "20:00"]
DIAS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
GRAPH = "https://graph.instagram.com/v21.0"

app = Flask(__name__, static_folder=None)
CORS(app)


# ------------------------------------------------------------------
# Contas (lidas do .env, iguais ao main.py / instagram.py)
# ------------------------------------------------------------------
def carregar_contas():
    contas = []
    i = 1
    ativas = [int(x) for x in os.getenv("CONTAS_ATIVAS", "1").split(",") if x.strip()]
    paleta = ["#8B7CF6", "#3FB984", "#D6A33E", "#E0693A", "#9AA0A6"]
    while os.getenv(f"IG_PASTA_{i}") or os.getenv(f"IG_USER_ID_{i}"):
        slug = os.getenv(f"IG_PASTA_{i}", f"conta{i}")
        contas.append({
            "numero": i,
            "slug":   slug,
            "nome":   slug.replace("_", " ").title(),
            "nicho":  os.getenv(f"IG_NICHO_{i}", "lifestyle"),
            "ativa":  i in ativas,
            "cor":    paleta[(i - 1) % len(paleta)],
        })
        i += 1
    return contas


def conta_por_slug(slug):
    for c in carregar_contas():
        if c["slug"] == slug:
            return c
    return None


# ------------------------------------------------------------------
# Regras (maxPorDia, horários) — lê do contrato salvo pela aba Config
# ------------------------------------------------------------------
def carregar_regras():
    regras = {"maxPorDia": 2, "horarios": HORARIOS_PADRAO}
    cfg = PASTA_DADOS / "config.json"
    if cfg.exists():
        try:
            dados = json.loads(cfg.read_text(encoding="utf-8"))
            r = dados.get("regras", {})
            if r.get("maxPorDia"):
                regras["maxPorDia"] = int(r["maxPorDia"])
            if r.get("horarios"):
                regras["horarios"] = list(r["horarios"])
        except Exception:
            pass
    return regras


def horarios_para(maxpordia, horarios):
    """Garante uma lista de horários do tamanho de maxPorDia."""
    if maxpordia <= len(horarios):
        return horarios[:maxpordia]
    # repete espaçando caso peçam mais posts/dia que horários definidos
    saida = list(horarios)
    while len(saida) < maxpordia:
        saida.append(horarios[len(saida) % len(horarios)])
    return saida[:maxpordia]


# ------------------------------------------------------------------
# Fila de fotos por conta
# ------------------------------------------------------------------
def fila_da_conta(slug):
    pasta = PASTA_FOTOS / slug
    if not pasta.exists():
        return []
    return sorted(
        [f.name for f in pasta.iterdir()
         if f.is_file() and f.suffix.lower() in EXTENSOES]
    )


def item_id(slug, arquivo):
    return hashlib.sha1(f"{slug}/{arquivo}".encode("utf-8")).hexdigest()[:12]


def pastas_conteudo():
    """Pastas que o app mostra/gerencia: a entrada 'ideias' + a fila de cada conta."""
    return ["ideias"] + [c["slug"] for c in carregar_contas()]


def fotos_da_pasta(pasta):
    d = PASTA_FOTOS / pasta
    if not d.exists():
        return []
    return sorted([f.name for f in d.iterdir()
                   if f.is_file() and f.suffix.lower() in EXTENSOES])


def achar_por_id(item):
    """Dado o id de um post do calendário, acha (conta, arquivo) na fila."""
    for c in carregar_contas():
        for arquivo in fila_da_conta(c["slug"]):
            if item_id(c["slug"], arquivo) == item:
                return c, arquivo
    return None, None


# ------------------------------------------------------------------
# Legendas geradas por IA (cache por post) — só gera quando pedido
# ------------------------------------------------------------------
def _legendas_path():
    return PASTA_DADOS / "legendas.json"


def carregar_legendas():
    p = _legendas_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def salvar_legendas(d):
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    _legendas_path().write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------
# Config do servidor (dados/config.json) — SEM segredos aqui.
# Chaves de API ficam no .env; aqui só pipeline/IA por conta + regras.
# ------------------------------------------------------------------
def config_defaults():
    contas = {}
    for c in carregar_contas():
        eh_estante = "estante" in c["slug"]
        contas[c["slug"]] = {
            "pipeline":  "ia" if eh_estante else "simples",
            "iaLegenda": "gemini",
            "iaImagem":  "grok" if eh_estante else "",
        }
    return {
        "regras": {
            "maxPorDia":         2,
            "horarios":          list(HORARIOS_PADRAO),
            "bloqueioRepeticao": True,
            "alertaEstoqueDias": 7,
        },
        "contas": contas,
    }


def carregar_config():
    base = config_defaults()
    p = PASTA_DADOS / "config.json"
    if p.exists():
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(s.get("regras"), dict):
                for k in base["regras"]:
                    if k in s["regras"]:
                        base["regras"][k] = s["regras"][k]
            if isinstance(s.get("contas"), dict):
                for slug, cfg in s["contas"].items():
                    if slug in base["contas"] and isinstance(cfg, dict):
                        for k in ("pipeline", "iaLegenda", "iaImagem"):
                            if k in cfg:
                                base["contas"][slug][k] = cfg[k]
        except Exception:
            pass
    return base


def salvar_config(cfg):
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    (PASTA_DADOS / "config.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------
# Calendário automático (gerado da fila)
# ------------------------------------------------------------------
def gerar_calendario(de, ate):
    regras = carregar_regras()
    maxdia = max(1, regras["maxPorDia"])
    horarios = horarios_para(maxdia, regras["horarios"])

    # mapa data -> lista de posts
    por_dia = {}
    legs = carregar_legendas()

    for c in carregar_contas():
        if not c["ativa"]:
            continue
        fila = fila_da_conta(c["slug"])
        if not fila:
            continue

        dia = de
        idx_no_dia = 0
        for arquivo in fila:
            # pula dias cheios
            while idx_no_dia >= maxdia:
                dia = dia + dt.timedelta(days=1)
                idx_no_dia = 0
            if dia > ate:
                break  # além do horizonte pedido
            chave = dia.isoformat()
            iid = item_id(c["slug"], arquivo)
            por_dia.setdefault(chave, [])
            por_dia[chave].append({
                "id":      iid,
                "conta":   c["slug"],
                "nome":    c["nome"],
                "cor":     c["cor"],
                "data":    chave,
                "hora":    horarios[idx_no_dia],
                "arquivo": arquivo,
                "img":     f"/api/foto/{c['slug']}/{arquivo}",
                "formato": "feed",
                "status":  "agendado",
                "legenda": (legs.get(iid) or {}).get("legenda", ""),
            })
            idx_no_dia += 1

    # monta a lista de dias ordenada, com posts ordenados por hora
    dias = []
    d = de
    while d <= ate:
        chave = d.isoformat()
        posts = sorted(por_dia.get(chave, []), key=lambda p: p["hora"])
        dias.append({
            "data":    chave,
            "diaSem":  DIAS_PT[d.weekday()],
            "diaNum":  d.day,
            "posts":   posts,
        })
        d = d + dt.timedelta(days=1)

    return {
        "de":        de.isoformat(),
        "ate":       ate.isoformat(),
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "maxPorDia": maxdia,
        "dias":      dias,
    }


# ------------------------------------------------------------------
# Auth leve
# ------------------------------------------------------------------
def checar_token():
    if not API_TOKEN:
        return True  # dev no PC: aberto
    return request.headers.get("X-API-Token", "") == API_TOKEN


# ==================================================================
# ROTAS — API
# ==================================================================
@app.get("/api/contas")
def api_contas():
    return jsonify(carregar_contas())


@app.get("/api/fila/<conta>")
def api_fila(conta):
    if not conta_por_slug(conta):
        abort(404, "conta desconhecida")
    arquivos = fila_da_conta(conta)
    return jsonify({
        "conta":    conta,
        "total":    len(arquivos),
        "arquivos": [
            {"arquivo": a, "id": item_id(conta, a), "img": f"/api/foto/{conta}/{a}"}
            for a in arquivos
        ],
    })


@app.post("/api/upload/<conta>")
def api_upload(conta):
    if not checar_token():
        abort(401, "token invalido")
    # aceita a fila de uma conta OU a entrada 'ideias'
    if conta not in pastas_conteudo():
        abort(404, "pasta desconhecida")

    enviados = request.files.getlist("fotos") or request.files.getlist("file")
    if not enviados:
        abort(400, "nenhum arquivo enviado (campo 'fotos')")

    destino = PASTA_FOTOS / conta
    destino.mkdir(parents=True, exist_ok=True)

    salvos, ignorados = [], []
    for f in enviados:
        nome = secure_filename(f.filename or "")
        ext = Path(nome).suffix.lower()
        if not nome or ext not in EXTENSOES:
            ignorados.append(f.filename)
            continue
        alvo = destino / nome
        n = 2
        while alvo.exists():
            alvo = destino / f"{Path(nome).stem}_{n}{ext}"
            n += 1
        f.save(str(alvo))
        salvos.append(alvo.name)

    return jsonify({
        "conta":        conta,
        "salvos":       salvos,
        "ignorados":    ignorados,
        "total_fila":   len(fila_da_conta(conta)),
    }), 201


@app.get("/api/calendario")
def api_calendario():
    hoje = dt.date.today()
    try:
        de = dt.date.fromisoformat(request.args["de"]) if request.args.get("de") else hoje
        ate = dt.date.fromisoformat(request.args["ate"]) if request.args.get("ate") else hoje + dt.timedelta(days=13)
    except ValueError:
        abort(400, "datas invalidas (use YYYY-MM-DD)")
    if ate < de:
        abort(400, "ate anterior a de")
    if (ate - de).days > 60:
        abort(400, "intervalo maximo 60 dias")
    return jsonify(gerar_calendario(de, ate))


@app.post("/api/calendario/<item>/cancelar")
def api_cancelar(item):
    """Reprovar: a foto que não gostei sai da fila (vai pra _canceladas)."""
    if not checar_token():
        abort(401, "token invalido")
    c, arquivo = achar_por_id(item)
    if not c:
        abort(404, "post nao encontrado (talvez ja tenha saido da fila)")
    origem = PASTA_FOTOS / c["slug"] / arquivo
    destino_dir = PASTA_CANCELADAS / c["slug"]
    destino_dir.mkdir(parents=True, exist_ok=True)
    alvo = destino_dir / arquivo
    n = 2
    while alvo.exists():
        alvo = destino_dir / f"{Path(arquivo).stem}_{n}{Path(arquivo).suffix}"
        n += 1
    origem.rename(alvo)
    # tira a legenda em cache também
    legs = carregar_legendas()
    if item in legs:
        legs.pop(item, None)
        salvar_legendas(legs)
    return jsonify({"cancelado": item, "conta": c["slug"], "arquivo": arquivo})


@app.post("/api/calendario/<item>/legenda")
def api_nova_legenda(item):
    """Gera uma legenda nova (IA) para a foto desse post e guarda no cache."""
    if not checar_token():
        abort(401, "token invalido")
    c, arquivo = achar_por_id(item)
    if not c:
        abort(404, "post nao encontrado")
    foto = PASTA_FOTOS / c["slug"] / arquivo
    try:
        from legenda import gerar_legenda  # importa só aqui (usa Gemini)
        texto = gerar_legenda(Path(arquivo).stem, contexto_extra=c["nicho"], caminho_imagem=str(foto))
    except Exception as e:
        abort(502, f"falha ao gerar legenda: {e}")
    legs = carregar_legendas()
    legs[item] = {"conta": c["slug"], "arquivo": arquivo, "legenda": texto}
    salvar_legendas(legs)
    return jsonify({"id": item, "conta": c["slug"], "arquivo": arquivo, "legenda": texto})


@app.get("/api/foto/<conta>/<path:arquivo>")
def api_foto(conta, arquivo):
    if not conta_por_slug(conta):
        abort(404)
    pasta = PASTA_FOTOS / conta
    return send_from_directory(str(pasta), arquivo)


@app.get("/api/historico")
def api_historico():
    """Desempenho REAL por conta, lido de dados/historico.json.
    ?atualizar=1 busca as métricas ao vivo no Instagram antes de responder."""
    atualizar = request.args.get("atualizar") == "1"
    contas = carregar_contas()

    if atualizar:
        from metricas import atualizar_metricas_historico
        for c in contas:
            try:
                atualizar_metricas_historico(c["numero"])
            except Exception as e:
                print(f"[api] falha ao atualizar metricas conta {c['numero']}: {e}")

    from metricas import carregar_historico
    hist = carregar_historico()
    METR = ["reach", "likes", "saved", "comments", "shares"]

    saida = []
    for c in contas:
        posts = [p for p in hist if p.get("conta") == c["numero"]]
        soma = {k: sum(int(p.get(k, 0) or 0) for p in posts) for k in METR}
        ult = max([p.get("registrado_em", "") for p in posts], default="")
        saida.append({
            "conta":      c["slug"],
            "nome":       c["nome"],
            "cor":        c["cor"],
            "numero":     c["numero"],
            "ativa":      c["ativa"],
            "totalPosts": len(posts),
            "soma":       soma,
            "comMetrica": any(p.get("reach", 0) for p in posts),
            "ultimo":     ult,
            "posts": [{
                "arquivo":       p.get("arquivo"),
                "media_id":      p.get("media_id_feed"),
                "reach":         p.get("reach", 0),
                "likes":         p.get("likes", 0),
                "saved":         p.get("saved", 0),
                "comments":      p.get("comments", 0),
                "shares":        p.get("shares", 0),
                "registrado_em": p.get("registrado_em", ""),
            } for p in posts],
        })

    return jsonify({
        "fonte":          "Instagram Graph API · gravado em dados/historico.json (cada post tem media_id real)",
        "atualizadoAgora": atualizar,
        "contas":         saida,
    })


@app.get("/api/config")
def api_get_config():
    cfg = carregar_config()
    meta = {c["slug"]: c for c in carregar_contas()}
    lista = []
    for slug, cc in cfg["contas"].items():
        m = meta.get(slug, {})
        lista.append({
            "slug":  slug,
            "nome":  m.get("nome", slug),
            "cor":   m.get("cor", "#888"),
            "ativa": m.get("ativa", False),
            "nicho": m.get("nicho", ""),
            **cc,
        })
    return jsonify({
        # status das chaves (true/false) — valor real NUNCA sai do servidor
        "chavesStatus": {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "grok":   bool(os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")),
            "imgbb":  bool(os.getenv("IMGBB_API_KEY")),
        },
        "iasDisponiveis": {"gemini": "Gemini (Google)", "grok": "Grok (xAI)"},
        "horariosPadrao": HORARIOS_PADRAO,
        "regras":         cfg["regras"],
        "contas":         lista,
    })


@app.post("/api/config")
def api_post_config():
    if not checar_token():
        abort(401, "token invalido")
    body = request.get_json(silent=True) or {}
    cfg = carregar_config()

    r = body.get("regras") or {}
    if "maxPorDia" in r:
        try:
            cfg["regras"]["maxPorDia"] = max(1, min(20, int(r["maxPorDia"])))
        except (ValueError, TypeError):
            pass
    if isinstance(r.get("horarios"), list):
        hs = [str(x).strip() for x in r["horarios"] if str(x).strip()]
        if hs:
            cfg["regras"]["horarios"] = hs
    if "bloqueioRepeticao" in r:
        cfg["regras"]["bloqueioRepeticao"] = bool(r["bloqueioRepeticao"])
    if "alertaEstoqueDias" in r:
        try:
            cfg["regras"]["alertaEstoqueDias"] = max(1, min(60, int(r["alertaEstoqueDias"])))
        except (ValueError, TypeError):
            pass

    cont = body.get("contas") or {}
    for slug, c in cont.items():
        if slug in cfg["contas"] and isinstance(c, dict):
            for k in ("pipeline", "iaLegenda", "iaImagem"):
                if k in c:
                    cfg["contas"][slug][k] = str(c[k])

    salvar_config(cfg)
    return jsonify({"ok": True, "regras": cfg["regras"], "contas": cfg["contas"]})


@app.get("/api/instagram/<conta>")
def api_instagram(conta):
    """Puxa as ÚLTIMAS publicações reais do Instagram (Graph API) dessa conta:
    miniatura, curtidas, comentários e alcance. Dados ao vivo, não o histórico local."""
    c = conta_por_slug(conta)
    if not c:
        abort(404, "conta desconhecida")
    num = c["numero"]
    uid = os.getenv(f"IG_USER_ID_{num}", "")
    tok = os.getenv(f"IG_ACCESS_TOKEN_{num}", "")
    if not uid or not tok:
        abort(400, "conta sem credenciais no .env")

    try:
        limite = max(1, min(25, int(request.args.get("limite", 12))))
    except (ValueError, TypeError):
        limite = 12

    try:
        r = requests.get(f"{GRAPH}/{uid}/media", params={
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
            "limit": limite,
            "access_token": tok,
        }, timeout=30)
        data = r.json()
    except Exception as e:
        abort(502, f"falha ao falar com o Instagram: {e}")

    if "data" not in data:
        abort(502, (data.get("error") or {}).get("message", "resposta inesperada do Instagram"))

    posts = []
    for m in data["data"]:
        reach = None
        try:  # alcance vem dos insights (nem todo tipo/conta libera)
            ri = requests.get(f"{GRAPH}/{m['id']}/insights",
                              params={"metric": "reach", "access_token": tok}, timeout=20)
            d = ri.json().get("data", [])
            if d:
                reach = d[0]["values"][0]["value"]
        except Exception:
            pass
        posts.append({
            "id":        m["id"],
            "timestamp": m.get("timestamp", ""),
            "tipo":      m.get("media_type", ""),
            "permalink": m.get("permalink", ""),
            "thumb":     m.get("thumbnail_url") or m.get("media_url") or "",
            "likes":     m.get("like_count", 0),
            "comments":  m.get("comments_count", 0),
            "reach":     reach if reach is not None else 0,
            "temReach":  reach is not None,
            "legenda":   (m.get("caption") or "")[:140],
        })

    return jsonify({
        "conta":      conta,
        "nome":       c["nome"],
        "cor":        c["cor"],
        "fonte":      "ao vivo da Graph API do Instagram",
        "total":      len(posts),
        "temAlcance": any(p["temReach"] for p in posts),
        "posts":      posts,
    })


@app.get("/api/biblioteca")
def api_biblioteca():
    """Pastas REAIS do servidor: a entrada 'ideias' + a fila de cada conta."""
    pastas = []
    inbox = fotos_da_pasta("ideias")
    pastas.append({
        "id": "ideias", "nome": "Ideias / referências", "tipo": "inbox", "cor": "#6a6a7a",
        "total": len(inbox),
        "fotos": [{"arquivo": a, "url": f"/api/conteudo/foto/ideias/{a}"} for a in inbox],
    })
    for c in carregar_contas():
        fs = fotos_da_pasta(c["slug"])
        pastas.append({
            "id": c["slug"], "nome": c["nome"], "tipo": "fila", "cor": c["cor"], "ativa": c["ativa"],
            "total": len(fs),
            "fotos": [{"arquivo": a, "url": f"/api/conteudo/foto/{c['slug']}/{a}"} for a in fs],
        })
    contas = [{"slug": c["slug"], "nome": c["nome"], "cor": c["cor"]} for c in carregar_contas()]
    return jsonify({"pastas": pastas, "contas": contas})


@app.get("/api/conteudo/foto/<pasta>/<path:arquivo>")
def api_conteudo_foto(pasta, arquivo):
    if pasta not in pastas_conteudo():
        abort(404)
    return send_from_directory(str(PASTA_FOTOS / pasta), arquivo)


@app.post("/api/conteudo/mover")
def api_mover():
    """Move uma foto de uma pasta pra outra (ex.: de 'ideias' pra a fila de uma conta)."""
    if not checar_token():
        abort(401, "token invalido")
    body = request.get_json(silent=True) or {}
    de = str(body.get("de", ""))
    para = str(body.get("para", ""))
    arquivo = secure_filename(str(body.get("arquivo", "")))
    allowed = pastas_conteudo()
    if de not in allowed or para not in allowed:
        abort(400, "pasta invalida")
    if de == para:
        abort(400, "origem e destino iguais")
    if not arquivo:
        abort(400, "arquivo invalido")
    origem = PASTA_FOTOS / de / arquivo
    if not origem.exists():
        abort(404, "arquivo nao encontrado")
    destino_dir = PASTA_FOTOS / para
    destino_dir.mkdir(parents=True, exist_ok=True)
    alvo = destino_dir / arquivo
    n = 2
    while alvo.exists():
        alvo = destino_dir / f"{Path(arquivo).stem}_{n}{Path(arquivo).suffix}"
        n += 1
    origem.rename(alvo)
    return jsonify({"ok": True, "de": de, "para": para, "arquivo": alvo.name})


@app.get("/api/notificacoes")
def api_notificacoes():
    """Avisos reais: conta ativa sem fotos na fila, ou estoque acabando."""
    cfg = carregar_config()
    maxdia = max(1, int(cfg["regras"].get("maxPorDia", 2) or 2))
    alerta = int(cfg["regras"].get("alertaEstoqueDias", 7) or 7)
    avisos = []
    for c in carregar_contas():
        if not c["ativa"]:
            continue
        fila = len(fotos_da_pasta(c["slug"]))
        dias = fila // maxdia
        if fila == 0:
            avisos.append({"nivel": "alto", "conta": c["slug"], "nome": c["nome"],
                           "texto": f"{c['nome']}: sem fotos na fila — não vai postar."})
        elif dias <= alerta:
            avisos.append({"nivel": "medio", "conta": c["slug"], "nome": c["nome"],
                           "texto": f"{c['nome']}: estoque acabando (~{dias} dia(s), {fila} foto(s))."})
    total = len(avisos)
    if not avisos:
        avisos.append({"nivel": "ok", "texto": "Tudo certo — nenhum aviso agora."})
    return jsonify({"total": total, "avisos": avisos})


@app.post("/api/gerar3d")
def api_gerar3d():
    """Recebe uma imagem 2D e gera a estátua 3D. engine: gemini (padrão) ou qwen."""
    if not checar_token():
        abort(401, "token invalido")
    enviados = (request.files.getlist("foto") or request.files.getlist("file")
                or request.files.getlist("fotos"))
    if not enviados:
        abort(400, "envie uma imagem (campo 'foto')")
    f = enviados[0]
    nome = secure_filename(f.filename or "ref.jpg")
    if Path(nome).suffix.lower() not in EXTENSOES:
        abort(400, "formato inválido (use jpg/png/webp)")
    engine = (request.form.get("engine") or "gemini").strip().lower()
    modelo = (request.form.get("modelo") or "").strip() or None

    tmpdir = PASTA_DADOS / "_upload_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    ref = tmpdir / nome
    f.save(str(ref))

    out_dir = PASTA_FOTOS / "_gerados"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = (modelo or engine).replace(".", "").replace("/", "")
    dst = out_dir / f"{Path(nome).stem}_{tag}_{int(time.time())}.png"

    try:
        import estante
        estante.gerar(str(ref), str(dst), engine=engine, modelo=modelo, tentativas=3)
    except Exception as e:
        abort(502, f"falha ao gerar: {e}")

    return jsonify({"ok": True, "engine": engine, "modelo": modelo,
                    "url": f"/api/gerado/{dst.name}", "arquivo": dst.name})


@app.get("/api/modelos3d")
def api_modelos3d():
    """Lista os modelos de imagem disponíveis pro gerador."""
    import estante
    return jsonify({"gemini": estante.MODELOS_GEMINI, "qwen": estante.MODELOS_QWEN})


@app.get("/api/gerado/<path:arquivo>")
def api_gerado(arquivo):
    return send_from_directory(str(PASTA_FOTOS / "_gerados"), arquivo)


@app.get("/api/status")
def api_status():
    regras = carregar_regras()
    maxdia = max(1, regras["maxPorDia"])
    saida = []
    for c in carregar_contas():
        fila = len(fila_da_conta(c["slug"]))
        saida.append({
            "conta":      c["slug"],
            "nome":       c["nome"],
            "cor":        c["cor"],
            "ativa":      c["ativa"],
            "fotosNaFila": fila,
            "estoqueDias": fila // maxdia if maxdia else fila,
        })
    return jsonify({"contas": saida, "maxPorDia": maxdia})


# ==================================================================
# ROTAS — serve o app (mesma origem da API)
# ==================================================================
@app.get("/")
def index():
    return send_from_directory(str(APP_DIR), "index.html")


@app.get("/<path:caminho>")
def arquivos_app(caminho):
    alvo = (APP_DIR / caminho).resolve()
    # nao deixa escapar da pasta do app
    if not str(alvo).startswith(str(APP_DIR)):
        abort(403)
    if alvo.is_file():
        return send_from_directory(str(APP_DIR), caminho)
    abort(404)


if __name__ == "__main__":
    PASTA_FOTOS.mkdir(exist_ok=True)
    PASTA_DADOS.mkdir(exist_ok=True)
    print(f"[api] app servido de: {APP_DIR}")
    print(f"[api] contas ativas: {[c['slug'] for c in carregar_contas() if c['ativa']]}")
    print(f"[api] http://localhost:5000  (Ctrl+C para parar)")
    app.run(host="0.0.0.0", port=5000, debug=False)
