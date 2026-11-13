"""Generate Mastermind brand PNGs (replacing DeepTutor brand assets).

Usage: uv run --with pillow python make_brand.py <web/public dir>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BLUE = (74, 163, 224)
ORANGE = (249, 166, 94)
BLACK = (24, 24, 27)
FONT_PATH = "/System/Library/Fonts/Avenir Next.ttc"
FONT_INDEX_DEMIBOLD = 2  # Avenir Next Demi Bold
SUPERSAMPLE = 4


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX_DEMIBOLD)


def gradient(w: int, h: int, a=BLUE, b=ORANGE) -> Image.Image:
    """Diagonal blue→orange gradient."""
    g = Image.new("RGB", (w, h))
    px = g.load()
    span = w + h
    for y in range(h):
        for x in range(w):
            t = (x + y) / span
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return g


def mark(size: int, mono: bool = False) -> Image.Image:
    """Rounded-square tile with a white 'M'."""
    s = size * SUPERSAMPLE
    tile = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * 0.24), fill=255)
    fill = Image.new("RGB", (s, s), BLACK) if mono else gradient(s, s)
    tile.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(tile)
    f = font(int(s * 0.62))
    box = d.textbbox((0, 0), "M", font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text(((s - tw) / 2 - box[0], (s - th) / 2 - box[1]), "M", font=f, fill=(255, 255, 255, 255))
    return tile.resize((size, size), Image.LANCZOS)


def wordmark(w: int, h: int, mono: bool = False) -> Image.Image:
    """'Mastermind' text, gradient-filled (or black), centred on transparent canvas."""
    s_w, s_h = w * SUPERSAMPLE, h * SUPERSAMPLE
    f = font(int(s_h * 0.62))
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    box = probe.textbbox((0, 0), "Mastermind", font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    scale = min(1.0, (s_w * 0.96) / tw)
    if scale < 1.0:
        f = font(int(s_h * 0.62 * scale))
        box = probe.textbbox((0, 0), "Mastermind", font=f)
        tw, th = box[2] - box[0], box[3] - box[1]
    mask = Image.new("L", (s_w, s_h), 0)
    ImageDraw.Draw(mask).text(((s_w - tw) / 2 - box[0], (s_h - th) / 2 - box[1]), "Mastermind", font=f, fill=255)
    fill = Image.new("RGB", (s_w, s_h), BLACK) if mono else gradient(s_w, s_h)
    out = Image.new("RGBA", (s_w, s_h), (0, 0, 0, 0))
    out.paste(fill, (0, 0), mask)
    return out.resize((w, h), Image.LANCZOS)


def full(w: int, h: int, mono: bool = False) -> Image.Image:
    """Mark + wordmark side by side."""
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m = mark(int(h * 0.86), mono)
    pad = int(h * 0.07)
    out.alpha_composite(m, (pad, (h - m.height) // 2))
    word_x = pad + m.width + int(h * 0.12)
    word = wordmark(w - word_x - pad, h, mono)
    out.alpha_composite(word, (word_x, 0))
    return out


def main(public: Path) -> None:
    brand = public / "brand"
    outputs = {
        brand / "color-logo.png": mark(512),
        brand / "black-logo.png": mark(512, mono=True),
        brand / "color-word.png": wordmark(1200, 310),
        brand / "black-word.png": wordmark(1200, 303, mono=True),
        brand / "color-full.png": full(1600, 313),
        brand / "black-full.png": full(1600, 313, mono=True),
        brand / "favicon-16x16.png": mark(16),
        brand / "favicon-32x32.png": mark(32),
        brand / "apple-touch-icon.png": mark(180),
        public / "logo.png": mark(512),
        public / "logo-ver2.png": mark(512),
        public / "logo_black.png": mark(512, mono=True),
        public / "apple-touch-icon.png": mark(180),
        public / "favicon-16x16.png": mark(16),
        public / "favicon-32x32.png": mark(32),
    }
    for path, img in outputs.items():
        if not path.exists():
            raise SystemExit(f"refusing to create new file (expected existing asset): {path}")
        img.save(path, optimize=True)
        print(f"wrote {path.relative_to(public)} {img.size}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]).resolve())
