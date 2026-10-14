# Galeria Local Pata3D

**Data:** 2026-05-10

## Resumo

App web local simples para enviar fotos e videos do celular para:

`D:\intagram postagem\instagram-poster\fotos`

Ele abre na rede local, funciona no navegador do celular e mistura:

- galeria visual;
- upload de arquivos;
- criacao de pastas;
- mover arquivos entre pastas;
- exclusao simples.

## Como usar

1. No PC, rode:

```powershell
python app.py
```

2. O terminal vai mostrar links como:

```text
http://127.0.0.1:8765
http://IP_DO_PC:8765
```

3. No celular, conectado na mesma rede Wi-Fi, abra o link `http://IP_DO_PC:8765`.

4. Envie as fotos/videos.

## Estrutura

- `app.py`: servidor web local.
- `INICIAR_GALERIA_LOCAL.bat`: atalho para iniciar mais rápido no Windows.

## Observacoes

- O servidor escuta em `0.0.0.0`, entao pode ser acessado por outros dispositivos da mesma rede local.
- O app limita operacoes a partir da pasta base `fotos`.
- Arquivos com nome repetido ganham sufixo automatico `_2`, `_3`, etc.
