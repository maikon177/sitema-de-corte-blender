# 📸 Handoff — Auto-Poster Instagram (Pata3D)

> Documento para retomar o projeto em outra conversa. Atualizado em **2026-10-09**.
> Objetivo: sistema que **posta sozinho no Instagram** (feed + stories), com legenda por IA, rodando na **VPS** (não depende mais do celular).

---

## 1. Resumo — o que é e como funciona

Programa em **Python** que, a cada execução, pega **1 foto por conta ativa** e:
1. **Edita** a imagem para feed e para stories (biblioteca Pillow) — `editor.py`
2. **Gera a legenda com IA (Google Gemini)** analisando a imagem — `legenda.py`
3. **Sobe a imagem no ImgBB** para ter uma URL pública (a API do Instagram exige URL pública) — `uploader.py`
4. **Posta no feed + stories** pela **API oficial do Instagram (Graph API)** — `instagram.py`
5. Guarda métricas em `dados/historico.json` e **move a foto** para `publicadas/<conta>/` — `metricas.py`, `main.py`

Ponto de entrada: **`main.py`**
- `python main.py` → posta (1 foto por conta) + atualiza métricas
- `python main.py --so-analise` → só métricas, não posta
- `python main.py --gerar-rascunhos` → gera rascunhos de legenda sem postar

**Importante:** usa a **API OFICIAL** (`graph.instagram.com`), não login/senha pirata. Por isso roda numa VPS (IP de datacenter) sem risco de bloqueio por automação.

---

## 2. Onde fica (PC e Servidor)

| Lugar | Caminho |
|-------|---------|
| Código-fonte (PC) | `E:\disco D\intagram postagem\instagram-poster` |
| Deploy na VPS | `/srv/instagram-poster` |
| Ambiente Python (VPS) | `/srv/instagram-poster/venv` |
| Config/segredos (VPS) | `/srv/instagram-poster/.env` (permissão 600) |
| Config/segredos (PC) | `E:\disco D\intagram postagem\instagram-poster\.env` |
| Fotos na fila | `fotos/<pasta_da_conta>/` |
| Fotos já postadas | `publicadas/<pasta_da_conta>/` |
| Histórico/métricas | `dados/historico.json` |

Dono dos arquivos na VPS: usuário **`webapps`**.

---

## 3. Acesso ao servidor (VPS)

- Provedor: **Hostinger VPS** · Ubuntu
- IP: **`SEU_IP_DA_VPS`** · usuário **`root`**
- Chave SSH (no PC): `CAMINHO_DA_CHAVE_SSH`

Conectar:
```bash
ssh -i "CAMINHO_DA_CHAVE_SSH" root@SEU_IP_DA_VPS
```

---

## 4. APIs e serviços que o programa precisa

Todos configurados no arquivo **`.env`**. Pegue cada chave assim:

| Serviço | Para que serve | Variável(is) no `.env` | Onde obter |
|---------|----------------|------------------------|------------|
| **Instagram Graph API** | Postar no feed/stories | `IG_USER_ID_1`, `IG_ACCESS_TOKEN_1`, `IG_USER_ID_2`, `IG_ACCESS_TOKEN_2` | Meta for Developers (developers.facebook.com) — ver seção 6 |
| **Google Gemini** | Gerar as legendas | `GEMINI_API_KEY` | https://aistudio.google.com/apikey (grátis) |
| **ImgBB** | Hospedar a imagem (URL pública) | `IMGBB_API_KEY` | https://api.imgbb.com (grátis) |

Outras variáveis do `.env`:
- `CONTAS_ATIVAS` → quais contas usar: `1`, `2` ou `1,2`
- `IG_PASTA_1` / `IG_PASTA_2` → nome da pasta em `fotos/` de cada conta (ex.: `pata3d_cortadores`)
- `IG_NICHO_1` / `IG_NICHO_2` → nicho (ajuda a IA na legenda)
- `NOME_MARCA` → marca d'água (se não houver `assets/logo.png`)
- `IDIOMA_LEGENDA` → idioma das legendas

> 🔒 **Os VALORES secretos NÃO estão neste documento, de propósito.** Eles ficam no `.env` (no PC e na VPS). Uma conversa futura neste projeto pode ler/editar o `.env` direto. Nunca colar chave/token em documento que possa ser compartilhado.

Dependências Python (já instaladas no venv): `pillow`, `google-genai`, `requests`, `python-dotenv`.
> ⚠️ É `google-genai` (SDK novo, `from google import genai`), **não** `google-generativeai`. O `requirements.txt` já foi corrigido.

---

## 5. STATUS ATUAL (2026-10-09) — o que falta

✅ Sistema **instalado e testado** na VPS (pipeline carrega 100%).
✅ Agendamento criado: **1x por dia, 10:00 (horário de Brasília)**.
⛔ **Agendamento DESLIGADO** de propósito — esperando token novo.
⛔ **BLOQUEIO: os 2 tokens do Instagram estão MORTOS** (verificado em 2026-10-08):
   - Conta 1: invalidado porque a **senha do Instagram/Facebook foi trocada**.
   - Conta 2: **expirou** em 06/jul/2026 (limite de ~60 dias).

➡️ **Para voltar a postar:** gerar tokens novos (seção 6), colocar no `.env`, e ligar o agendamento (seção 7).

Fila de fotos: **`pata3d_cortadores` tem 16 fotos prontas**; `pata3d_artesanato` está com 0.

---

## 6. Como gerar os tokens novos do Instagram

Pré-requisitos (provavelmente já existem, pois já funcionou antes):
- Cada conta do Instagram precisa ser **Business ou Creator**.
- Ligada a uma **Página do Facebook**.
- Um **app na Meta** (developers.facebook.com) com o produto **Instagram** adicionado.

Passo geral (peça ajuda à IA para guiar clique a clique):
1. Entrar em **developers.facebook.com** → seu app.
2. Produto **Instagram → API setup** → gerar **token de acesso** da conta.
3. Converter para **token de longa duração** (~60 dias).
4. Pegar também o **IG User ID** de cada conta.
5. Colocar no `.env`: `IG_ACCESS_TOKEN_1`, `IG_USER_ID_1` (e `_2` para a segunda conta).

> A IA **não digita a senha/token por você** (regra de segurança) — você faz os logins e cliques; a IA mostra onde clicar e depois grava o token no `.env` da VPS.

Testar se um token está vivo (na VPS, sem postar):
```bash
cd /srv/instagram-poster
./venv/bin/python - <<'PY'
import os,urllib.request,json,urllib.parse
from pathlib import Path
env=dict(l.split("=",1) for l in Path(".env").read_text().splitlines() if l and not l.startswith("#") and "=" in l)
t=env.get("IG_ACCESS_TOKEN_1","").strip()
url=f"https://graph.instagram.com/v21.0/me?fields=id,username&access_token={urllib.parse.quote(t)}"
try:
    print("VIVO:", json.load(urllib.request.urlopen(url,timeout=20)))
except Exception as e:
    print("MORTO/ERRO:", e)
PY
```

---

## 7. Operação do dia a dia (comandos na VPS)

**Editar o `.env` (ex.: colocar token novo):**
```bash
nano /srv/instagram-poster/.env
```

**Ligar o agendamento (depois do token novo):**
```bash
systemctl enable --now instagram-poster.timer
systemctl list-timers instagram-poster.timer   # ver próxima execução
```

**Desligar o agendamento:**
```bash
systemctl disable --now instagram-poster.timer
```

**Postar AGORA, na mão (1 foto por conta):**
```bash
sudo -u webapps /srv/instagram-poster/venv/bin/python /srv/instagram-poster/main.py
# ou rodar o serviço:
systemctl start instagram-poster.service
```

**Ver o que aconteceu (logs):**
```bash
journalctl -u instagram-poster.service -n 50 --no-pager
```

**Adicionar fotos na fila:** copiar imagens para a pasta da conta. Do PC:
```bash
scp -i "CAMINHO_DA_CHAVE_SSH" "foto.jpg" root@SEU_IP_DA_VPS:/srv/instagram-poster/fotos/pata3d_cortadores/
# depois, na VPS: chown webapps:webapps /srv/instagram-poster/fotos/pata3d_cortadores/*.jpg
```

**Atualizar o código depois de editar no PC** (reenviar os `.py`):
```bash
scp -i "CAMINHO_DA_CHAVE_SSH" *.py root@SEU_IP_DA_VPS:/srv/instagram-poster/
```

---

## 8. Detalhes do agendamento (systemd)

- Serviço: `/etc/systemd/system/instagram-poster.service` (tipo oneshot, roda como `webapps`, WorkingDirectory `/srv/instagram-poster`).
- Timer: `/etc/systemd/system/instagram-poster.timer` → `OnCalendar=*-*-* 13:00:00` (UTC = **10:00 Brasília**), `Persistent=true`.
- Mudar horário/frequência: editar o `OnCalendar` do `.timer` e `systemctl daemon-reload`.

---

## 9. Pendências / melhorias futuras

- 🔑 **Renovar token a cada ~60 dias** (a API do Instagram expira). Não há renovação automática no código ainda — dá para automatizar depois (refresh de long-lived token).
- A conta `pata3d_artesanato` está sem fotos na fila.
- (Fora deste projeto, mas anotado: o site **tarefas.blog.br** ficou no erro 530 esperando um ajuste de DNS na Cloudflare.)

---

## 10. Arquivos do projeto (referência rápida)

| Arquivo | Função |
|---------|--------|
| `main.py` | Orquestra tudo (ler fila → editar → legenda → upload → postar → mover) |
| `editor.py` | Edita imagem para feed e stories (Pillow) |
| `legenda.py` | Gera legenda com Gemini |
| `uploader.py` | Sobe imagem no ImgBB e devolve URL pública |
| `instagram.py` | Posta via Graph API (container + publish) |
| `metricas.py` | Salva/atualiza métricas no histórico |
| `rascunhos.py` | Gera rascunhos de legenda |
| `.env` | Todas as chaves/configuração (NÃO versionar/compartilhar) |
| `.env.example` | Modelo do `.env`, sem segredos |
| `requirements.txt` | Dependências Python |
