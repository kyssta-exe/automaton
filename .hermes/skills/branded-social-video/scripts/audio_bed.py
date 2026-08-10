"""Finish the audio, then mux it onto the composited video without re-encoding.

Two modes:

  ambience_loop  Replace the whole track with a clean donor stretch, looped.
                 Use when the location audio has people talking in it. Patching
                 individual speech windows turns into whack-a-mole — one missed
                 syllable and the client hears it. Rebuilding the bed removes
                 speech by construction. Cost: the bed no longer syncs to
                 on-screen events, so knocks and clunks disappear.

  keep           Keep location audio as cut, just filter and normalise.

Loudness: -14 LUFS is a speech/music target and is wrong for quiet ambience.
Nature beds often measure around -40 LUFS with a huge peak-to-loudness ratio
(wind transients sitting 30dB+ above the average), so hitting -14 needs ~+25dB,
which lifts the noise floor into a roar and crushes the dynamic range. -18 with
a high-pass for rumble is a far better landing spot. Check the reported LRA: if
it collapses below ~4 LU you are over-compressing.

Usage:
    python scripts/audio_bed.py <project.json>
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

from common import duration, edit_dir, load_project, resolve


def read_wav(p: Path):
    with wave.open(str(p)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return pcm.reshape(-1, ch).astype(np.float32) / 32768.0, sr


def write_wav(p: Path, data: np.ndarray, sr: int) -> None:
    with wave.open(str(p), "wb") as w:
        w.setnchannels(data.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(data, -1, 1) * 32767).astype(np.int16).tobytes())


def build_bed(donor: np.ndarray, sr: int, total_s: float,
              xfade: float, footage_end: float, tail: float) -> np.ndarray:
    """Loop the donor to length with equal-power crossfades at each seam.

    Equal-power (sin/cos) rather than linear: the two sides are uncorrelated
    noise, and a linear crossfade dips audibly in the middle.
    """
    n_total = int(total_s * sr)
    f = int(xfade * sr)
    t = np.linspace(0.0, 1.0, f, dtype=np.float32)[:, None]
    fade_in, fade_out = np.sin(t * np.pi / 2), np.cos(t * np.pi / 2)

    bed = donor.copy()
    while len(bed) < n_total:
        seam = bed[-f:] * fade_out + donor[:f] * fade_in
        bed = np.concatenate([bed[:-f], seam, donor[f:]])
    bed = bed[:n_total]

    s0 = int(footage_end * sr)
    s1 = min(n_total, int((footage_end + tail) * sr))
    if s1 > s0:
        ramp = np.cos(np.linspace(0, 1, s1 - s0, dtype=np.float32) * np.pi / 2)[:, None]
        bed[s0:s1] *= ramp
    bed[s1:] = 0.0

    lead = int(0.4 * sr)
    bed[:lead] *= np.linspace(0.0, 1.0, lead, dtype=np.float32)[:, None]
    return bed


def measure(src: Path, af: str) -> dict:
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
         "-af", af + ":print_format=json", "-vn", "-f", "null", "-"],
        capture_output=True, text=True)
    a, b = p.stderr.rfind("{"), p.stderr.rfind("}")
    return json.loads(p.stderr[a:b + 1])


def main() -> None:
    cfg = load_project(sys.argv[1])
    e = edit_dir(cfg)
    a = cfg["audio"]
    video = e / "composite.mp4"
    out = e / "final.mp4"

    total = duration(video)
    footage_end = round(sum(r["end"] - r["start"] for r in cfg["ranges"]), 3)

    hpf = f"highpass=f={a['highpass']}"
    ln = f"loudnorm=I={a['lufs']}:TP={a['true_peak']}:LRA=11"

    with tempfile.TemporaryDirectory() as tmp:
        track = Path(tmp) / "track.wav"

        if a["mode"] == "ambience_loop":
            d = a["donor"]
            raw = Path(tmp) / "donor.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(d["start"]), "-t", str(d["length"]),
                 "-i", str(resolve(cfg, d["file"])), "-vn", "-ac", "2",
                 "-ar", "48000", "-c:a", "pcm_s16le", str(raw)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            donor, sr = read_wav(raw)
            print(f"donor: {d['file']} {d['start']}s +{d['length']}s")
            write_wav(track, build_bed(donor, sr, total, a["loop_xfade"],
                                       footage_end, a["tail_fade"]), sr)
            print(f"bed: {total:.2f}s, {a['loop_xfade']}s seams, "
                  f"fade-out at {footage_end:.2f}s")
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(e / "base.mp4"), "-vn", "-ac", "2",
                 "-ar", "48000", "-c:a", "pcm_s16le", str(track)],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("keeping location audio")

        m = measure(track, f"{hpf},{ln}")
        print(f"measured: I={m['input_i']} LUFS  TP={m['input_tp']}  "
              f"LRA={m['input_lra']}")

        af = (f"{hpf},{ln}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}")

        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video), "-i", str(track),
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", af,
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-shortest", "-movflags", "+faststart", str(out)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    print(f"\nwrote {out}  {duration(out):.2f}s  {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
