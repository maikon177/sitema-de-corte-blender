# APK Galeria Local Pata3D

App Android nativo para:

- conectar no servidor local do PC;
- navegar pelas pastas dentro de `fotos`;
- ver a galeria;
- enviar imagens e videos do celular sem depender do navegador.

## Requisitos

1. No PC, iniciar:

`D:\intagram postagem\galeria-local-uploader\INICIAR_GALERIA_LOCAL.bat`

2. No celular e no PC, usar a mesma rede local.

3. No app Android, informar o IP do PC, por exemplo:

`http://192.168.50.46:8765`

## Gerar APK

Rode:

```powershell
BUILD_APK.bat
```

## Saida esperada

`app\build\outputs\apk\debug\app-debug.apk`
