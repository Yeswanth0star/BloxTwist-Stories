import os
import random
import subprocess

RAW_DIR = "raw_backgrounds"
os.makedirs(RAW_DIR, exist_ok=True)

PALETTES = [
    ("0x0f0c29", "0x302b63", "0x24243e"),
    ("0x1a002b", "0x4a0072", "0x004d40"),
    ("0x001f3f", "0x0074D9", "0x111111"),
    ("0x2b0909", "0x7a1c1c", "0x1c1c1c"),
    ("0x09203f", "0x537895", "0x141e30")
]

def generate_procedural_bg():
    out_path = os.path.join(RAW_DIR, "bg_generated.mp4")
    c0, c1, c2 = random.choice(PALETTES)
    hue_speed = random.choice([8, 12, 16, 20])
    print("Generating clean 1080x1920 animated background via FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"gradients=s=1080x1920:d=75:r=30:c0={c0}:c1={c1}:c2={c2}:speed=0.06",
        "-vf", f"hue=H={hue_speed}*t:s=1.4,noise=alls=8:allf=t+u",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True)
    print("Background ready!")

if __name__ == "__main__":
    generate_procedural_bg()

