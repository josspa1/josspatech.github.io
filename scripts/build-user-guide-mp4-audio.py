#!/usr/bin/env python3
"""Generate all 89 EN MP3s and mux onto existing MP4 — single atomic pipeline."""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
AUDIO = HTML.parent / "audio"
MP4 = HTML.parent / "pocketbudjet-user-guide.mp4"
VOICE = "en-US-AndrewNeural"
SLIDES = 89
SLIDE_SEC = 8


def extract_texts() -> list[str]:
    html = HTML.read_text(encoding="utf-8")
    m = re.search(r"const NARRATION = \[(.*?)\];", html, re.S)
    texts = [t.replace('\\"', '"') for t in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
    if len(texts) != SLIDES:
        raise SystemExit(f"Expected {SLIDES} NARRATION strings, got {len(texts)}")
    return texts


def ffprobe_ok(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 5000:
        return False
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
    )
    return r.returncode == 0


def gen_mp3(text: str, out: Path) -> None:
    for attempt in range(8):
        try:
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(out)],
                check=True, capture_output=True, text=True,
            )
            if ffprobe_ok(out):
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"Failed: {out.name}")


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit((r.stderr or r.stdout or "")[-800:])


def main() -> None:
    texts = extract_texts()
    AUDIO.mkdir(parents=True, exist_ok=True)
    print(f"[1/3] Validating {SLIDES} MP3s")
    for i, text in enumerate(texts):
        out = AUDIO / f"slide-{i}.mp3"
        if ffprobe_ok(out):
            continue
        print(f"  [{i+1}/{SLIDES}] regen {out.name} ({len(text)} chars)")
        gen_mp3(text, out)
        time.sleep(0.4)

    tmp = AUDIO / "_mux_tmp"
    tmp.mkdir(exist_ok=True)
    segs = []
    print(f"[2/3] Building {SLIDE_SEC}s/slide audio track")
    for i in range(SLIDES):
        seg = tmp / f"seg-{i:03d}.m4a"
        run([
            "ffmpeg", "-y", "-i", str(AUDIO / f"slide-{i}.mp3"),
            "-af", f"apad=whole_dur={SLIDE_SEC}", "-t", str(SLIDE_SEC),
            "-c:a", "aac", "-b:a", "128k", str(seg),
        ])
        segs.append(seg)
    lst = tmp / "concat.txt"
    lst.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs), encoding="utf-8")
    combined = HTML.parent / "_combined-narration.m4a"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "aac", "-b:a", "128k", str(combined)])

    if not MP4.exists():
        raise SystemExit(f"Missing video: {MP4}")
    tmp_out = MP4.with_suffix(".muxing.mp4")
    print("[3/3] Muxing video + narration")
    run([
        "ffmpeg", "-y", "-i", str(MP4), "-i", str(combined),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(tmp_out),
    ])
    tmp_out.replace(MP4)
    for s in segs:
        s.unlink(missing_ok=True)
    lst.unlink(missing_ok=True)
    combined.unlink(missing_ok=True)
    try:
        tmp.rmdir()
    except OSError:
        pass

    probe = subprocess.run(["ffmpeg", "-i", str(MP4), "-hide_banner"], capture_output=True, text=True)
    has_audio = "Audio:" in (probe.stderr or "")
    size_mb = MP4.stat().st_size / (1024 * 1024)
    print(f"Done: {MP4} ({size_mb:.1f} MB, hasAudio={has_audio})")


if __name__ == "__main__":
    main()
