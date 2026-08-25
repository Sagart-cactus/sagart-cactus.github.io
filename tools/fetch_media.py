#!/usr/bin/env python3
"""Download article images and convert animated GIFs to MP4.

LinkedIn serves the explainer diagrams as GIF. The animated ones are large
(up to 2.6 MB each, ~23 MB in total); re-encoded to H.264 they lose roughly two
orders of magnitude with no visible difference, and a <video autoplay loop muted
playsinline> behaves like a GIF in every browser we care about.

Writes assets/articles/<slug>/NN.<ext> and records a "media" list on each article
in articles.json for build_site.py to render.

Requires ffmpeg on PATH. Usage:  python tools/fetch_media.py
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ARTICLES_JSON = os.path.join(HERE, "articles.json")
MEDIA_ROOT = os.path.join(ROOT, "assets", "articles")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)
REQUEST_DELAY = 0.8
GIF_FRAME_MARKER = b"\x21\xF9\x04"          # graphic control extension


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def probe(data: bytes) -> tuple[str, int, int, int]:
    """Return (kind, width, height, frames) for the downloaded bytes."""
    if data[:3] == b"GIF":
        width, height = struct.unpack("<HH", data[6:10])
        return "gif", width, height, data.count(GIF_FRAME_MARKER)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return "png", width, height, 1
    if data[:2] == b"\xff\xd8":
        return "jpg", 0, 0, 1
    return "bin", 0, 0, 1


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {result.stderr.strip()[:200]}")


def video_size(path: str) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
        capture_output=True, text=True, check=True).stdout.strip()
    width, height = out.split("x")[:2]
    return int(width), int(height)


def convert_animation(gif_path: str, stem: str) -> dict:
    """Animated GIF to H.264 MP4 plus a poster frame."""
    mp4 = f"{stem}.mp4"
    poster = f"{stem}.jpg"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", gif_path,
         "-movflags", "faststart", "-pix_fmt", "yuv420p",
         # H.264 requires even dimensions
         "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
         "-crf", "28", mp4])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", gif_path,
         "-vframes", "1", "-q:v", "4", poster])
    width, height = video_size(mp4)
    return {
        "type": "video",
        "src": os.path.basename(mp4),
        "poster": os.path.basename(poster),
        "width": width,
        "height": height,
        "bytes": os.path.getsize(mp4) + os.path.getsize(poster),
    }


def process(article: dict) -> list[dict]:
    slug = article["slug"]
    out_dir = os.path.join(MEDIA_ROOT, slug)
    os.makedirs(out_dir, exist_ok=True)
    media = []

    for index, image in enumerate(article.get("images", [])):
        data = download(image["url"])
        kind, width, height, frames = probe(data)
        stem = os.path.join(out_dir, f"{index:02d}")

        if kind == "gif" and frames > 1:
            gif_path = f"{stem}.gif"
            with open(gif_path, "wb") as handle:
                handle.write(data)
            try:
                entry = convert_animation(gif_path, stem)
            finally:
                os.remove(gif_path)          # keep only the encoded output
        else:
            ext = "png" if kind == "png" else ("jpg" if kind == "jpg" else "gif")
            path = f"{stem}.{ext}"
            with open(path, "wb") as handle:
                handle.write(data)
            entry = {
                "type": "image",
                "src": os.path.basename(path),
                "width": width,
                "height": height,
                "bytes": os.path.getsize(path),
            }

        entry["linkedin_alt"] = image.get("linkedin_alt", "")
        entry["source_bytes"] = len(data)
        media.append(entry)
        print(f"  [{index}] {entry['type']:5} {entry.get('width')}x{entry.get('height')}"
              f"  {len(data) / 1024:>7.0f} KB -> {entry['bytes'] / 1024:>6.0f} KB")
        time.sleep(REQUEST_DELAY)

    return media


def main() -> int:
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found on PATH", file=sys.stderr)
        return 1

    with open(ARTICLES_JSON, encoding="utf-8") as handle:
        articles = json.load(handle)

    before = after = 0
    for article in articles:
        if not article.get("images"):
            article["media"] = []
            continue
        print(f"{article['slug']}")
        article["media"] = process(article)
        before += sum(m["source_bytes"] for m in article["media"])
        after += sum(m["bytes"] for m in article["media"])

    with open(ARTICLES_JSON, "w", encoding="utf-8") as handle:
        json.dump(articles, handle, indent=1)

    total = sum(len(a.get("media", [])) for a in articles)
    print(f"\n{total} files  {before / 1024 / 1024:.1f} MB source "
          f"-> {after / 1024 / 1024:.1f} MB shipped "
          f"({before / after:.0f}x smaller)" if after else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
