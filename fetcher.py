import os
import random
import subprocess

RAW_DIR = "raw_backgrounds"
os.makedirs(RAW_DIR, exist_ok=True)

# Clean, bright gameplay backgrounds (no commentary, no copyrighted music)
BG_QUERIES = [
    "ytsearch3:roblox parkour gameplay no copyright vertical",
    "ytsearch3:minecraft parkour gameplay no copyright 1080p",
    "ytsearch3:gta 5 mega ramp gameplay no commentary 1080p",
    "ytsearch3:subway surfers no commentary gameplay 1080p"
]

def fetch_backgrounds():
    existing = [f for f in os.listdir(RAW_DIR) if f.endswith(".mp4")]
    if len(existing) >= 5:
        print("Enough background videos already cached.")
        return

    query = random.choice(BG_QUERIES)
    cmd = [
        "yt-dlp",
        query,
        "-f", "bestvideo[height<=1080][ext=mp4]/best[ext=mp4]",
        "--match-filter", "duration >= 60 & duration <= 600",
        "--download-archive", "downloaded_bg.txt",
        "--max-downloads", "2",
        "-o", f"{RAW_DIR}/bg_%(id)s.%(ext)s"
    ]
    subprocess.run(cmd, check=False)

if __name__ == "__main__":
    fetch_backgrounds()
