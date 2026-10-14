# Instagram Preview Pata3D

Mini site local para testar como as postagens podem ficar antes de publicar no Instagram real.

## O que mostra

- feed estilo Instagram;
- cards de carrossel;
- area de reels de teste;
- legenda;
- hashtags;
- horario sugerido;
- painel lateral com detalhes do post selecionado.

## Fonte atual

`D:\intagram postagem\instagram-poster\fotos\pata3d_cortadores`

## Como usar

1. Rode:

```powershell
INICIAR_PREVIEW_INSTAGRAM.bat
```

2. Abra:

`http://127.0.0.1:8787`

3. Veja como cada grupo/arquivo esta virando rascunho de post.

## Observacao

Agora a previa usa o mesmo motor central de rascunhos de `D:\intagram postagem\instagram-poster\rascunhos.py`.

Isso significa que:

- a logica de legenda, hashtags, horario e tipo de post nao fica mais presa no preview;
- os rascunhos podem ser reaproveitados depois na fila de aprovacao e na postagem real;
- o JSON atual e salvo em `D:\intagram postagem\instagram-poster\dados\rascunhos_pata3d_cortadores.json`.
