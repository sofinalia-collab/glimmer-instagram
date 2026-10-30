"""Generate 9:16 Reels (1080x1920, 30 fps, H.264 + silent AAC) presenting the Glimmer range.

Run: python3 scripts/make_reel.py [reel-name ...]  ->  posts/<reel-name>/reel.mp4 (+ cover.jpg)
Requires ffmpeg.
"""
import subprocess

from PIL import Image, ImageDraw

from make_posts import (BLACK, GREY, OUT, SANS, SANS_BOLD, SILVER, WHITE, font, product,
                        wordmark, wrap)

W, H, FPS = 1080, 1920, 30
FADE = 0.35  # seconds of crossfade between scenes


def centered(d, y, text, fnt, fill, max_w=W - 160, spacing=1.12):
    for line in wrap(d, text, fnt, max_w):
        d.text((W // 2, y), line, font=fnt, fill=fill, anchor="ma")
        y += int(fnt.size * spacing)
    return y


def logo_scene(headline, sub):
    def frame(p):
        img = Image.new("RGB", (W, H), BLACK)
        size = int(110 + 10 * p)
        wordmark(img, 640 - size // 2, fill=WHITE, size=size)
        d = ImageDraw.Draw(img)
        y = centered(d, 980, headline, font(SANS_BOLD, 66), WHITE)
        centered(d, y + 20, sub, font(SANS, 40), SILVER)
        return img
    return frame


def product_scene(names, tag, headline):
    shots = [product(n) for n in names]
    shots = [s.crop((int(s.width * 0.1), 0, int(s.width * 0.9), s.height)) for s in shots]

    def frame(p):
        img = Image.new("RGB", (W, H), WHITE)
        wordmark(img, 110, fill=BLACK, size=70)
        zoom = 1.0 + 0.07 * p
        area_h, area_w = 900, W - 120
        scale = min(area_h / shots[0].height, area_w / sum(s.width for s in shots)) * zoom
        total = sum(int(s.width * scale) for s in shots)
        x = (W - total) // 2
        top = 300 + (area_h - int(shots[0].height * scale)) // 2
        for s in shots:
            r = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
            img.paste(r, (x, top))
            x += r.width
        d = ImageDraw.Draw(img)
        d.text((W // 2, 1260), tag.upper(), font=font(SANS_BOLD, 34), fill=GREY, anchor="ma")
        centered(d, 1320, headline, font(SANS_BOLD, 70), BLACK)
        return img
    return frame


def photo_scene(name, headline):
    src = product(name)

    def frame(p):
        zoom = 1.0 + 0.06 * p
        ch = int(src.height / zoom)
        cw = int(ch * W / 1150)
        left = (src.width - cw) // 2 + 40
        top = (src.height - ch) // 2
        photo = src.crop((left, top, left + cw, top + ch)).resize((W, 1150), Image.LANCZOS)
        img = Image.new("RGB", (W, H), BLACK)
        img.paste(photo, (0, 0))
        d = ImageDraw.Draw(img)
        centered(d, 1280, headline, font(SANS_BOLD, 70), WHITE)
        return img
    return frame


REELS = {
    "reel-01-range": [
        (2.6, logo_scene("Faceți cunoștință cu Glimmer", "Cosmetică profesională pentru păr")),
        (2.2, product_scene(["rebond-shampoo", "rebond-conditioner"], "Re:Bond · șampon + balsam",
                            "Keratină + ceramide")),
        (2.2, product_scene(["frizz-blocker"], "Frizz Blocker", "Stop frizz — până la 4 spălări")),
        (2.2, product_scene(["heat-protection-220"], "220 Heat Protection", "Protecție până la 220 °C")),
        (2.2, product_scene(["dry-shampoo"], "Dry Shampoo", "Păr proaspăt fără apă")),
        (2.2, product_scene(["repair-nourish-shampoo"], "Repair & Nourish Shampoo",
                            "Strălucire și catifelare")),
        (2.2, product_scene(["set-heat-protection-repair"], "Set Heat Protection & Repair",
                            "Curățare + protecție")),
        (2.6, photo_scene("banner-lifestyle", "Produs în Spania. Gândit pentru Moldova.")),
        (3.2, logo_scene("Disponibil la Cosmetic Shop", "cosmeticshop.md  ·  079 811 081")),
    ],
    "reel-02-rebond-routine": [
        (2.6, logo_scene("Rutina Re:Bond", "2 pași pentru păr uscat, poros și deteriorat")),
        (2.8, product_scene(["rebond-shampoo"], "Pasul 1 · Re:Bond Shampoo",
                            "Masează pe părul umed, apoi clătește")),
        (2.8, product_scene(["rebond-conditioner"], "Pasul 2 · Re:Bond Conditioner",
                            "Lasă 2–3 minute pe lungimi și vârfuri")),
        (2.8, product_scene(["rebond-shampoo", "rebond-conditioner"], "Rezultatul",
                            "Păr mai dens, mai elastic și mai strălucitor")),
    (3.0, logo_scene("Disponibil la Cosmetic Shop", "cosmeticshop.md  ·  079 811 081")),
    ],
    "reel-03-frizz": [
        (2.6, logo_scene("Vreme umedă = păr pufos?", "Glimmer Frizz Blocker")),
        (2.6, product_scene(["frizz-blocker"], "Pasul 1", "Aplică pe părul spălat și umed")),
        (2.6, product_scene(["frizz-blocker"], "Pasul 2", "Distribuie uniform și continuă coafarea")),
        (2.8, product_scene(["frizz-blocker"], "Efectul", "Fără frizz până la 4 spălări")),
    (3.0, logo_scene("Disponibil la Cosmetic Shop", "cosmeticshop.md  ·  079 811 081")),
    ],
    "reel-04-dry-shampoo": [
        (2.6, logo_scene("Nu ai timp să speli părul?", "Păr proaspăt în 2 minute")),
        (2.4, product_scene(["dry-shampoo"], "Pasul 1", "Agită și pulverizează la rădăcini, de la 20 cm")),
        (2.4, product_scene(["dry-shampoo"], "Pasul 2", "Masează ușor cu vârfurile degetelor")),
        (2.4, product_scene(["dry-shampoo"], "Pasul 3", "Lasă 2 minute, apoi pieptănă")),
        (2.6, product_scene(["dry-shampoo"], "Rezultatul", "Volum la rădăcină, fără urme")),
    (3.0, logo_scene("Disponibil la Cosmetic Shop", "cosmeticshop.md  ·  079 811 081")),
    ],
}


def frames(scenes):
    prev_tail = None
    for duration, scene in scenes:
        n = int(duration * FPS)
        fade_n = int(FADE * FPS)
        for i in range(n):
            img = scene(i / (n - 1))
            if prev_tail is not None and i < fade_n:
                img = Image.blend(prev_tail, img, (i + 1) / (fade_n + 1))
            yield img
        prev_tail = scene(1.0)


def render(name, scenes):
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "reel.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-crf", "20", "-preset", "medium", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "128k", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for img in frames(scenes):
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    scenes[0][1](1.0).save(folder / "cover.jpg", "JPEG", quality=90)


def main(names=None):
    for name in names or REELS:
        render(name, REELS[name])


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
