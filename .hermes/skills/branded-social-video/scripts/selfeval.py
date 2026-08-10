"""Check the rendered file before showing it to anyone.

Two failure modes are worth catching automatically because they are invisible
until someone watches on good speakers or a big screen:

  audio pops at cuts   a transient spiking far above local RMS means an edge
                       fade did not take
  visual jumps         frames straddling each cut, so you can see flashes,
                       mismatched exposure, or a caption clipped by the cut

It also samples mid-card frames so you can confirm every caption actually
rendered, at full opacity, paired with the right shot. Duration is checked
against the project — a mismatch usually means a stale segment cache.

Usage:
    python scripts/selfeval.py <project.json> [out_dir]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import duration, edit_dir, load_project

TILE = 210


def _font(size):
    for p in (r"C:\Windows\Fonts\arialbd.ttf",
              "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def grab(v, t, dest, w=TILE):
    subprocess.run(["ffmpeg", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(v),
                    "-frames:v", "1", "-q:v", "4", "-vf", f"scale={w}:-2", str(dest)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(dest).convert("RGB").copy()


def main() -> None:
    cfg = load_project(sys.argv[1])
    e = edit_dir(cfg)
    v = e / "final.mp4"
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else e / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)

    cuts, mids, off = [], [], 0.0
    for r in cfg["ranges"]:
        d = r["end"] - r["start"]
        mids.append(off + d / 2)
        off += d
        cuts.append(off)
    expected = off + cfg["endcard"]["seconds"]

    actual = duration(v)
    flag = "OK" if abs(actual - expected) < 0.25 else "MISMATCH — stale segment cache?"
    print(f"duration: {actual:.2f}s vs expected {expected:.2f}s  [{flag}]\n")

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "a.wav"
        subprocess.run(["ffmpeg", "-y", "-i", str(v), "-vn", "-ac", "1",
                        "-ar", "48000", "-c:a", "pcm_s16le", str(wav)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with wave.open(str(wav)) as w:
            sr = w.getframerate()
            pcm = (np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                   .astype(np.float32) / 32768.0)

        print("cut      rms_before  rms_after   peak    verdict")
        win = int(0.020 * sr)
        for c in cuts[:-1]:
            i = int(c * sr)
            before, after = pcm[max(0, i - 10 * win):i], pcm[i:i + 10 * win]
            local = pcm[max(0, i - win):i + win]
            rb = float(np.sqrt(np.mean(before ** 2))) if before.size else 0.0
            ra = float(np.sqrt(np.mean(after ** 2))) if after.size else 0.0
            pk = float(np.max(np.abs(local))) if local.size else 0.0
            verdict = "POP?" if pk > max(rb, ra, 1e-9) * 8 else "ok"
            print(f"{c:6.2f}  {rb:10.5f}  {ra:9.5f}  {pk:7.4f}   {verdict}")

        rows = [(c, [grab(v, c + o, Path(tmp) / f"c{c}{o}.jpg")
                     for o in (-0.40, -0.12, 0.12, 0.40)]) for c in cuts[:-1]]
        th = rows[0][1][0].height
        sheet = Image.new("RGB", (4 * (TILE + 6) + 120, len(rows) * (th + 32) + 6),
                          (12, 12, 14))
        d = ImageDraw.Draw(sheet)
        f = _font(20)
        for r, (c, ims) in enumerate(rows):
            y = 6 + r * (th + 32)
            d.text((6, y + th // 2), f"cut\n{c:.1f}s", fill=(255, 216, 24), font=f)
            for i, im in enumerate(ims):
                sheet.paste(im, (126 + i * (TILE + 6), y))
        sheet.save(out_dir / "cuts.png")

        cards = [grab(v, t, Path(tmp) / f"m{i}.jpg", 300) for i, t in enumerate(mids)]
        cw, chh = cards[0].size
        cs = Image.new("RGB", (cw * len(cards), chh))
        for i, im in enumerate(cards):
            cs.paste(im, (i * cw, 0))
        cs.save(out_dir / "cards.png")

    print(f"\nwrote {out_dir / 'cuts.png'} and {out_dir / 'cards.png'} — "
          f"look at both before delivering.")


if __name__ == "__main__":
    main()
