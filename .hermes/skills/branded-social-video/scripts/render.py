"""Cut, grade, concat and composite — everything except the final audio.

Pipeline, in this order for reasons that matter:

1. Per-segment extract, with the grade and 30ms edge audio fades baked in.
   Extracting per segment (rather than one big filtergraph) means overlays can
   be added later without re-encoding the picture twice.
2. Lossless `-c copy` concat. No generation loss.
3. One composite pass: scrim, watermark, then text. Text goes LAST so nothing
   can ever be drawn over it.
4. Audio is finished separately by audio_bed.py.

Segment cache keys encode source and in/out times. Do not key them by index —
inserting a segment shifts every index and the cache will silently serve the
previous occupant of each slot, pairing every caption with the wrong shot.

Usage:
    python scripts/render.py <project.json>
"""
from __future__ import annotations

import sys
from pathlib import Path

from common import card_name, duration, edit_dir, load_project, resolve, run

PANEL_IN = 0.30      # scrim/watermark fade up once, then hold
CARD_FADE = 0.28     # short, so the frame is never bare for long at swaps


def extract(cfg, src: Path, start: float, dur: float, out: Path, reverse: bool = False) -> None:
    """One range -> its own file, grade and edge fades baked in.

    scale=<W>:-2 is applied AFTER ffmpeg auto-rotates, so rotated sources land
    at the right frame size instead of something enormous and sideways.
    The 30ms afades exist because hard audio cuts at segment joins pop.
    """
    o = cfg["output"]
    if o["height"] > o["width"]:
        # Landscape source -> vertical social crop. Scale by height first so
        # the requested portrait frame is filled, then take the centered crop.
        vf = (f"scale=-2:{o['height']},"
              f"crop={o['width']}:{o['height']}:(in_w-{o['width']})/2:0")
    else:
        vf = f"scale={o['width']}:-2"
    if cfg.get("grade"):
        vf += "," + cfg["grade"]
    if reverse:
        vf = "reverse," + vf
    af = (f"afade=t=in:st=0:d=0.03,"
          f"afade=t=out:st={max(0.0, dur - 0.03):.3f}:d=0.03")
    if reverse:
        af = "areverse," + af
    seek = ["-ss", f"{start:.3f}"]
    if reverse:
        # Limit the input before reverse; otherwise reverse() buffers the
        # remainder of the source and returns unrelated later footage first.
        seek += ["-t", f"{dur:.3f}"]
    run(["ffmpeg", "-y", *seek, "-i", str(src),
         *([] if reverse else ["-t", f"{dur:.3f}"]),
         "-vf", vf, "-af", af,
         "-c:v", "libx264", "-preset", o["preset"], "-crf", str(o["crf"]),
         "-pix_fmt", "yuv420p", "-r", str(o["fps"]),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", str(out)])


def make_still(cfg, png: Path, out: Path, secs: float) -> None:
    """Still -> video with identical codec params, so concat stays lossless."""
    o = cfg["output"]
    run(["ffmpeg", "-y",
         "-loop", "1", "-t", str(secs), "-i", str(png),
         "-f", "lavfi", "-t", str(secs), "-i",
         "anullsrc=channel_layout=stereo:sample_rate=48000",
         "-vf", f"scale={o['width']}:{o['height']},format=yuv420p",
         "-c:v", "libx264", "-preset", o["preset"], "-crf", str(o["crf"]),
         "-r", str(o["fps"]),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-shortest", "-movflags", "+faststart", str(out)])


def make_endcard(cfg, png: Path, out: Path) -> None:
    make_still(cfg, png, out, cfg["endcard"]["seconds"])


def concat(parts: list[Path], out: Path, work: Path) -> None:
    lst = work / "_concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", "-movflags", "+faststart", str(out)])
    lst.unlink(missing_ok=True)


def composite(cfg, base: Path, windows, e: Path, out: Path, hold_end: float) -> None:
    """Overlay scrim, watermark and text.

    Every still is looped for the whole timeline, so each filter's local time
    equals output time — the fade values below are absolute output seconds,
    which keeps the arithmetic readable.
    """
    o = cfg["output"]
    total = duration(base)

    inputs = ["-i", str(base)]
    for png in (e / "scrim.png", e / "watermark.png"):
        inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(png)]
    for png, _, _ in windows:
        inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(png)]

    def env(tag, a, b, d):
        return (f"fade=t=in:st={a:.3f}:d={d}:alpha=1,"
                f"fade=t=out:st={b - d:.3f}:d={d}:alpha=1[{tag}]")

    p = [f"[1:v]format=rgba,{env('scrim', PANEL_IN, hold_end, 0.50)}",
         f"[0:v][scrim]overlay=0:0:enable='between(t,{PANEL_IN},{hold_end:.3f})'[v_s]",
         f"[2:v]format=rgba,{env('wm', PANEL_IN, hold_end, 0.50)}",
         f"[v_s][wm]overlay=0:0:enable='between(t,0,{hold_end:.3f})'[v_w]"]

    cur = "[v_w]"
    for i, (_, a, b) in enumerate(windows):
        p.append(f"[{i + 3}:v]format=rgba,{env(f'c{i}', a, b, CARD_FADE)}")
        nxt = f"[v{i}]"
        p.append(f"{cur}[c{i}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'{nxt}")
        cur = nxt

    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(p),
         "-map", cur, "-map", "0:a",
         "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", o["preset"], "-crf", str(o["crf"]),
         "-pix_fmt", "yuv420p", "-r", str(o["fps"]),
         "-c:a", "copy", "-movflags", "+faststart", str(out)])


def main() -> None:
    cfg = load_project(sys.argv[1])
    e = edit_dir(cfg)
    clips = e / "clips"
    clips.mkdir(exist_ok=True)

    parts, windows, offset = [], [], 0.0
    print(f"extracting {len(cfg['ranges'])} segments at "
          f"{cfg['output']['width']}x{cfg['output']['height']}@{cfg['output']['fps']}")

    for r in cfg["ranges"]:
        src = resolve(cfg, cfg["sources"][r["source"]])
        start, end = float(r["start"]), float(r["end"])
        dur = end - start
        card = r.get("card")
        if card == "title":
            version = cfg.get("title", {}).get("asset_version", "v1")
            seg = clips / f"seg_title_{start:07.2f}-{end:07.2f}_{version}.mp4"
        else:
            seg = clips / f"seg_{r['source']}_{start:07.2f}-{end:07.2f}.mp4"

        # Reverse ranges are always regenerated because their filter-input
        # semantics can change independently of the filename cache key.
        cached = seg.exists() and not bool(r.get("reverse", False))
        label = "OUTRO" if card in (None, "none") else card_name(card)
        print(f"  {r['source']} {start:6.2f}-{end:6.2f} ({dur:4.2f}s) "
              f"-> {label}{'  (cached)' if cached else ''}")
        if not cached:
            if card == "title":
                make_still(cfg, e / "cards" / "title.png", seg, dur)
            else:
                extract(cfg, src, start, dur, seg, reverse=bool(r.get("reverse", False)))
        parts.append(seg)
        if card not in (None, "none"):
            windows.append((e / "cards" / card_name(card), offset, offset + dur))
        offset += dur

    hold_end = offset

    print("endcard")
    endcard = clips / (f"seg_endcard_{cfg['endcard']['seconds']:.2f}_"
                       f"{cfg['endcard'].get('asset_version', 'v1')}.mp4")
    if not endcard.exists():
        make_endcard(cfg, e / "endcard.png", endcard)
    parts.append(endcard)

    print("concat (lossless)")
    base = e / "base.mp4"
    concat(parts, base, e)

    print("composite: scrim + watermark + text")
    out = e / "composite.mp4"
    composite(cfg, base, windows, e, out, hold_end)

    print(f"\ndone: {out}  {duration(out):.2f}s  {out.stat().st_size / 1e6:.1f} MB")
    print(f"footage ends {hold_end:.2f}s; next: python scripts/audio_bed.py <project.json>")


if __name__ == "__main__":
    main()
