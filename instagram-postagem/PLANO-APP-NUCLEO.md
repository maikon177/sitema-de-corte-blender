# Plano de ação — Pata3D Studio como núcleo

> Atualizado em 2026-10-13. Regra principal: **o APP (Pata3D Studio) é o centro. Toda peça se liga nele por uma API no servidor.**

## A ideia central (o que o produto faz)
1. **Eu coloco as fotos pelo app** → elas ficam **salvas no servidor**, na fila de cada conta.
2. O servidor **monta sozinho o calendário** do que vai ser postado em cada dia.
3. **Posta automático todo dia**, sem precisar de aprovação.
4. No app eu só **acompanho** o calendário e **cancelo** o que não gostar (o resto sai sozinho).
5. O app também mostra a **análise do Instagram e do site** pata3d.

```
Celular (app) ──upload──► Servidor: fila por conta ──► Calendário automático ──► Posta sozinho
      ▲                                                     │
      └──── acompanhar / cancelar / análise (Instagram + site) ◄──┘
```

## Inventário (onde está cada peça)

| Peça | Pasta | Estado |
|------|-------|--------|
| **App (núcleo)** | `pata3d-studio-recuperado\` | protótipo com dados de exemplo; aba **Configurações** já salva (localStorage) |
| Extraído do APK original | `apk-recuperado\` | só referência |
| Poster (posta no Instagram) | `instagram-poster\` | funciona local; 3 tokens vivos; Gemini ok; editor simples; contas dinâmicas |
| Galeria/uploader | `galeria-local-uploader\`, `galeria-local-apk\` | vai ser **substituído** pelo upload do próprio app |
| Prévia dos posts | `instagram-preview\` | reaproveitar a lógica na tela de detalhe do app |
| Site pata3d (para a análise) | VPS (nginx) | fonte da análise do site |
| VPS | `SEU_IP_DA_VPS` (Hostinger) | **sem acesso**: falta colar a chave pública nova |

## Fase 0 — Garantir que está tudo ligado (checagem)
- [ ] Tokens das 3 contas respondem na Graph API (`/me`).
- [ ] Chave do Gemini válida.
- [ ] `instagram-poster\venv` existe; `python main.py --so-analise` roda sem erro.
- [ ] Código enxerga as 3 contas; `CONTAS_ATIVAS=1,2`.
- [ ] App abre servido por HTTP e a aba Configurações salva.

## Fase 1 — A ponte: API do app (primeiro no PC, depois na VPS)
Servidor Flask dentro de `instagram-poster\` que **serve o app** e expõe:

| Rota | Faz |
|------|-----|
| `POST /api/upload/<conta>` | recebe fotos do celular e salva na fila da conta |
| `GET /api/fila/<conta>` | lista o que está na fila |
| `GET /api/calendario?de=&ate=` | o que vai ser postado em cada dia (gerado automático) |
| `POST /api/calendario/<id>/cancelar` | cancela um post agendado (a foto sai da fila ou vai pra "canceladas") |
| `GET /api/status` | token vivo/vencendo por conta, fotos na fila, dias de estoque, última postagem |
| `GET/POST /api/config` | IA por conta, pipeline, regras (máx/dia, horários), chaves |
| `GET /api/historico` | o que já foi postado + métricas do Instagram |
| `GET /api/site/analise` | visitas, páginas mais vistas, origem do tráfego do site |

Segurança: a API guarda fotos e chaves → exigir **senha/token de acesso** no app e só expor com HTTPS.

## Fase 2 — Agendador automático (o coração)
- Gera o **calendário** a partir da fila: respeita `maxPorDia` por conta e os horários definidos nas configurações.
- Na hora marcada, **posta sozinho** (sem aprovação) e move a foto pra `publicadas/`.
- Item **cancelado** no app é pulado.
- Avisa no app quando: token vai vencer, estoque de fotos acabando, post falhou.

## Fase 3 — Ligar o app na API (tela por tela)
1. `data.js` → `fetch()` na API.
2. **Conteúdo** → upload real das fotos (`/api/upload`).
3. **Calendário** → tela principal: o que sai hoje/semana, com botão **Cancelar**.
4. **Início / Contas** → `/api/status` (números reais).
5. **Configurações** → `/api/config`.
6. **Analytics** → Instagram (`/api/historico`) + site (`/api/site/analise`).
7. Remover o que não faz parte da ideia: etapa **"Aprovar"** e a esteira de aprovação.

## Fase 4 — Análise do site
Fonte sugerida: os **logs do nginx** que já existem na VPS (sem ferramenta de terceiros). Alternativa: um contador leve no próprio site. Decidir na hora.

## Fase 5 — VPS (onde tudo vai morar de verdade)
Fotos e postagem automática precisam de servidor ligado 24h → colar a chave pública → subir API + agendador → `.env` atualizado → HTTPS + autenticação.

## Fase 6 — APK novo
Recompilar o Capacitor apontando para a API da VPS.

## Fase 7 — Estante Imaginária
Pipeline de IA (imagem 2D → conceito colecionável) com Grok ou Gemini, escolhido na aba Configurações.

## Regras para quem for executar
- **Produto**: posta automático, sem aprovação; o usuário só cancela.
- **Durante o desenvolvimento**: não disparar post real no Instagram sem o usuário pedir — testar com conta/foto de teste ou modo simulação.
- Não colar chaves/tokens no chat nem em documentos; só no `.env`.
- Caminho certo é `D:\disco D\intagram postagem` (docs antigos falam `E:\`).
