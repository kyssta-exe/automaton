"""Labelled contact sheets for choosing cut points by eye.

Scrubbing a video one frame at a time burns turns. One sheet of evenly spaced,
timestamped frames lets you choose all your in/out points in a single look.

Usage:
    python scripts/contact_sheet.py <video> <start> <end> <step_s> <out.png>
    python scripts/contact_sheet.py <video> --bounds 18.0,24.5 12.1,18.3 <out.png>

The --bounds form renders the first and last frame of each proposed range side
by side, which is how you confirm a cut does not land mid-gesture before
committing to a render.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TILE_W = 384
COLS = 5


def _font(size: int):
    for p in (r"C:\Windows\Fonts\arialbd.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def grab(video: str, t: float, dest: Path, width: int = TILE_W) -> Image.Image:
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", video,
                    "-frames:v", "1", "-q:v", "3", "-vf", f"scale={width}:-2",
                    str(dest)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(dest).convert("RGB").copy()


def sheet_even(video: str, start: float, end: float, step: float, out: str) -> None:
    times, t = [], start
    while t <= end:
        times.append(t)
        t += step

    font = _font(22)
    with tempfile.TemporaryDirectory() as tmp:
        imgs = [(t, grab(video, t, Path(tmp) / f"{i:03d}.jpg"))
                for i, t in enumerate(times)]

    th = imgs[0][1].height
    rows = (len(imgs) + COLS - 1) // COLS
    pad, lab = 6, 30
    sheet = Image.new("RGB",
                      (COLS * (TILE_W + pad) + pad, rows * (th + lab + pad) + pad),
                      (12, 12, 14))
    d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(imgs):
        r, c = divmod(i, COLS)
        x, y = pad + c * (TILE_W + pad), pad + r * (th + lab + pad)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 4), f"{t:6.2f}s", fill=(255, 216, 24), font=font)
    sheet.save(out, "PNG", optimize=True)
    print(f"{out}  {sheet.size}  {len(imgs)} frames")


def sheet_bounds(video: str, pairs: list[tuple[float, float]], out: str) -> None:
    font = _font(24)
    w = 470
    with tempfile.TemporaryDirectory() as tmp:
        rows = []
        for i, (a, b) in enumerate(pairs):
            ims = [(tag, t, grab(video, t, Path(tmp) / f"{i}_{tag}.jpg", w))
                   for tag, t in (("IN", a), ("OUT", b))]
            rows.append((b - a, ims))

    th = rows[0][1][0][2].height
    pad, lab, hdr = 8, 30, 34
    sheet = Image.new("RGB", (2 * w + 3 * pad, len(rows) * (th + lab + hdr + pad) + pad),
                      (12, 12, 14))
    d = ImageDraw.Draw(sheet)
    for r, (dur, ims) in enumerate(rows):
        y = pad + r * (th + lab + hdr + pad)
        d.text((pad, y), f"range {r}  ({dur:.2f}s)", fill=(255, 216, 24), font=font)
        for c, (tag, t, im) in enumerate(ims):
            x = pad + c * (w + pad)
            sheet.paste(im, (x, y + hdr))
            d.text((x + 4, y + hdr + th + 3), f"{tag}  {t:.2f}s",
                   fill=(235, 235, 235), font=font)
    sheet.save(out, "PNG", optimize=True)
    print(f"{out}  {sheet.size}  {len(rows)} ranges")


def main() -> None:
    if "--bounds" in sys.argv:
        i = sys.argv.index("--bounds")
        video = sys.argv[1]
        pairs = [tuple(float(x) for x in a.split(",")) for a in sys.argv[i + 1:-1]]
        sheet_bounds(video, pairs, sys.argv[-1])
    else:
        video, start, end, step, out = sys.argv[1:6]
        sheet_even(video, float(start), float(end), float(step), out)


if __name__ == "__main__":
    main()
