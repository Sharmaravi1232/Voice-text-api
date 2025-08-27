# app.py
import os
import tempfile
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from gradio_client import Client, handle_file
import uvicorn

app = FastAPI(title="Audio Transcription API (via URL)")

# Hugging Face client
try:
    client = Client("Ravishankarsharma/voice2text-summarizer")
except Exception as e:
    print("Warning: Hugging Face client failed:", e)
    client = None

# ✅ Pydantic model for URL input
class AudioURL(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
    <html><body>
    <h2>Submit an audio URL to transcribe:</h2>
    <form action="/transcribe_url" method="post">
    <input name="url" type="text" placeholder="Enter audio URL" required>
    <button type="submit">Transcribe</button>
    </form>
    <p>Swagger: <a href="/docs">/docs</a></p>
    </body></html>
    """)

# ✅ New endpoint: Accepts URL instead of file
@app.post("/transcribe_url")
async def transcribe_from_url(audio: AudioURL):
    if not client:
        raise HTTPException(status_code=500, detail="Hugging Face client not initialized")

    try:
        # 1. Download the audio file from given URL
        response = requests.get(audio.url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download audio file from URL")

        # 2. Save it temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp_path = tmp.name

        # 3. Send to Hugging Face model
        result = client.predict(handle_file(tmp_path), api_name="/predict")
        os.remove(tmp_path)

        return {
            "source_url": audio.url,
            "transcription": result[0],
            "summary": result[1],
            "api_endpoint": result[2]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Server running at http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
