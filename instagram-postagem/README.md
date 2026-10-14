# Instagram postagem

Código do projeto que está em `D:\disco D\intagram postagem`, enviado para acompanhar a issue #2.

## O que tem aqui

| Pasta | Função |
| --- | --- |
| `instagram-poster` | Programa Python que edita a foto, gera a legenda e posta pela API oficial do Instagram |
| `pata3d-studio-recuperado` | Protótipo do app Pata3D Studio |
| `galeria-local-apk` | App Android da galeria local |
| `galeria-local-uploader` | Uploader local em Python |
| `instagram-preview` | Prévia dos posts |
| `apk-recuperado` | Referência extraída do APK (só os textos; sem dex, imagens e zip) |

## O que ficou de fora de propósito

O repositório é público. Estes itens continuam só no computador:

- `.env`, `.env.bak`, `.env.bak2` e `.env.bak3` (tokens do Instagram, Gemini, ImgBB e Qwen)
- `venv/`, `__pycache__/` e pastas `build/`
- `pagina/` (página do Instagram salva pelo navegador)
- fotos, renders e os arquivos `.blend`
- `local.properties` (caminho do Android SDK nesta máquina)
- binários do APK (`classes.dex`, `resources.arsc`, zip)

O endereço da VPS e o caminho da chave SSH foram trocados nos textos por `SEU_IP_DA_VPS` e `CAMINHO_DA_CHAVE_SSH`. Os originais continuam no PC.

Para rodar o poster: copie `.env.example` para `.env`, preencha as chaves e instale `instagram-poster/requirements.txt`.
