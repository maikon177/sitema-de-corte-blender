from __future__ import annotations

import hashlib
import json
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def make_schedule(index: int) -> tuple[str, str]:
    slots = [
        ("manha", "08:12 • Bom dia / leve"),
        ("tarde", "14:40 • Post principal"),
        ("noite", "20:18 • Reel / destaque"),
    ]
    return slots[index % len(slots)]


def hashtags_for_text(source_label: str, is_encomenda: bool) -> list[str]:
    base = ["pata3d", "confeitaria", "docespersonalizados", "biscoitosdecorados"]
    if is_encomenda:
        base += ["encomenda", "feitocomcarinho", "detalhesqueencantam"]
    if "grupo" in source_label.lower():
        base += ["carrossel", "colecao", "modelinhos"]
    else:
        base += ["cortadores", "carimbo", "ejetor"]
    return base


def infer_tags_from_name(name: str) -> set[str]:
    text = name.lower()
    tags: set[str] = set()
    if any(word in text for word in ["flor", "flower", "margarida"]):
        tags.add("floral")
    if any(word in text for word in ["laco", "laço", "bow"]):
        tags.add("laco")
    if any(word in text for word in ["arco", "rainbow"]):
        tags.add("arco")
    if any(word in text for word in ["cereja", "cherry"]):
        tags.add("fruta")
    if any(word in text for word in ["coelho", "bunny", "pascoa", "páscoa"]):
        tags.add("pascoa")
    if any(word in text for word in ["embal", "saquinho", "pedido", "encomenda"]):
        tags.add("embalado")
    if any(word in text for word in ["fofo", "urso", "boneco", "personagem"]):
        tags.add("fofo")
    return tags


def infer_tags_from_media(media_files: list[Path]) -> set[str]:
    tags: set[str] = set()
    for path in media_files:
        tags.update(infer_tags_from_name(path.stem))
    return tags


def choose_variant(options: list[str], seed_text: str) -> str:
    if not options:
        return ""
    digest = hashlib.sha1(seed_text.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)
    return options[seed % len(options)]


def title_for_post(source_label: str, tags: set[str], media_count: int) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return "Carrossel de encomenda"
        if "fofo" in tags:
            return "Carrossel de modelinhos"
        return "Carrossel de produtos"

    if "floral" in tags:
        return "Modelinho floral"
    if "laco" in tags:
        return "Modelinho com laço"
    if "arco" in tags:
        return "Modelinho de arco"
    if "fruta" in tags:
        return "Modelinho delicado"
    return source_label


def overlay_for_context(schedule_slot: str, media_count: int, is_encomenda: bool, tags: set[str]) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return "Olha essa encomenda 😍"
        if "fofo" in tags:
            return "Um modelinho mais lindo que o outro ✨"
        return "Passando pra mostrar essa coleção 💖"

    if schedule_slot == "manha":
        if "fofo" in tags:
            return "Bom dia com fofura por aqui ✨"
        return "Bom dia com inspiração doce ✨"
    if "floral" in tags:
        return "Delicadeza em cada detalhe 🌸"
    if "laco" in tags:
        return "Olha esse charme 🎀"
    if "arco" in tags:
        return "Mais um modelinho encantador 🌈"
    if "fruta" in tags:
        return "Detalhes que encantam 🍒"
    if is_encomenda:
        return "Mais um pedido feito com carinho 💖"
    return "Passando pra mostrar essa lindeza 😍"


def reel_overlay_text(source_label: str, tags: set[str], is_encomenda: bool, seed_text: str) -> str:
    if "embalado" in tags:
        return choose_variant(
            [
                "encomenda passando na sua tela 🥹",
                "olha esse pedido prontinho 💕",
                "mais uma entrega linda por aqui ✨",
                "detalhe simples mas faz diferença 🥹",
            ],
            seed_text,
        )
    if "floral" in tags:
        return choose_variant(
            [
                "esse detalhe floral ficou um charme 🌸",
                "bem delicadinho do jeitinho que amamos ✨",
                "florzinha linda pra dar destaque 💗",
                "só um toque e já mudou tudo 🥹",
            ],
            seed_text,
        )
    if "laco" in tags:
        return choose_variant(
            [
                "um lacinho e pronto: ficou lindo 🎀",
                "laço fofo pra dar aquele charme 💕",
                "detalhe pequeno mas faz diferença ✨",
                "essa legendinha aqui é só pra dar destaque 🥹",
            ],
            seed_text,
        )
    if "arco" in tags:
        return choose_variant(
            [
                "esse modelinho alegra qualquer produção 🌈",
                "olha esse charme bem delicadinho 🥹",
                "pequeno destaque que muda tudo ✨",
                "bem bobinha mas ficou fofa 💕",
            ],
            seed_text,
        )
    if is_encomenda:
        return choose_variant(
            [
                "mais uma encomenda linda por aqui 💕",
                "feito com carinho pra encantar ✨",
                "esses detalhes fazem toda diferença 🥹",
                "legendinha curta só pra dar destaque 💕",
            ],
            seed_text,
        )
    return choose_variant(
        [
            "olha essa delicadeza ✨",
            "bem pequenininho e cheio de charme 💕",
            "só pra dar aquele destaque 🥹",
            "uma bobinha só pra destacar ✨",
        ],
        seed_text,
    )


def caption_for_post(
    source_label: str,
    media_count: int,
    is_encomenda: bool,
    tags: set[str],
    schedule_slot: str,
    seed_text: str,
) -> str:
    if media_count > 1:
        if "embalado" in tags:
            return choose_variant(
                [
                    "Passando pra mostrar uma encomenda cheia de detalhes lindos. Esses modelinhos ficam perfeitos para valorizar ainda mais suas produções 💖",
                    "Esses modelinhos foram juntos para uma encomenda especial e o resultado ficou um encanto. Perfeito para deixar a produção ainda mais delicada ✨",
                    "Tem encomenda que merece aparecer por aqui, e essa é uma delas. Vários detalhes lindos para inspirar produções cheias de carinho 🌸",
                ],
                seed_text,
            )
        if "fofo" in tags:
            return choose_variant(
                [
                    "Quando os modelinhos conversam entre si, a produção fica ainda mais encantadora. Ótima inspiração para quem ama variedade com delicadeza ✨",
                    "Esses modelinhos juntos deixam qualquer produção com mais personalidade. Uma combinação linda para encantar nas encomendas 💕",
                    "Separei esses modelinhos porque a combinação deles ficou uma graça. Perfeito para quem gosta de variar sem perder delicadeza 🥹",
                ],
                seed_text,
            )
        return choose_variant(
            [
                "Separei esses modelinhos juntos porque eles combinam super bem entre si. Perfeito para compor produções cheias de personalidade 🌸",
                "Quando a gente junta modelinhos que conversam entre si, a produção ganha outro charme. Uma ótima inspiração para encomendas delicadas ✨",
                "Essas combinações deixam a produção mais rica e mais bonita visualmente. Ideia linda para quem ama caprichar nos detalhes 💖",
            ],
            seed_text,
        )

    if "floral" in tags:
        return choose_variant(
            [
                "Esse modelinho floral é daquele tipo que deixa qualquer produção mais delicada. Uma graça para doces que pedem acabamento especial 🌸",
                "Detalhes florais sempre trazem um charme extra para a produção. Um modelinho lindo para quem ama delicadeza 🌼",
                "Tem modelinho que já transmite delicadeza só de olhar. Esse floral é perfeito para produções com toque mais romântico 🌸",
            ],
            seed_text,
        )
    if "laco" in tags:
        return choose_variant(
            [
                "Laço é aquele detalhe que transforma a produção e deixa tudo com mais charme. Perfeito para encomendas delicadas e cheias de carinho 🎀",
                "Esse modelinho com laço é uma graça para deixar a produção mais delicada e com acabamento encantador 🎀",
                "Tem detalhe que faz toda a diferença na produção, e o laço é um deles. Fica lindo em encomendas fofas e caprichadas 💖",
            ],
            seed_text,
        )
    if "arco" in tags:
        return choose_variant(
            [
                "Tem modelinho que já chama atenção só de bater o olho, e esse é um deles. Lindo para produções alegres e cheias de encanto 🌈",
                "Esse modelinho traz um ar alegre e delicado para a produção. Uma graça para doces com proposta mais leve e encantadora ✨",
                "Quando a ideia é deixar a produção mais fofa e marcante, esse tipo de modelinho faz toda diferença 🌈",
            ],
            seed_text,
        )
    if "fruta" in tags:
        return choose_variant(
            [
                "Os detalhes pequenos fazem toda diferença no resultado final. Esse modelinho é uma graça para deixar a produção ainda mais especial 🍒",
                "Um detalhezinho assim já muda a cara da produção e deixa tudo mais encantador. Lindo para doces delicados 🍒",
                "Esse modelinho é daquele tipo que traz charme sem pesar. Ótimo para composições leves e cheias de carinho ✨",
            ],
            seed_text,
        )
    if schedule_slot == "manha":
        return choose_variant(
            [
                "Começando o dia com uma inspiração linda por aqui. Porque até os pequenos detalhes fazem diferença na hora de encantar 💕",
                "Bom dia com um modelinho que é pura delicadeza. Ideia linda para inspirar produções cheias de carinho ✨",
                "Passando cedo por aqui para deixar uma inspiração doce no feed. Pequenos detalhes fazem toda diferença 🥹",
            ],
            seed_text,
        )
    if is_encomenda:
        return choose_variant(
            [
                "Mais uma encomenda feita com carinho e pensada para deixar cada doce ainda mais especial. É esse tipo de detalhe que valoriza a produção ✨",
                "Essa peça entrou em uma encomenda linda por aqui e ficou um charme. Detalhes assim fazem a produção ganhar ainda mais valor 💖",
                "Passando pra mostrar mais um modelinho de encomenda que ficou uma graça. É esse cuidado nos detalhes que encanta o cliente final 🌸",
            ],
            seed_text,
        )
    return choose_variant(
        [
            "Olha só esse modelinho passando no feed. Ideal para quem ama produzir com mais personalidade e deixar cada doce ainda mais especial 💕",
            "Esse modelinho é uma inspiração linda para quem gosta de caprichar na produção e encantar nos detalhes ✨",
            "Tem peça que já chama atenção pela delicadeza. Essa é uma daquelas ideias que deixam a produção ainda mais bonita 🌸",
        ],
        seed_text,
    )


def media_kind(path: Path) -> str:
    return "video" if path.suffix.lower() in VIDEO_EXTENSIONS else "image"


def all_media_files(folder: Path) -> list[Path]:
    return sorted(
        [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS],
        key=lambda p: p.name.lower(),
    )


def build_media_entries(root_media_dir: Path, media_files: list[Path]) -> list[dict[str, str]]:
    return [
        {
            "name": path.name,
            "kind": media_kind(path),
            "relative_path": path.relative_to(root_media_dir).as_posix(),
        }
        for path in media_files
    ]


def build_draft_payload(root_media_dir: Path, profile: str = "@pata3d", max_extra_reels: int = 8) -> dict[str, object]:
    root_media_dir = root_media_dir.resolve()
    posts: list[dict[str, object]] = []
    post_index = 0

    root_files = all_media_files(root_media_dir)
    for media_path in root_files:
        slot, schedule_label = make_schedule(post_index)
        source_label = "pata3d_cortadores"
        is_encomenda = True
        tags = infer_tags_from_name(media_path.stem)
        posts.append(
            {
                "id": f"post-{post_index}",
                "title": title_for_post(media_path.stem, tags, 1),
                "post_type": "single",
                "post_type_label": "Post único",
                "preview_type": "feed",
                "schedule_slot": slot,
                "schedule_label": schedule_label,
                "overlay_text": overlay_for_context(slot, 1, is_encomenda, tags),
                "reel_overlay_text": reel_overlay_text(source_label, tags, is_encomenda, f"{media_path.stem}-{post_index}-reel"),
                "caption": caption_for_post(source_label, 1, is_encomenda, tags, slot, f"{media_path.stem}-{post_index}"),
                "hashtags": hashtags_for_text(source_label, is_encomenda),
                "source_label": source_label,
                "mock_likes": 108 + post_index * 13,
                "tags": sorted(tags),
                "media": build_media_entries(root_media_dir, [media_path]),
            }
        )
        post_index += 1

    for folder in sorted([path for path in root_media_dir.iterdir() if path.is_dir()], key=lambda p: p.name.lower()):
        media_files = all_media_files(folder)
        if not media_files:
            continue

        slot, schedule_label = make_schedule(post_index)
        source_label = folder.name
        is_encomenda = True
        tags = infer_tags_from_media(media_files)
        preview_type = "reel" if any(path.suffix.lower() in VIDEO_EXTENSIONS for path in media_files) else "feed"
        posts.append(
            {
                "id": f"post-{post_index}",
                "title": title_for_post(folder.name, tags, len(media_files)),
                "post_type": "carousel" if len(media_files) > 1 else "single",
                "post_type_label": "Carrossel" if len(media_files) > 1 else "Post único",
                "preview_type": preview_type,
                "schedule_slot": slot,
                "schedule_label": schedule_label,
                "overlay_text": overlay_for_context(slot, len(media_files), is_encomenda, tags),
                "reel_overlay_text": reel_overlay_text(source_label, tags, is_encomenda, f"{folder.name}-{post_index}-reel"),
                "caption": caption_for_post(source_label, len(media_files), is_encomenda, tags, slot, f"{folder.name}-{post_index}"),
                "hashtags": hashtags_for_text(source_label, is_encomenda),
                "source_label": source_label,
                "mock_likes": 172 + post_index * 17,
                "tags": sorted(tags),
                "media": build_media_entries(root_media_dir, media_files),
            }
        )
        post_index += 1

    extra_reels: list[dict[str, object]] = []
    for source_post in list(posts):
        if len(extra_reels) >= max_extra_reels:
            break
        if not source_post["media"]:
            continue
        first_media = source_post["media"][0]
        extra_reels.append(
            {
                "id": f"{source_post['id']}-reel",
                "title": f"Reel • {source_post['title']}",
                "post_type": "reel_mock",
                "post_type_label": "Reel de teste",
                "preview_type": "reel",
                "schedule_slot": source_post["schedule_slot"],
                "schedule_label": source_post["schedule_label"],
                "overlay_text": source_post["overlay_text"],
                "reel_overlay_text": source_post.get("reel_overlay_text", source_post["overlay_text"]),
                "caption": source_post["caption"],
                "hashtags": source_post["hashtags"],
                "source_label": source_post["source_label"],
                "mock_likes": source_post["mock_likes"],
                "tags": source_post["tags"],
                "media": [first_media],
            }
        )

    posts.extend(extra_reels)
    return {
        "profile": profile,
        "root_media_dir": str(root_media_dir),
        "posts": posts,
    }


def save_draft_payload(root_media_dir: Path, output_path: Path, profile: str = "@pata3d") -> Path:
    payload = build_draft_payload(root_media_dir, profile=profile)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    default_root = Path(__file__).resolve().parent / "fotos" / "pata3d_cortadores"
    default_output = Path(__file__).resolve().parent / "dados" / "rascunhos_pata3d_cortadores.json"
    saved = save_draft_payload(default_root, default_output)
    print(f"Rascunhos salvos em: {saved}")
