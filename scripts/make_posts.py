"""Generate Instagram post images (1080x1350 JPEG, 4:5) for Glimmer.

Source product photos: assets/products/ (downloaded from cosmeticshop.md/glimmer).
Output: posts/<post>/<n>.jpg
Run: python3 scripts/make_posts.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "products"
OUT = ROOT / "posts"

W, H = 1080, 1350
BLACK = (17, 17, 17)
WHITE = (255, 255, 255)
SILVER = (196, 198, 202)
GREY = (120, 122, 126)

SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def product(name):
    return Image.open(SRC / f"{name}.png").convert("RGB")


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            test = f"{line} {word}".strip()
            if draw.textlength(test, font=fnt) <= max_w:
                line = test
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_lines(draw, xy, lines, fnt, fill, spacing=1.25, anchor_center=False):
    x, y = xy
    step = int(fnt.size * spacing)
    for line in lines:
        if anchor_center:
            draw.text((W // 2, y), line, font=fnt, fill=fill, anchor="ma")
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def wordmark(canvas, y, fill=BLACK, size=56):
    """Paste the official logo (assets/logo-*.png), centred, ~size px x-height scale."""
    logo = Image.open(ROOT / "assets" / ("logo-white.png" if fill == WHITE else "logo-black.png"))
    w = size * 5
    logo = logo.resize((w, int(logo.height * w / logo.width)), Image.LANCZOS)
    canvas.paste(logo, ((W - w) // 2, y), logo)


def product_card(images, headline, sub, tag=None):
    """White top with product shot(s), black panel with headline at the bottom."""
    canvas = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(canvas)
    wordmark(canvas, 40)

    panel_top = 930
    area_h = panel_top - 140
    area_w = W - 80
    shots = [product(n) for n in images]
    # product photos are 4:5 on white; crop side margins so pairs sit close together
    shots = [s.crop((int(s.width * 0.12), 0, int(s.width * 0.88), s.height)) for s in shots]
    scale = min(area_h / shots[0].height, area_w / sum(s.width for s in shots))
    total_w = sum(int(s.width * scale) for s in shots)
    x = (W - total_w) // 2
    for s in shots:
        s = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
        canvas.paste(s, (x, 120))
        x += s.width

    d.rectangle((0, panel_top, W, H), fill=BLACK)
    if tag:
        d.text((72, panel_top + 52), tag.upper(), font=font(SANS_BOLD, 26), fill=SILVER)
    y = panel_top + (100 if tag else 64)
    y = draw_lines(d, (72, y), wrap(d, headline.upper(), font(SANS_BOLD, 64), W - 144),
                   font(SANS_BOLD, 64), WHITE, spacing=1.08)
    draw_lines(d, (72, y + 18), wrap(d, sub, font(SANS, 34), W - 144), font(SANS, 34), SILVER)
    d.text((W - 72, H - 50), "cosmeticshop.md", font=font(SANS, 26), fill=GREY, anchor="rs")
    return canvas


def text_slide(kicker, headline, bullets, dark=True):
    bg, fg, muted = (BLACK, WHITE, SILVER) if dark else ((236, 237, 239), BLACK, GREY)
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    wordmark(canvas, 80, fill=fg)
    hf, bf = font(SANS_BOLD, 84), font(SANS, 46)
    head = wrap(d, headline, hf, W - 180)
    blines = [wrap(d, b, bf, W - 240) for b in bullets]
    block = 60 + len(head) * int(hf.size * 1.1) + 60 + sum(len(b) * int(bf.size * 1.25) + 26 for b in blines)
    y = (H - block) // 2
    d.text((90, y), kicker.upper(), font=font(SANS_BOLD, 32), fill=muted)
    y = draw_lines(d, (90, y + 60), head, hf, fg, spacing=1.1) + 60
    for b in blines:
        d.text((90, y), "/", font=font(SANS_BOLD, 46), fill=muted)
        y = draw_lines(d, (150, y), b, bf, fg) + 26
    d.text((W // 2, H - 80), "cosmeticshop.md", font=font(SANS, 28), fill=muted, anchor="ma")
    return canvas


def cover_photo(name, headline, sub):
    """Lifestyle photo on top, black panel with headline below."""
    panel_top = 900
    src = product(name)
    th = src.height
    tw = int(th * W / panel_top)
    left = (src.width - tw) // 2 + 40
    photo = src.crop((left, 0, left + tw, th)).resize((W, panel_top), Image.LANCZOS)
    img = Image.new("RGB", (W, H), BLACK)
    img.paste(photo, (0, 0))
    d = ImageDraw.Draw(img)
    wordmark(img, panel_top + 45, fill=WHITE, size=60)
    y = draw_lines(d, (0, panel_top + 150), wrap(d, headline, font(SANS_BOLD, 60), W - 144),
                   font(SANS_BOLD, 60), WHITE, spacing=1.1, anchor_center=True)
    draw_lines(d, (0, y + 16), wrap(d, sub, font(SANS, 34), W - 144), font(SANS, 34), SILVER,
               anchor_center=True)
    return img


def range_grid(names, headline):
    canvas = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(canvas)
    wordmark(canvas, 40)
    d.text((W // 2, 130), headline.upper(), font=font(SANS_BOLD, 40), fill=BLACK, anchor="ma")
    cols, rows = 4, 2
    cw, ch = (W - 60) // cols, 520
    for i, n in enumerate(names):
        s = product(n)
        s = s.crop((int(s.width * 0.1), 0, int(s.width * 0.9), s.height))
        s.thumbnail((cw, ch), Image.LANCZOS)
        x = 30 + (i % cols) * cw + (cw - s.width) // 2
        y = 220 + (i // cols) * (ch + 20)
        canvas.paste(s, (x, y))
    d.rectangle((0, H - 90, W, H), fill=BLACK)
    d.text((W // 2, H - 45), "Disponibil la Cosmetic Shop  ·  cosmeticshop.md",
           font=font(SANS, 30), fill=WHITE, anchor="mm")
    return canvas


def save(img, post, n):
    folder = OUT / post
    folder.mkdir(parents=True, exist_ok=True)
    img.save(folder / f"{n}.jpg", "JPEG", quality=90, optimize=True, progressive=False)


def main():
    # 01 — brand intro carousel
    save(cover_photo("banner-lifestyle", "Formule care fac ceea ce trebuie să facă.",
                     "Glimmer — cosmetică profesională pentru păr."), "01-brand-intro", 1)
    save(text_slide("Creat pentru Moldova",
                    "Produs în Spania. Gândit pentru părul tău.",
                    ["climat umed", "păr neascultător și poros", "coafări termice zilnice"]),
         "01-brand-intro", 2)
    save(text_slide("Fiecare produs — o sarcină concretă", "Ce face Glimmer",
                    ["control frizz", "protecție la coafat", "volum și prospețime fără îngreuare",
                     "netezime care rezistă toată ziua"], dark=False),
         "01-brand-intro", 3)
    save(range_grid(["rebond-shampoo", "rebond-conditioner", "frizz-blocker", "heat-protection-220",
                     "repair-nourish-shampoo", "dry-shampoo", "sea-salt-booster",
                     "set-heat-protection-repair"], "Gama Glimmer"),
         "01-brand-intro", 4)

    # 02 — Re:Bond duo
    save(product_card(["rebond-shampoo", "rebond-conditioner"], "Re:Bond",
                      "Keratină + ceramide pentru păr uscat, poros și deteriorat. Șampon fără sulfați.",
                      tag="Duo regenerant · 750 ml"), "02-rebond", 1)
    # 03 — Frizz Blocker
    save(product_card(["frizz-blocker"], "Stop frizz",
                      "Protecție de încrețire și umiditate pentru până la 4 spălări.",
                      tag="Frizz Blocker · 150 ml"), "03-frizz-blocker", 1)
    # 04 — Heat protection
    save(product_card(["heat-protection-220"], "Protecție până la 220 °C",
                      "Foehn, placă, ondulator — fără păr lipicios sau îngreunat.",
                      tag="220 Heat Protection · 175 ml"), "04-heat-protection", 1)
    # 05 — Dry shampoo
    save(product_card(["dry-shampoo"], "Păr proaspăt fără apă",
                      "Amidon de orez absoarbe sebumul și dă volum la rădăcină. Nu lasă urme.",
                      tag="Dry Shampoo · 150 ml"), "05-dry-shampoo", 1)
    # 06 — Set
    save(product_card(["set-heat-protection-repair"], "Duo: curățare + protecție",
                      "Șampon Repair & Nourish 200 ml + spray termoprotector 220 °C 175 ml.",
                      tag="Set Heat Protection & Repair"), "06-set", 1)


if __name__ == "__main__":
    main()
