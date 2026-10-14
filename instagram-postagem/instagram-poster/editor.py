"""
Editor de imagem — versão SIMPLES (contas Pata3D).

Objetivo: foto real com edição leve, sem marca d'água/CTA/template.
- Corrige luz/contraste/cor (ótimo pra fotos escuras da impressora).
- Enquadra em 1080x1080 (feed) e 1080x1920 (stories) usando FUNDO DESFOCADO
  da própria foto, sem cortar o produto.
"""

from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path

FEED_SIZE    = (1080, 1080)
STORIES_SIZE = (1080, 1920)


def _redimensionar_com_crop(img: Image.Image, tamanho: tuple) -> Image.Image:
    """Preenche o tamanho alvo cortando o excedente (usado só pro fundo)."""
    alvo_w, alvo_h = tamanho
    orig_w, orig_h = img.size
    ratio = max(alvo_w / orig_w, alvo_h / orig_h)
    novo = (int(orig_w * ratio), int(orig_h * ratio))
    img = img.resize(novo, Image.LANCZOS)
    esq = (novo[0] - alvo_w) // 2
    top = (novo[1] - alvo_h) // 2
    return img.crop((esq, top, esq + alvo_w, top + alvo_h))


def _corrigir_foto(img: Image.Image) -> Image.Image:
    """Correção de luz/contraste/cor proporcional ao quão escura é a foto."""
    arr = img.convert("RGB")
    pontos = [
        arr.getpixel((arr.width // 2, arr.height // 2)),
        arr.getpixel((arr.width // 4, arr.height // 4)),
        arr.getpixel((arr.width * 3 // 4, arr.height // 4)),
        arr.getpixel((arr.width // 4, arr.height * 3 // 4)),
        arr.getpixel((arr.width * 3 // 4, arr.height * 3 // 4)),
    ]
    brilho = sum(sum(p) / 3 for p in pontos) / len(pontos)

    if brilho < 80:        # muito escura (LED roxo da impressora)
        img = ImageEnhance.Brightness(img).enhance(1.55)
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = ImageEnhance.Color(img).enhance(1.30)
    elif brilho < 130:     # moderadamente escura
        img = ImageEnhance.Brightness(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.20)
    else:                  # razoável — ajuste leve
        img = ImageEnhance.Brightness(img).enhance(1.08)
        img = ImageEnhance.Contrast(img).enhance(1.10)
        img = ImageEnhance.Color(img).enhance(1.15)

    return ImageEnhance.Sharpness(img).enhance(1.20)


def _compor_fundo_desfocado(foto: Image.Image, tamanho: tuple,
                            margem: int = 60, blur: int = 40) -> Image.Image:
    """Centraliza a foto nítida sobre um fundo desfocado dela mesma (sem cortar o produto)."""
    W, H = tamanho
    fundo = _redimensionar_com_crop(foto, (W, H)).filter(ImageFilter.GaussianBlur(blur))
    fundo = ImageEnhance.Brightness(fundo).enhance(0.92)

    frente = foto.copy()
    frente.thumbnail((W - margem * 2, H - margem * 2), Image.LANCZOS)
    x = (W - frente.width) // 2
    y = (H - frente.height) // 2
    fundo.paste(frente, (x, y))
    return fundo


def processar_para_feed(caminho_original: str, saida: str = "feed_editada.jpg") -> str:
    """Feed 1080x1080: correção de cor + fundo desfocado (produto inteiro, sem corte)."""
    foto = Image.open(caminho_original).convert("RGB")
    foto = _corrigir_foto(foto)
    img = _compor_fundo_desfocado(foto, FEED_SIZE, margem=50, blur=38)
    img.save(saida, "JPEG", quality=95)
    print(f"[editor] Feed salvo: {saida}")
    return saida


def processar_para_stories(caminho_original: str, saida: str = "stories_editada.jpg") -> str:
    """Stories 1080x1920: correção de cor + fundo desfocado (sem marca/CTA)."""
    foto = Image.open(caminho_original).convert("RGB")
    foto = _corrigir_foto(foto)
    img = _compor_fundo_desfocado(foto, STORIES_SIZE, margem=70, blur=46)
    img.save(saida, "JPEG", quality=95)
    print(f"[editor] Stories salvo: {saida}")
    return saida
