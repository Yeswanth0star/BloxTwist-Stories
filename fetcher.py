import os
import random
import subprocess
import urllib.request

RAW_DIR = "raw_backgrounds"
os.makedirs(RAW_DIR, exist_ok=True)

# Direct, unblockable public-domain / CC0 high-motion background video URLs
DIRECT_BG_URLS = [
    "https://wikimedia.org",
    "https://googleapis.com",
    "https://googleapis.com",
    "https://googleapis.com",
    "https://googleapis.com"
]

def generate_procedural_bg(out_path):
    """Generates a smooth, hypnotic 75-second 1080x1920 neon plasma wave video using FFmpeg if downloads fail."""
    print("Generating procedural neon background via FFmpeg...")
    hue_speed = random.choice([25, 40, 60])
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "gradients=s=1080x1920:d=75:r=30:c0=0x0f0c29:c1=0x302b63:c2=0x24243e:speed=0.05",
        "-vf", f"hue=H={hue_speed}*t:s=1.4,noise=alls=8:allf=t+u",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
        out_path
    ]
    subprocess.run(cmd, check=True)

def fetch_backgrounds():
    existing = [f for f in os.listdir(RAW_DIR) if f.endswith((".mp4", ".webm"))]
    if existing:
        print(f"Found {len(existing)} background(s) ready.")
        return

    # Try downloading 1 clean direct video first
    url = random.choice(DIRECT_BG_URLS)
    ext = ".webm" if url.endswith(".webm") else ".mp4"
    out_file = os.path.join(RAW_DIR, f"bg_{random.randint(1000,9999)}{ext}")

    try:
        print(f"Downloading background from {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(out_file, "wb") as f:
            f.write(resp.read())
        print("Download succeeded!")
    except Exception as e:
        print(f"Download failed ({e}), falling back to FFmpeg procedural background...")
        if os.path.exists(out_file):
            os.remove(out_file)
        generate_procedural_bg(os.path.join(RAW_DIR, "bg_generated.mp4"))

if __name__ == "__main__":
    fetch_backgrounds()
