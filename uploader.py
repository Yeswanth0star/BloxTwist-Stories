import os
import json
import shutil
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

READY_DIR = "ready_to_upload"
UPLOADED_DIR = "uploaded_archive"
os.makedirs(UPLOADED_DIR, exist_ok=True)

def get_youtube_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"].strip(),
        token_uri="https://googleapis.com",
        client_id=os.environ["YT_CLIENT_ID"].strip(),
        client_secret=os.environ["YT_CLIENT_SECRET"].strip(),
        scopes=["https://googleapis.com"]
    )
    return build("youtube", "v3", credentials=creds)

def upload_one_short():
    videos = sorted([f for f in os.listdir(READY_DIR) if f.endswith(".mp4")])
    if not videos:
        print("No videos ready to upload.")
        return

    video_file = videos[0]
    base_name = os.path.splitext(video_file)[0]

def upload_one_short():
    videos = sorted([f for f in os.listdir(READY_DIR) if f.endswith(".mp4")])
    if not videos:
        print("No videos ready to upload.")
        return

    video_file = videos[0]
    base_name = os.path.splitext(video_file)[0]
    video_path = os.path.join(READY_DIR, video_file)
    meta_path = os.path.join(READY_DIR, f"{base_name}.json")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    youtube = get_youtube_service()
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": meta.get("categoryId", "24")
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    print(f"Uploading: {meta['title']}")
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()

    print(f"Live on YouTube! Video ID: {response['id']}")
    shutil.move(video_path, os.path.join(UPLOADED_DIR, video_file))
    shutil.move(meta_path, os.path.join(UPLOADED_DIR, f"{base_name}.json"))

if __name__ == "__main__":
    upload_one_short()
