"""Inventory every source clip, reporting TRUE display orientation.

Run this first, before deciding anything about aspect ratio or output size.
It exists because `ffprobe -show_entries stream=width,height` reports coded
dimensions, which silently lie about orientation on rotated footage.

Usage:
    python scripts/probe.py <videos_dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

from common import VIDEO_EXTS, display_size, duration, ffprobe_json


def main() -> None:
    d = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    vids = sorted(p for p in d.iterdir() if p.is_file() and p.suffix in VIDEO_EXTS)
    if not vids:
        sys.exit(f"no video files in {d}")

    print(f"{'file':<34}{'coded':>12}{'display':>12}{'rot':>6}"
          f"{'fps':>7}{'dur':>8}  audio")
    print("-" * 92)

    for v in vids:
        data = ffprobe_json(v)
        vs = next(s for s in data["streams"] if s["codec_type"] == "video")
        aud = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        dw, dh, rot = display_size(v)

        num, den = (vs.get("r_frame_rate") or "0/1").split("/")
        fps = float(num) / float(den) if float(den) else 0.0

        a = (f"{aud['codec_name']} {aud.get('channels', '?')}ch "
             f"{aud.get('sample_rate', '?')}Hz") if aud else "none"

        print(f"{v.name[:33]:<34}{vs['width']}x{vs['height']:>5}"
              f"{dw:>7}x{dh:<5}{rot:>6.0f}{fps:>7.2f}{duration(v):>8.2f}  {a}")

    print()
    orientations = {("portrait" if h > w else "landscape")
                    for w, h, _ in (display_size(v) for v in vids)}
    if len(orientations) > 1:
        print("MIXED ORIENTATIONS — decide one output frame and plan how the "
              "odd clips get cropped or pillarboxed before cutting.")
    else:
        o = orientations.pop()
        print(f"All sources display {o}. Target a {o} output frame "
              f"({'1080x1920' if o == 'portrait' else '1920x1080'} is the usual choice).")
    print("Any clip with rot != 0 will scale differently than its coded size "
          "suggests — scale by width and let height follow (-2).")


if __name__ == "__main__":
    main()
