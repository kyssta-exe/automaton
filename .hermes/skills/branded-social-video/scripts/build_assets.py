"""Build every still overlay the render needs, from project.json.

Produces in <videos_dir>/edit/:
  scrim.png          bottom gradient - carries text contrast
  cards/title.png    opening sheet
  cards/card_N.png   one per instruction
  watermark.png      brand lockup, top-right
  endcard.png        closing brand card

Design rationale lives in SKILL.md; the short version is that text sits
directly on the footage with no box, and legibility comes from two cheap
tricks stacked: a gradient scrim under the lower third, and a blurred dark
halo behind the glyphs. That combination survives both bright sky and dark
subjects without a panel covering the product.

Usage:
    python scripts/build_assets.py <project.json>
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import edit_dir, load_project, resolve

HALO_BLUR = 8
HALO_PASSES = 3
HEAD_LEAD = 14
SUP_LEAD = 10
CARD_GAP_RATIO = 0.028


def wrap(draw, text, font, max_w):
    raw_words = text.split()
    words, i = [], 0
    while i < len(raw_words):
        if raw_words[i] == "—" and i + 1 < len(raw_words):
            words.append(f"— {raw_words[i + 1]}")
            i += 2
        else:
            words.append(raw_words[i])
            i += 1
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_scrim(cfg, W, H, out: Path) -> None:
    s = cfg["scrim"]
    y = np.arange(H, dtype=np.float32)
    t = np.clip((y - s["start"]) / (H - s["start"]), 0.0, 1.0)
    alpha = (t ** s["curve"]) * s["max_alpha"]

    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[..., 3] = np.repeat(alpha[:, None], W, axis=1).astype(np.uint8)
    Image.fromarray(arr, "RGBA").save(out)
    print(f"  {out.name}  from y={s['start']} to alpha {s['max_alpha']}")


def build_card(cfg, W, H, headline, support, out: Path,
               head_size, sup_size) -> None:
    """Centred headline / support line, anchored from the bottom.

    Bottom-anchoring matters: it keeps the support line on the same baseline
    whether the headline wraps to one line or two, so nothing jitters between
    cards. The card has no divider; consistent type and spacing carry the
    hierarchy.
    """
    t = cfg["text"]
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    head_font_key = "semibold" if cfg.get("text", {}).get("single_style_cards") else "bold"
    f_head = ImageFont.truetype(str(resolve(cfg, cfg["fonts"][head_font_key])), head_size)
    f_sup = ImageFont.truetype(str(resolve(cfg, cfg["fonts"]["semibold"])), sup_size)
    max_w = W - t["side_margin"] * 2

    head_txt = headline.upper() if t.get("uppercase_headlines", True) else headline
    head_lines = wrap(probe, head_txt, f_head, max_w)
    sup_lines = wrap(probe, support, f_sup, max_w) if support else []

    head_lh, sup_lh = head_size + HEAD_LEAD, sup_size + SUP_LEAD
    head_h = len(head_lines) * head_lh - HEAD_LEAD
    sup_h = (len(sup_lines) * sup_lh - SUP_LEAD) if sup_lines else 0
    gap = round(W * CARD_GAP_RATIO)
    y0 = t["block_bottom"] - (head_h + (gap if sup_lines else 0) + sup_h)

    def centred(draw, text, font, y, fill):
        draw.text(((W - draw.textlength(text, font=font)) / 2, y), text,
                  fill=fill, font=font)

    def paint(draw, head_fill, sup_fill):
        y = y0
        for line in head_lines:
            centred(draw, line, f_head, y, head_fill)
            y += head_lh
        if sup_lines:
            y = y0 + head_h + gap
            for line in sup_lines:
                centred(draw, line, f_sup, y, sup_fill)
                y += sup_lh

    ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paint(ImageDraw.Draw(ink), (0, 0, 0, 255), (0, 0, 0, 255))
    halo = ink.filter(ImageFilter.GaussianBlur(HALO_BLUR))

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(HALO_PASSES):
        img.alpha_composite(halo)
    paint(ImageDraw.Draw(img), (255, 255, 255, 255), (255, 255, 255, 255))

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"  {out.name}  head {len(head_lines)}L + support {len(sup_lines)}L")


def _logo(cfg) -> Image.Image:
    return Image.open(resolve(cfg, cfg["brand"]["logo"])).convert("RGBA")


def recolour(img: Image.Image, to=(255, 255, 255)) -> Image.Image:
    """Repaint dark ink while leaving saturated accent shapes alone.

    Useful when a black-ink lockup has to sit on dark footage. Prefer a light
    plate instead where the client cares about exact brand colour.
    """
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and not (max(r, g, b) - min(r, g, b) > 60):
                px[x, y] = (*to, a)
    return img


def build_watermark(cfg, W, H, out: Path) -> None:
    wm = cfg["watermark"]
    surface = tuple(cfg["brand"]["surface"])
    lw = _logo(cfg)
    mw = wm["width"]
    lw = lw.resize((mw, max(1, round(mw * lw.height / lw.width))), Image.LANCZOS)

    pad_h, pad_v = 22, 18
    plate_w, plate_h = mw + pad_h * 2, lw.height + pad_v * 2
    px, py = W - plate_w - wm["right_margin"], wm["top"]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [px, py + 3, px + plate_w, py + plate_h + 3], radius=14, fill=(0, 0, 0, 130))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))

    if cfg["brand"].get("logo_is_dark_ink", True):
        plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(plate).rounded_rectangle(
            [px, py, px + plate_w, py + plate_h], radius=14, fill=(*surface, 242))
        img.alpha_composite(plate)
    else:
        lw = recolour(lw)
    img.alpha_composite(lw, (px + pad_h, py + pad_v))
    img.save(out)
    print(f"  {out.name}  plate {plate_w}x{plate_h} at ({px},{py})")


def build_endcard(cfg, W, H, out: Path) -> None:
    surface = tuple(cfg["brand"]["surface"])
    ink = tuple(cfg["brand"]["ink"])
    img = Image.new("RGBA", (W, H), (*surface, 255))
    d = ImageDraw.Draw(img)

    mw = int(W * 0.76)
    lw = _logo(cfg)
    if not cfg["brand"].get("logo_is_dark_ink", True):
        lw = recolour(lw, ink)
    lw = lw.resize((mw, max(1, round(mw * lw.height / lw.width))), Image.LANCZOS)
    lx, ly = (W - mw) // 2, (H - lw.height) // 2 - 80
    img.alpha_composite(lw, (lx, ly))

    tag = cfg["endcard"].get("tagline", "")
    if tag:
        f = ImageFont.truetype(str(resolve(cfg, cfg["fonts"]["regular"])), 36)
        d.text(((W - d.textlength(tag, font=f)) / 2, ly + lw.height + 70),
               tag, fill=(74, 66, 54, 255), font=f)

    img.convert("RGB").save(out)
    print(f"  {out.name}  {img.size}")


def build_title_screen(cfg, W, H, out: Path) -> None:
    """Build a clean opening screen using the same brand surface as the end card."""
    surface = tuple(cfg["brand"]["surface"])
    ink = tuple(cfg["brand"]["ink"])
    img = Image.new("RGBA", (W, H), (*surface, 255))

    mw = int(W * 0.64)
    lw = _logo(cfg)
    lw = lw.resize((mw, max(1, round(mw * lw.height / lw.width))), Image.LANCZOS)
    lx, ly = (W - mw) // 2, 620
    img.alpha_composite(lw, (lx, ly))

    f = ImageFont.truetype(str(resolve(cfg, cfg["fonts"]["semibold"])),
                           cfg["text"]["card_size"])
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap(probe, cfg["title"]["text"].upper(), f,
                 W - cfg["text"]["side_margin"] * 2)
    d = ImageDraw.Draw(img)
    y = 1160
    line_h = cfg["text"]["card_size"] + 14
    for line in lines:
        d.text(((W - d.textlength(line, font=f)) / 2, y), line,
               fill=(*ink, 255), font=f)
        y += line_h

    img.convert("RGB").save(out)
    print(f"  {out.name}  title screen {img.size}")


def main() -> None:
    cfg = load_project(sys.argv[1])
    W, H = cfg["output"]["width"], cfg["output"]["height"]
    e = edit_dir(cfg)
    (e / "cards").mkdir(parents=True, exist_ok=True)
    t = cfg["text"]

    print("scrim")
    build_scrim(cfg, W, H, e / "scrim.png")

    print("title + cards")
    if cfg.get("title"):
        if t.get("title_screen"):
            build_title_screen(cfg, W, H, e / "cards" / "title.png")
        elif t.get("single_style_cards") and cfg["title"].get("text"):
            build_card(cfg, W, H, cfg["title"]["text"], "",
                       e / "cards" / "title.png", t["card_size"], t["card_size"])
        else:
            build_card(cfg, W, H, cfg["title"]["headline"], cfg["title"].get("support", ""),
                       e / "cards" / "title.png",
                       t["title_head_size"], t["title_sup_size"])
    for i, c in enumerate(cfg["cards"], start=1):
        if t.get("single_style_cards"):
            build_card(cfg, W, H, c["text"], "",
                       e / "cards" / f"card_{i}.png", t["card_size"], t["card_size"])
        else:
            build_card(cfg, W, H, c["headline"], c.get("support", ""),
                       e / "cards" / f"card_{i}.png", t["head_size"], t["sup_size"])

    print("brand")
    build_watermark(cfg, W, H, e / "watermark.png")
    build_endcard(cfg, W, H, e / "endcard.png")


if __name__ == "__main__":
    main()
