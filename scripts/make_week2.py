"""Week 2 (07.11–13.11.2026): stock atmosphere photos (assets/stock, Pexels) + product shots
(assets/products, only from cosmeticshop.md/glimmer). Stock people are never presented as product results.

Run: cd scripts && python3 make_week2.py
"""
from PIL import Image, ImageDraw

from make_posts import (BLACK, GREY, OUT, ROOT, SANS, SANS_BOLD, SILVER, WHITE, draw_lines, font,
                        product, save, text_slide, wordmark, wrap)
import make_reel
from make_reel import logo_scene, product_scene, render

STOCK = ROOT / "assets" / "stock"


def stock(pid):
    return Image.open(next(STOCK.glob(f"pexels-{pid}-*.jpg"))).convert("RGB")


def cover(img, w, h, focus_y=0.35, zoom=1.0):
    """Crop img to w:h around a vertical focus point, optionally zoomed in."""
    r = w / h
    cw, ch = img.width, int(img.width / r)
    if ch > img.height:
        ch, cw = img.height, int(img.height * r)
    cw, ch = int(cw / zoom), int(ch / zoom)
    left = (img.width - cw) // 2
    top = min(max(0, int(img.height * focus_y - ch / 2)), img.height - ch)
    return img.crop((left, top, left + cw, top + ch)).resize((w, h), Image.LANCZOS)


def top_shade(img, height=260, strength=150):
    """Darken the top of a photo so the white logo stays readable on light backgrounds."""
    mask = Image.linear_gradient("L").rotate(180).resize((img.width, height)).point(lambda v: v * strength // 255)
    img.paste(Image.new("RGB", (img.width, height), BLACK), (0, 0), mask)
    return img


def product_inset(names, box_w, box_h):
    card = Image.new("RGB", (box_w, box_h), WHITE)
    shots = [product(n) for n in names]
    shots = [s.crop((int(s.width * 0.12), int(s.height * 0.04), int(s.width * 0.88), int(s.height * 0.96)))
             for s in shots]
    scale = min((box_h - 30) / shots[0].height, (box_w - 30) / sum(s.width for s in shots))
    x = (box_w - sum(int(s.width * scale) for s in shots)) // 2
    for s in shots:
        s = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
        card.paste(s, (x, (box_h - s.height) // 2))
        x += s.width
    return card


def lifestyle(pid, names, tag, headline, sub, w=1080, h=1350, photo_h=900, focus_y=0.35):
    """Stock photo on top, white product card overlapping, black text panel below."""
    img = Image.new("RGB", (w, h), BLACK)
    img.paste(top_shade(cover(stock(pid), w, photo_h, focus_y)), (0, 0))
    card_w, card_h = (300, 380) if len(names) == 1 else (440, 380)
    img.paste(product_inset(names, card_w, card_h), (w - card_w - 50, photo_h - card_h + 120))
    wordmark(img, 40, fill=WHITE, size=56)
    d = ImageDraw.Draw(img)
    text_w = w - card_w - 150
    d.text((60, photo_h + 50), tag.upper(), font=font(SANS_BOLD, 26), fill=SILVER)
    y = draw_lines(d, (60, photo_h + 95), wrap(d, headline, font(SANS_BOLD, 54), text_w),
                   font(SANS_BOLD, 54), WHITE, spacing=1.08)
    sub_w = w - 120 if y > photo_h + 170 + 120 else text_w
    draw_lines(d, (60, max(y + 14, photo_h + 270) if sub_w == w - 120 else y + 14),
               wrap(d, sub, font(SANS, 30), sub_w), font(SANS, 30), SILVER)
    d.text((w - 60, h - 40), "cosmeticshop.md", font=font(SANS, 24), fill=GREY, anchor="rs")
    return img


def lifestyle_story(pid, names, tag, headline, sub, focus_y=0.35):
    w, h, photo_h = 1080, 1920, 1150
    img = Image.new("RGB", (w, h), BLACK)
    img.paste(top_shade(cover(stock(pid), w, photo_h, focus_y)), (0, 0))
    card_w, card_h = (320, 400) if len(names) == 1 else (460, 400)
    img.paste(product_inset(names, card_w, card_h), ((w - card_w) // 2, photo_h - card_h // 2))
    wordmark(img, 110, fill=WHITE, size=70)
    d = ImageDraw.Draw(img)
    y0 = photo_h + card_h // 2 + 50
    d.text((w // 2, y0), tag.upper(), font=font(SANS_BOLD, 30), fill=SILVER, anchor="ma")
    y = draw_lines(d, (0, y0 + 60), wrap(d, headline, font(SANS_BOLD, 70), w - 160),
                   font(SANS_BOLD, 70), WHITE, spacing=1.1, anchor_center=True)
    draw_lines(d, (0, y + 16), wrap(d, sub, font(SANS, 42), w - 160), font(SANS, 42), SILVER,
               anchor_center=True)
    return img


def photo_text_scene(pid, headline, focus_y=0.35):
    """Reel scene: full-bleed stock photo with slow zoom and a headline on a dark band."""
    src = stock(pid)
    W, H = make_reel.W, make_reel.H

    def frame(p):
        img = cover(src, W, H, focus_y, zoom=1.0 + 0.08 * p)
        band = Image.new("RGB", (W, 330), BLACK)
        img.paste(Image.blend(img.crop((0, 1150, W, 1480)), band, 0.72), (0, 1150))
        d = ImageDraw.Draw(img)
        make_reel.centered(d, 1200, headline, font(SANS_BOLD, 68), WHITE)
        return img
    return frame


END = (3.0, logo_scene("Disponibil la Cosmetic Shop", "cosmeticshop.md  ·  079 811 081"))

REELS = {
    "reel-05-shine": [
        (2.6, photo_text_scene("11431138", "Vrei păr lucios?", 0.4)),
        (2.4, product_scene(["rebond-shampoo"], "Re:Bond Shampoo", "Curățare fără sulfați")),
        (2.4, product_scene(["rebond-conditioner"], "Re:Bond Conditioner", "Luciu oglindă, fără puf")),
        (2.6, photo_text_scene("7142796", "Și se pieptănă ușor", 0.45)),
        END,
    ],
    "reel-06-heat": [
        (2.4, photo_text_scene("973406", "Foehn în fiecare zi?", 0.5)),
        (2.4, photo_text_scene("8467969", "Placă sau ondulator?", 0.4)),
        (2.6, product_scene(["heat-protection-220"], "220 Heat Protection", "Protecție până la 220 °C")),
        (2.6, product_scene(["heat-protection-220"], "Cum se folosește",
                            "Pe părul umed, de la rădăcini la vârfuri. Nu se clătește.")),
        END,
    ],
    "reel-07-humidity": [
        (2.4, photo_text_scene("28751262", "Noiembrie. Ploaie. Umezeală.", 0.45)),
        (2.4, photo_text_scene("19265331", "Și părul se încrețește", 0.5)),
        (2.6, product_scene(["frizz-blocker"], "Frizz Blocker", "Protecție de frizz și umiditate")),
        (2.6, product_scene(["frizz-blocker"], "Un singur gest", "Rezistă până la 4 spălări")),
        END,
    ],
}


def main():
    posts = [
        ("07-frizz-rain", "19265331", ["frizz-blocker"], "Frizz Blocker · 150 ml",
         "Ploaie afară, păr neted", "Protecție de frizz și umiditate până la 4 spălări.", 0.45),
        ("08-heat-iron", "3738359", ["heat-protection-220"], "220 Heat Protection · 175 ml",
         "Mai întâi protecția, apoi placa", "Peliculă invizibilă care protejează până la 220 °C.", 0.4),
        ("09-rebond-color", "10483564", ["rebond-shampoo", "rebond-conditioner"], "Re:Bond · 750 ml",
         "Pentru păr vopsit și poros", "Keratină, ceramide și acid hialuronic. Fără sulfați în șampon.", 0.4),
        ("10-dry-morning", "7320796", ["dry-shampoo"], "Dry Shampoo · 150 ml",
         "Dimineață grăbită?", "Volum la rădăcină în 2 minute, fără apă și fără urme.", 0.45),
    ]
    for folder, pid, names, tag, head, sub, fy in posts:
        save(lifestyle(pid, names, tag, head, sub, focus_y=fy), folder, 1)

    # 11 — educational carousel on heat protection
    save(lifestyle("973406", ["heat-protection-220"], "Ghid rapid",
                   "3 lucruri despre protecția termică", "Glisează →", focus_y=0.5), "11-heat-guide", 1)
    save(text_slide("1 / 3", "Pe părul umed, nu pe cel uscat",
                    ["după spălare, uscat cu prosopul", "de la rădăcini până la vârfuri, cu pieptenele"]),
         "11-heat-guide", 2)
    save(text_slide("2 / 3", "Foehn, placă și ondulator",
                    ["protecție la temperaturi de până la 220 °C", "reduce electrizarea părului"], dark=False),
         "11-heat-guide", 3)
    save(text_slide("3 / 3", "Nu se clătește",
                    ["nu lipește și nu îngreunează părul", "nu lasă urme", "previne buclele nedorite"]),
         "11-heat-guide", 4)

    stories = [
        ("story-09-shine", "2320890", ["rebond-conditioner"], "Re:Bond Conditioner",
         "Luciu oglindă", "Efect de „mătase lichidă”: fără puf, fără electrizare.", 0.3),
        ("story-10-frizz", "15167450", ["frizz-blocker"], "Frizz Blocker",
         "Păr care nu ascultă?", "Netezire și strălucire, protecție până la 4 spălări.", 0.35),
        ("story-11-sulfate-free", "7142796", ["rebond-shampoo"], "Re:Bond Shampoo",
         "Fără sulfați", "Curăță delicat, fără să usuce firul de păr.", 0.45),
        ("story-12-heat", "8467969", ["heat-protection-220"], "220 Heat Protection",
         "Protecție înainte de placă", "Până la 220 °C. Nu se clătește.", 0.4),
        ("story-13-nourish", "10483564", ["repair-nourish-shampoo"], "Repair & Nourish Shampoo",
         "Strălucire și catifelare", "Cu extracte de zmeură, căpșuni, kiwi și piersică.", 0.35),
        ("story-14-dry", "7320796", ["dry-shampoo"], "Dry Shampoo",
         "Fără apă, fără urme", "Amidon de orez care absoarbe excesul de sebum.", 0.45),
        ("story-15-gift", "11431138", ["set-heat-protection-repair"], "Set Heat Protection & Repair",
         "Idee de cadou", "Șampon + spray termoprotector, într-un singur set.", 0.4),
    ]
    for folder, pid, names, tag, head, sub, fy in stories:
        save(lifestyle_story(pid, names, tag, head, sub, fy), folder, 1)

    for name, scenes in REELS.items():
        render(name, scenes)


if __name__ == "__main__":
    main()
