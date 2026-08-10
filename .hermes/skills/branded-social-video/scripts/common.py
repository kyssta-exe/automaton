"""Shared helpers: config loading, ffprobe wrappers, rotation-aware sizing."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".MP4", ".MOV", ".MKV"}


def load_project(path: str | Path) -> dict:
    p = Path(path).resolve()
    cfg = json.loads(p.read_text(encoding="utf-8"))
    cfg["_dir"] = p.parent
    return cfg


def resolve(cfg: dict, rel: str) -> Path:
    """Resolve a config-relative path."""
    q = Path(rel)
    return q if q.is_absolute() else (cfg["_dir"] / q)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE, **kw)


def ffprobe_json(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def display_size(path: Path) -> tuple[int, int, float]:
    """Return (display_w, display_h, rotation).

    ffprobe reports CODED dimensions. Phone and action-cam footage very often
    carries a +/-90 display matrix, so a clip that reports 3840x2160 actually
    plays as 2160x3840 vertical. ffmpeg auto-rotates on decode, so the filter
    graph sees the rotated size — but any logic that reads stream width/height
    to decide "is this portrait?" gets it exactly backwards. Always ask here.
    """
    data = ffprobe_json(path)
    v = next(s for s in data["streams"] if s["codec_type"] == "video")
    w, h = int(v["width"]), int(v["height"])

    rot = 0.0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = float(sd["rotation"])
    if not rot:
        rot = float(v.get("tags", {}).get("rotate", 0) or 0)

    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h, rot


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def edit_dir(cfg: dict) -> Path:
    d = cfg["_dir"] / "edit"
    d.mkdir(parents=True, exist_ok=True)
    return d


def card_spec(cfg: dict, key) -> dict:
    """Ranges reference cards by index, or the literal string 'title'."""
    if key == "title":
        return cfg["title"]
    return cfg["cards"][int(key)]


def card_name(key) -> str:
    return "title.png" if key == "title" else f"card_{int(key) + 1}.png"
