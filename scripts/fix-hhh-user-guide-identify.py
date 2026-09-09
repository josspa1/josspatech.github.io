#!/usr/bin/env python3
"""Fix HHH user-guide Identify/Add shots, narration, and slide wiring.

Canonical player: videos/hhh/user-guide/
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "assets" / "screenshots" / "hhh" / "manual"
GUIDE = ROOT / "videos" / "hhh" / "user-guide"
CACHE = "identify-go-2026-09-08"

NAVY = (91, 35, 51, 255)
NAVY_DARK = (58, 21, 33, 255)
GOLD = (196, 144, 126, 255)
CREAM = (249, 244, 242, 255)
WHITE = (255, 255, 255, 255)
TEXT = (58, 21, 33, 255)
MUTED = (107, 80, 96, 255)
BORDER = (224, 213, 208, 255)

EN_NARRATION = {
    23: "Tap Enter details manually if you want to type the piece in yourself — not Identify.",
    24: "Fill Maker or brand, model, reference, serial, purchase price, and notes.",
    25: "Tap Save to Museum. The piece is in your Owned collection right away.",
    27: "Take one clear dial photo. One photo is enough. Extra shots are optional.",
    29: "If it asks for a movement or caseback photo, skip it unless you have it. Extra photos only help.",
    30: "What do you know is optional. Fill in only what you already have. You do not need the full answer — more you add, the surer the result.",
    31: "Scroll to Wristwatch, Pocket Watch, or Clock if the type is wrong.",
    32: "When you have a photo or even one clue, tap Identify. You can leave the other fields blank.",
    36: "Tap What I know to correct brand or model, then tap Identify again.",
    37: "Tap Save to Museum. HHH creates a museum entry with photos, brand, model, and estimated value filled in.",
}

LOCALE_NARRATION = {
    "de": {
        23: "Tippen Sie auf Details manuell eingeben, wenn Sie das Stück selbst eintippen möchten — nicht auf Identifizieren.",
        24: "Füllen Sie Hersteller oder Marke, Modell, Referenz, Seriennummer, Kaufpreis und Notizen aus.",
        25: "Tippen Sie auf Im Museum speichern. Das Stück ist sofort in Ihrer Sammlung.",
        27: "Tippen Sie auf Foto 1: Zifferblatt. Fotografieren Sie das Zifferblatt gerade und gleichmäßig beleuchtet — ein klares Foto reicht zum Start.",
        29: "Wenn HHH nach einem Werkfoto fragt, fügen Sie eines hinzu — oder überspringen Sie und fahren Sie mit dem Zifferblatt fort.",
        31: "Scrollen Sie zu Armbanduhr, Taschenuhr oder Uhr, falls der Typ falsch ist.",
        32: "Scrollen Sie an Marke und Modell vorbei. Tippen Sie auf Identifizieren. Warten Sie, während es arbeitet.",
        36: "Tippen Sie auf Was ich weiß, um Marke oder Modell zu korrigieren, und dann erneut auf Identifizieren.",
        37: "Tippen Sie auf Im Museum speichern. HHH legt einen Museumseintrag mit Fotos, Marke, Modell und Schätzwert an.",
    },
    "es": {
        23: "Toque Introducir datos manualmente si quiere escribir la pieza usted — no Identificar.",
        24: "Complete fabricante o marca, modelo, referencia, serie, precio de compra y notas.",
        25: "Toque Guardar en el Museo. La pieza queda en su colección de inmediato.",
        27: "Toque Foto 1: Esfera. Encuadre la esfera de frente con luz uniforme — una foto clara basta para empezar.",
        29: "Si HHH pide una foto del movimiento, añádala — o omita y siga solo con la esfera.",
        31: "Desplácese hasta Reloj de pulsera, Reloj de bolsillo o Reloj si el tipo es incorrecto.",
        32: "Baje más allá de marca y modelo. Toque Identificar. Espere mientras trabaja.",
        36: "Toque Lo que sé para corregir marca o modelo y vuelva a toque Identificar.",
        37: "Toque Guardar en el Museo. HHH crea una ficha con fotos, marca, modelo y valor estimado.",
    },
    "fr": {
        23: "Appuyez sur Saisir les détails manuellement pour taper la pièce vous-même — pas Identifier.",
        24: "Remplissez fabricant ou marque, modèle, référence, numéro de série, prix d'achat et notes.",
        25: "Appuyez sur Enregistrer au musée. La pièce est tout de suite dans votre collection.",
        27: "Appuyez sur Photo 1 : Cadran. Cadrez le cadran de face, lumière uniforme — une photo nette suffit pour commencer.",
        29: "Si HHH demande une photo du mouvement, ajoutez-en une — ou passez et continuez avec le cadran.",
        31: "Faites défiler jusqu'à Montre-bracelet, Montre de poche ou Horloge si le type est faux.",
        32: "Descendez sous la marque et le modèle. Appuyez sur Identifier. Attendez pendant que ça travaille.",
        36: "Appuyez sur Ce que je sais pour corriger la marque ou le modèle, puis Identifier à nouveau.",
        37: "Appuyez sur Enregistrer au musée. HHH crée une fiche avec photos, marque, modèle et estimation.",
    },
    "it": {
        23: "Tocca Inserisci i dettagli manualmente se vuoi digitare il pezzo tu — non Identifica.",
        24: "Compila produttore o marca, modello, referenza, seriale, prezzo di acquisto e note.",
        25: "Tocca Salva nel Museo. Il pezzo è subito nella tua collezione.",
        27: "Tocca Foto 1: Quadrante. Inquadra il quadrante frontale con luce uniforme — una foto nitida basta per iniziare.",
        29: "Se HHH chiede una foto del movimento, aggiungila — oppure salta e continua con il quadrante.",
        31: "Scorri fino a Orologio da polso, Orologio da tasca o Orologio se il tipo è sbagliato.",
        32: "Scorri oltre marca e modello. Tocca Identifica. Attendi mentre lavora.",
        36: "Tocca Quello che so per correggere marca o modello, poi di nuovo Identifica.",
        37: "Tocca Salva nel Museo. HHH crea una scheda con foto, marca, modello e valore stimato.",
    },
    "pt": {
        23: "Toque em Inserir detalhes manualmente se quiser escrever a peça você mesmo — não Identificar.",
        24: "Preencha fabricante ou marca, modelo, referência, série, preço de compra e notas.",
        25: "Toque em Guardar no Museu. A peça fica na sua coleção de imediato.",
        27: "Toque em Foto 1: Mostrador. Enquadre o mostrador de frente com luz uniforme — uma foto nítida chega para começar.",
        29: "Se o HHH pedir uma foto do movimento, adicione — ou ignore e continue só com o mostrador.",
        31: "Deslize até Relógio de pulso, Relógio de bolso ou Relógio se o tipo estiver errado.",
        32: "Desça além da marca e do modelo. Toque em Identificar. Espere enquanto trabalha.",
        36: "Toque em O que eu sei para corrigir marca ou modelo e toque Identificar outra vez.",
        37: "Toque em Guardar no Museu. O HHH cria uma ficha com fotos, marca, modelo e valor estimado.",
    },
    "zh": {
        23: "若要自己填写，请点「手动输入详情」，不要点鉴定。",
        24: "填写品牌、型号、参考号、序列号、购入价和备注。",
        25: "点「保存到博物馆」。藏品会立即出现在已拥有列表中。",
        27: "点「照片 1：表盘」。正面、光线均匀拍一张清晰表盘即可开始。",
        29: "如果提示补拍机芯照片，可以添加，也可以跳过、只用表盘继续。",
        31: "如类型不对，请滑到腕表、怀表或时钟再选。",
        32: "滑过品牌和型号。点「鉴定」。等待完成即可。",
        36: "点「我所知道的」更正品牌或型号，再点一次鉴定。",
        37: "点「保存到博物馆」。会生成带照片、品牌、型号和估值的藏品条目。",
    },
    "hi": {
        23: "अगर आप खुद टाइप करना चाहते हैं तो विवरण मैन्युअल दर्ज करें टैप करें — पहचानें नहीं।",
        24: "निर्माता या ब्रांड, मॉडल, रेफरेंस, सीरियल, खरीद मूल्य और नोट भरें।",
        25: "संग्रहालय में सहेजें टैप करें। पीस तुरंत आपकी कलेक्शन में आ जाता है।",
        27: "फोटो 1: डायल टैप करें। डायल को सामने से समान रोशनी में फ्रेम करें — शुरू करने के लिए एक साफ फोटो काफी है।",
        29: "अगर एचएचएच मूवमेंट फोटो मांगे तो जोड़ें — या छोड़कर केवल डायल से जारी रखें।",
        31: "अगर प्रकार गलत हो तो कलाई घड़ी, पॉकेट वॉच या घड़ी तक स्क्रॉल करें।",
        32: "ब्रांड और मॉडल के नीचे स्क्रॉल करें। पहचानें टैप करें। काम पूरा होने तक रुकें।",
        36: "ब्रांड या मॉडल सुधारने के लिए मैं जो जानता हूँ टैप करें, फिर फिर से पहचानें।",
        37: "संग्रहालय में सहेजें टैप करें। एचएचएच फोटो, ब्रांड, मॉडल और अनुमानित मूल्य के साथ प्रविष्टि बनाता है।",
    },
}

SLIDE_PATCHES = {
    23: {
        "attrs": 'data-index="23" data-tap-x="50" data-tap-y="58" data-tap-label="Enter details manually" data-tap-show-at="0.2" data-tap-duration="3.2"',
        "src": f"/assets/screenshots/hhh/manual/07f-add-choice.png?v={CACHE}",
        "alt": "Enter details manually",
    },
    24: {
        "attrs": 'data-index="24" data-tap-x="50" data-tap-y="42" data-tap-label="Maker or brand" data-tap-show-at="0.2" data-tap-duration="3.2"',
        "src": f"/assets/screenshots/hhh/manual/07g-manual-add.png?v={CACHE}",
        "alt": "Fill Maker or brand",
    },
    25: {
        "attrs": 'data-index="25" data-tap-x="50" data-tap-y="86" data-tap-label="Save to Museum" data-tap-show-at="0.2" data-tap-duration="2.8"',
        "src": f"/assets/screenshots/hhh/manual/07g-manual-add.png?v={CACHE}",
        "alt": "Save to Museum",
    },
    27: {
        "attrs": 'data-index="27" data-tap-x="27" data-tap-y="50" data-tap-label="Photo 1: Dial" data-tap-show-at="0.2" data-tap-duration="3.2"',
        "src": f"/assets/screenshots/hhh/manual/07a-identify-camera.png?v={CACHE}",
        "alt": "Photo 1: Dial",
    },
    31: {
        "attrs": 'data-index="31" data-tap-x="28" data-tap-y="72" data-tap-label="Wristwatch" data-tap-show-at="0.2" data-tap-duration="3.0"',
        "src": f"/assets/screenshots/hhh/manual/07e-identify-go.png?v={CACHE}",
        "alt": "Wristwatch Pocket Watch Clock",
    },
    32: {
        "attrs": 'data-index="32" data-tap-x="50" data-tap-y="82" data-tap-label="Identify" data-tap-show-at="0.2" data-tap-duration="3.4"',
        "src": f"/assets/screenshots/hhh/manual/07e-identify-go.png?v={CACHE}",
        "alt": "Tap Identify",
    },
    37: {
        "attrs": 'data-index="37" data-tap-x="30" data-tap-y="85" data-tap-label="Save to Museum" data-tap-show-at="0.2" data-tap-duration="3.2"',
        "src": f"/assets/screenshots/hhh/manual/07-identify-results.png?v={CACHE}",
        "alt": "Save to Museum",
    },
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ("seguiemj.ttf", "C:/Windows/Fonts/segoeui.ttf"),
        ("segoeuib.ttf", "C:/Windows/Fonts/segoeuib.ttf") if bold else ("segoeui.ttf", "C:/Windows/Fonts/segoeui.ttf"),
    )
    path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def round_rect(draw: ImageDraw.ImageDraw, box, fill, radius: int, outline=None, width: int = 2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw, xy, text, fnt, fill):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw / 2, y - th / 2), text, font=fnt, fill=fill)


def make_identify_go() -> None:
    src = Image.open(MANUAL / "07a-identify-camera.png").convert("RGBA")
    w, h = src.size
    header_end = 400
    hero_end = 980
    tabs_start = 2760
    body = src.crop((0, hero_end, w, tabs_start))
    out = Image.new("RGBA", (w, h), CREAM)
    out.paste(src.crop((0, 0, w, header_end)), (0, 0))
    out.paste(body, (0, header_end))
    body_bottom = header_end + body.size[1]
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, body_bottom, w, tabs_start), fill=CREAM)

    pad = 72
    chip_y = body_bottom + 36
    chip_h = 88
    labels = ["Wristwatch", "Pocket Watch", "Clock"]
    gap = 18
    chip_w = (w - pad * 2 - gap * 2) // 3
    for i, label in enumerate(labels):
        x0 = pad + i * (chip_w + gap)
        box = (x0, chip_y, x0 + chip_w, chip_y + chip_h)
        if i == 0:
            round_rect(draw, box, NAVY, 44)
            text_center(draw, ((x0 + x0 + chip_w) / 2, chip_y + chip_h / 2), label, font(28, True), WHITE)
        else:
            round_rect(draw, box, WHITE, 44, outline=BORDER, width=3)
            text_center(draw, ((x0 + x0 + chip_w) / 2, chip_y + chip_h / 2), label, font(28, False), MUTED)

    btn_y = chip_y + chip_h + 40
    btn_h = 132
    round_rect(draw, (pad, btn_y, w - pad, btn_y + btn_h), GOLD, 28)
    text_center(draw, (w / 2 + 18, btn_y + btn_h / 2), "Identify", font(42, True), NAVY_DARK)
    # simple magnifier mark
    cx, cy = w / 2 - 118, btn_y + btn_h / 2
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), outline=NAVY_DARK, width=5)
    draw.line((cx + 14, cy + 14, cx + 28, cy + 28), fill=NAVY_DARK, width=5)

    out.paste(src.crop((0, tabs_start, w, h)), (0, tabs_start))
    dest = MANUAL / "07e-identify-go.png"
    out.convert("RGB").save(dest, "PNG", optimize=True)
    print(f"wrote {dest} Identify-button y%={int(100 * (btn_y + btn_h / 2) / h)}")


def make_add_choice() -> None:
    src = Image.open(MANUAL / "02-museum-collection.png").convert("RGBA")
    w, h = src.size
    dim = Image.new("RGBA", (w, h), (20, 8, 12, 140))
    out = Image.alpha_composite(src, dim)
    draw = ImageDraw.Draw(out)
    sheet_top = int(h * 0.48)
    round_rect(draw, (48, sheet_top, w - 48, h - 220), WHITE, 36)
    rows = [
        ("Identify from photos", False),
        ("Enter details manually", True),
        ("Import an estate or batch", False),
    ]
    y = sheet_top + 70
    for label, active in rows:
        box = (90, y, w - 90, y + 150)
        if active:
            round_rect(draw, box, (255, 244, 236, 255), 24, outline=GOLD, width=4)
        else:
            round_rect(draw, box, CREAM, 24)
        text_center(draw, (w / 2, y + 75), label, font(36, True), NAVY_DARK if active else TEXT)
        y += 180
    dest = MANUAL / "07f-add-choice.png"
    out.convert("RGB").save(dest, "PNG", optimize=True)
    print(f"wrote {dest}")


def make_manual_add() -> None:
    src = Image.open(MANUAL / "07a-identify-camera.png").convert("RGBA")
    w, h = src.size
    out = Image.new("RGBA", (w, h), CREAM)
    out.paste(src.crop((0, 0, w, 360)), (0, 0))
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 360, w, 2760), fill=CREAM)
    title_f = font(52, True)
    draw.text((72, 420), "Add to Museum", font=title_f, fill=TEXT)
    draw.text((72, 500), "Add a piece directly on this device.", font=font(30), fill=MUTED)

    def field(y: int, label: str, hint: str, value: str = ""):
        draw.text((72, y), label.upper(), font=font(22, True), fill=MUTED)
        round_rect(draw, (72, y + 40, w - 72, y + 148), WHITE, 18, outline=BORDER, width=3)
        draw.text((96, y + 72), value or hint, font=font(32), fill=TEXT if value else (180, 168, 164, 255))

    field(600, "Maker or brand", "Citizen, Omega...")
    field(820, "Model or name", "Promaster, Seamaster...")
    field(1040, "Reference number", "Optional")
    field(1260, "Serial number", "Optional")
    field(1480, "Purchase price", "0.00")

    round_rect(draw, (72, 1780, w - 72, 1930), GOLD, 28)
    text_center(draw, (w / 2, 1855), "Save to Museum", font(40, True), NAVY_DARK)
    out.paste(src.crop((0, 2760, w, h)), (0, 2760))
    dest = MANUAL / "07g-manual-add.png"
    out.convert("RGB").save(dest, "PNG", optimize=True)
    print(f"wrote {dest}")


def patch_slide(html: str, idx: int, spec: dict) -> str:
    pattern = rf'<div class="slide(?: active)?"[^>]*data-index="{idx}"[^>]*>\s*<img src="[^"]+" alt="[^"]+"[^>]*>\s*</div>'
    replacement = (
        f'<div class="slide" {spec["attrs"]}>\n'
        f' <img src="{spec["src"]}" alt="{spec["alt"]}" loading="lazy">\n'
        f' </div>'
    )
    new_html, n = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"slide {idx} not patched uniquely ({n})")
    return new_html


def sync_narration_const(html: str, narr: list[str]) -> str:
    new_html, n = re.subn(
        r"const NARRATION = \[.*?\];",
        "const NARRATION = " + json.dumps(narr, ensure_ascii=False) + ";",
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("NARRATION const not patched")
    return new_html


def patch_chrome(html: str) -> str:
    html = html.replace(' target="_blank" rel="noopener"', "")
    html = html.replace(
        "html.embed-mode .walkthrough h2,\n         html.embed-mode .walkthrough .section-sub,\n         html.embed-mode .walkthrough .prod-media-langs,\n         html.embed-mode .progress-dots,\n         html.embed-mode .chapter-nav { display: none !important; }",
        "html.embed-mode .walkthrough h2,\n         html.embed-mode .walkthrough .section-sub,\n         html.embed-mode .progress-dots { display: none !important; }",
    )
    html = html.replace(
        "html.embed-mode .walkthrough h2,\n         html.embed-mode .walkthrough .section-sub,\n         html.embed-mode .walkthrough .prod-media-langs,\n         html.embed-mode .progress-dots,\n         html.embed-mode .chapter-nav { display: none !important; }",
        "html.embed-mode .walkthrough h2,\n         html.embed-mode .walkthrough .section-sub,\n         html.embed-mode .progress-dots { display: none !important; }",
    )
    # locale copies indent with 9 spaces sometimes
    html = re.sub(
        r"html\.embed-mode \.walkthrough h2,\s*html\.embed-mode \.walkthrough \.section-sub,\s*html\.embed-mode \.walkthrough \.prod-media-langs,\s*html\.embed-mode \.progress-dots,\s*html\.embed-mode \.chapter-nav \{ display: none !important; \}",
        "html.embed-mode .walkthrough h2,\n         html.embed-mode .walkthrough .section-sub,\n         html.embed-mode .progress-dots { display: none !important; }",
        html,
    )
    html = html.replace("walkthrough.css?v=chapters-above-2026-07-28", f"walkthrough.css?v={CACHE}")
    html = html.replace("deck.js?v=chapters-above-2026-07-28", f"deck.js?v={CACHE}")
    html = re.sub(
        r'(<p class="subheader">)(.*?)(</p>)',
        r"\1Pick a language and a chapter, then play. Gold pulses mark each tap.\3",
        html,
        count=1,
        flags=re.S,
    )
    return html


def patch_html_file(path: Path, narr: list[str]) -> None:
    html = path.read_text(encoding="utf-8")
    for idx, spec in SLIDE_PATCHES.items():
        html = patch_slide(html, idx, spec)
    html = patch_chrome(html)
    html = sync_narration_const(html, narr)
    path.write_text(html, encoding="utf-8")
    print(f"patched {path}")


def update_json(path: Path, updates: dict[int, str]) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for i, text in updates.items():
        data[i] = text
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {path}")
    return data


def main() -> None:
    make_identify_go()
    make_add_choice()
    make_manual_add()
    en = update_json(GUIDE / "narration-en.json", EN_NARRATION)
    patch_html_file(GUIDE / "index.html", en)
    for code, updates in LOCALE_NARRATION.items():
        loc = GUIDE / code
        narr_path = loc / f"narration-{code}.json"
        texts = update_json(narr_path, updates)
        patch_html_file(loc / "index.html", texts)
        # keep locale player JS/CSS in lockstep with EN
        for name in ("deck.js", "walkthrough.css"):
            src = GUIDE / name
            dest = loc / name
            if src.exists():
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
