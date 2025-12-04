# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid, os, threading, time

from .morse_generator import generate_morse_video

app = FastAPI()

# Allow frontend (served from file:// or another host) to call this API during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during dev; lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "videos")

class Message(BaseModel):
    text: str

def schedule_delete(path: str, delay: int = 30):
    def _del():
        time.sleep(delay)
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    threading.Thread(target=_del, daemon=True).start()

@app.post("/generate")
def generate(msg: Message):
    if not msg.text or not msg.text.strip():
        raise HTTPException(status_code=400, detail="Empty message")
    uid = str(uuid.uuid4())
    out_path = os.path.abspath(os.path.join(VIDEOS_DIR, f"{uid}.mp4"))
    try:
        generate_morse_video(msg.text, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # schedule delete after 60 seconds (so frontend can download/play)
    schedule_delete(out_path, delay=60)
    return {"file_url": f"/video/{uid}"}

@app.get("/video/{uid}")
def serve_video(uid: str):
    path = os.path.abspath(os.path.join(VIDEOS_DIR, f"{uid}.mp4"))
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="video/mp4", filename=f"{uid}.mp4")
