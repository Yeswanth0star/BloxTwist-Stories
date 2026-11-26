import os
import json
import random
import asyncio
import subprocess
import whisper
import edge_tts
from google import genai

RAW_DIR = "raw_backgrounds"
TEMP_DIR = "temp_build"
READY_DIR = "ready_to_upload"
HISTORY_FILE = "past_titles.txt"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(READY_DIR, exist_ok=True)

NICHES = [
    "Mind-bending sci-fi world where everyone has a hidden rule, timer, or number above their head",
    "Creepy two-sentence horror expanded into a suspenseful 50-second first-person mystery",
    "Emotional plot-twist story about family, friendship, or sacrifice with a shocking ending",
    "Impossible survival choice where one small decision saves or dooms the main character",
    "Weird glitch in reality / parallel universe story that feels eerily real",
    "Unexplained true-style mystery or urban legend told in fast first-person storytelling"
]

VOICES = [
    "en-US-ChristopherNeural",
    "en-US-GuyNeural",
    "en-US-AndrewNeural"
]

OFFLINE_FALLBACK = {
    "title": "You Can Only See How People Die… Until You Look In A Mirror 😱 #shorts",
    "description": "Every time I touch someone, I see their final second. Today I accidentally touched my own reflection.\n\n#shorts #storytime #plottwist #scary",
    "tags": ["shorts", "storytime", "plot twist", "scary story", "viral"],
    "script": "Since I was ten years old, every time I shook someone's hand, I saw a three second flash of how they would die. Most were peaceful. Old age in a hospital bed. Sleep. Nothing scary. So I started wearing gloves everywhere just to live a normal life. Yesterday, a kid dropped his basketball into the street right in front of a speeding truck. Without thinking, I pulled my glove off, grabbed his arm, and yanked him back onto the sidewalk. I braced myself for the vision. Instead, I saw nothing. Complete darkness. Confused, I looked at the kid, and he smiled and said, thank you, you saved me. Then I realized why I saw nothing. You can only see someone's future if they still have one. And when I looked down at my own bare hand, the vision finally started."
}

def generate_infinite_story():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("No GEMINI_API_KEY found, using offline fallback story.")
        return OFFLINE_FALLBACK

    past_titles = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            past_titles = [line.strip() for line in f if line.strip()][-50:]

    niche = random.choice(NICHES)
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a viral YouTube Shorts scriptwriter getting millions of views.
Write ONE completely original, addictive first-person story in this niche:
"{niche}"

Strict rules:
1. Hook in the VERY FIRST SENTENCE (shocking rule, mystery, or dilemma in under 12 words).
2. Length: 115 to 140 words (about 45 to 55 seconds spoken).
3. Simple everyday English, fast pacing, short punchy sentences, and a jaw-dropping twist in the final sentence.
4. Family-friendly / YouTube safe (no gore, no self-harm, no profanity).
5. Must be completely different from these past titles: {past_titles}

Return ONLY valid JSON with these exact keys:
{{
  "title": "Catchy curiosity title under 70 chars with 1 emoji and #shorts",
  "description": "2-sentence teaser + 4 relevant hashtags",
  "tags": ["shorts", "storytime", "plottwist", "viral", "stories"],
  "script": "The full spoken narration text only, no stage directions"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI generation failed ({e}), using offline fallback.")
        return OFFLINE_FALLBACK

async def generate_tts(text, out_audio):
    voice = random.choice(VOICES)
    communicate = edge_tts.Communicate(text, voice, rate="+13%")
    await communicate.save(out_audio)

def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    return float(subprocess.check_output(cmd).decode().strip())

def format_timestamp(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def create_srt(audio_path, srt_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    with open(srt_path, "w", encoding="utf-8") as f:
        idx = 1
        for seg in result["segments"]:
            words = seg.get("words", [])
            for i in range(0, len(words), 3):
                chunk = words[i:i+3]
                if not chunk:
                    continue
                start = format_timestamp(chunk[0]["start"])
                end = format_timestamp(chunk[-1]["end"])
                text = " ".join(w["word"].strip() for w in chunk).upper()
                f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
                idx += 1

def build_short():
    bgs = [os.path.join(RAW_DIR, x) for x in os.listdir(RAW_DIR) if x.endswith((".mp4", ".webm"))]
    if not bgs:
        print("No background videos in raw_backgrounds/!")
        return

    story = generate_infinite_story()
    vid_id = f"short_{random.randint(100000, 999999)}"
    bg_video = random.choice(bgs)

    audio_path = os.path.join(TEMP_DIR, f"{vid_id}.mp3")
    srt_path = os.path.join(TEMP_DIR, f"{vid_id}.srt")
    out_video = os.path.join(READY_DIR, f"{vid_id}.mp4")
    out_meta = os.path.join(READY_DIR, f"{vid_id}.json")

    print(f"Generating voiceover for: {story['title']}")
    asyncio.run(generate_tts(story["script"], audio_path))

    audio_dur = get_duration(audio_path) + 0.5
    bg_dur = get_duration(bg_video)
    max_start = max(0, bg_dur - audio_dur - 2)
    start_time = random.uniform(0, max_start) if max_start > 0 else 0

    print("Transcribing exact word timestamps...")
    create_srt(audio_path, srt_path)
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    vf = (
        f"crop=ih*9/16:ih,scale=1080:1920,"
        f"subtitles='{srt_escaped}':force_style='FontName=Arial Black,FontSize=19,"
        f"PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,"
        f"Alignment=10,MarginV=50'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-t", str(audio_dur),
        "-i", bg_video,
        "-i", audio_path,
        "-vf", vf,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        out_video
    ]
    subprocess.run(cmd, check=True)

    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump({
            "title": story["title"],
            "description": story["description"],
            "tags": story["tags"],
            "categoryId": "24"
        }, f, ensure_ascii=False, indent=2)

    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(story["title"] + "\n")

    print(f"Built ready Short: {out_video}")

if __name__ == "__main__":
    build_short()
