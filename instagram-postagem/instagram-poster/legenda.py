from google import genai
from pathlib import Path
import os

cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
MODELO  = "gemini-flash-latest"

MARCA  = os.getenv("NOME_MARCA", "@pata3d")
IDIOMA = os.getenv("IDIOMA_LEGENDA", "português brasileiro")


def gerar_legenda(nome_arquivo: str, contexto_extra: str = "", caminho_imagem: str = "") -> str:
    prompt = f"""
Você é um especialista em marketing para Instagram da marca {MARCA}, focada em {contexto_extra or "artesanato"}.

Analise a imagem e crie uma legenda profissional e envolvente para o feed do Instagram.

Regras obrigatórias:
- Escreva em {IDIOMA}
- Máximo 150 palavras
- Tom humano, autêntico, não robótico
- Mencione detalhes ESPECÍFICOS do que você vê na imagem (produto, cor, formato, contexto)
- Inclua uma chamada para ação natural (salva, comenta, marca alguém, etc.)
- Termine com 8 a 12 hashtags relevantes e específicas para o produto
- NÃO use aspas nem markdown
- NÃO comece com "Olha" ou "Ei" — seja direto e criativo

Retorne APENAS a legenda pronta para copiar.
""".strip()

    conteudo = [prompt]

    # Usa visão do Gemini se tiver a imagem
    if caminho_imagem and Path(caminho_imagem).exists():
        img_bytes = Path(caminho_imagem).read_bytes()
        conteudo = [
            genai.types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            prompt,
        ]

    resposta = cliente.models.generate_content(model=MODELO, contents=conteudo)
    legenda  = resposta.text.strip()
    print(f"[legenda] Gerada com {len(legenda)} caracteres")
    return legenda


def avaliar_performance(historico: list) -> str:
    if not historico:
        return "Nenhum histórico de posts para analisar ainda."

    linhas = []
    for p in historico:
        linhas.append(
            f"- Arquivo: {p.get('arquivo','?')} | "
            f"Alcance: {p.get('reach',0)} | "
            f"Curtidas: {p.get('likes',0)} | "
            f"Salvamentos: {p.get('saved',0)} | "
            f"Comentários: {p.get('comments',0)} | "
            f"Compartilhamentos: {p.get('shares',0)}"
        )

    prompt = f"""
Você é um analista de redes sociais especialista em Instagram.
Analise o desempenho dos posts abaixo e dê um relatório claro.

Marca: {MARCA}

Posts:
{chr(10).join(linhas)}

Responda em {IDIOMA} com:
1. Qual post performou melhor e por quê
2. O que pode ter contribuído para posts fracos
3. 3 sugestões práticas para os próximos posts
4. Melhor tipo de conteúdo com base nos dados
""".strip()

    resposta = cliente.models.generate_content(model=MODELO, contents=prompt)
    return resposta.text.strip()
