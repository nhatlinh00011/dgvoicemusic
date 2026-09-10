from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
STATIC = BASE / "frontend"

UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

app = FastAPI(title="DG Music Splitter")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


def safe_name(name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ .")
    return "".join(c if c in allowed else "_" for c in name).strip() or "audio"


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout[-8000:])
    return result.stdout


@app.post("/api/split")
async def split_audio(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}:
        raise HTTPException(400, "Định dạng chưa được hỗ trợ.")

    job = uuid.uuid4().hex[:10]
    work = UPLOADS / job
    work.mkdir(parents=True, exist_ok=True)

    input_path = work / ("input" + ext)
    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Demucs writes: separated/<model>/<track>/{vocals,drums,bass,other}.wav
        cmd = [
            sys.executable, "-m", "demucs",
            "-n", "htdemucs",
            "--out", str(work / "separated"),
            str(input_path),
        ]
        run_cmd(cmd)

        stem_dir = work / "separated" / "htdemucs" / input_path.stem
        if not stem_dir.exists():
            raise RuntimeError("Không tìm thấy kết quả Demucs.")

        job_out = OUTPUTS / job
        job_out.mkdir(exist_ok=True)

        result = []
        for stem in ["vocals", "drums", "bass", "other"]:
            src = stem_dir / f"{stem}.wav"
            if src.exists():
                dst = job_out / src.name
                shutil.copy2(src, dst)
                result.append({
                    "name": src.name,
                    "url": f"/api/file/{job}/{src.name}"
                })

        return {"job": job, "files": result}

    except Exception as e:
        shutil.rmtree(work, ignore_errors=True)
        raise HTTPException(500, str(e))


@app.post("/api/midi")
async def make_midi(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".mp3", ".wav", ".flac", ".m4a", ".ogg"}:
        raise HTTPException(400, "Định dạng chưa được hỗ trợ.")

    job = uuid.uuid4().hex[:10]
    work = UPLOADS / job
    work.mkdir(parents=True, exist_ok=True)

    input_path = work / ("input" + ext)
    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    job_out = OUTPUTS / job
    job_out.mkdir(exist_ok=True)

    try:
        # basic-pitch CLI:
        # basic-pitch <output_directory> <input_audio>
        run_cmd([
            sys.executable, "-m", "basic_pitch",
            str(job_out),
            str(input_path)
        ])

        midi_files = list(job_out.glob("*.mid")) + list(job_out.glob("*.midi"))
        if not midi_files:
            raise RuntimeError("Không tạo được MIDI.")

        midi = midi_files[0]
        return {
            "job": job,
            "files": [{
                "name": midi.name,
                "url": f"/api/file/{job}/{midi.name}"
            }]
        }

    except Exception as e:
        shutil.rmtree(work, ignore_errors=True)
        raise HTTPException(500, str(e))


@app.get("/api/file/{job}/{filename}")
def get_file(job: str, filename: str):
    # Prevent path traversal
    clean = Path(filename).name
    path = OUTPUTS / job / clean
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "Không tìm thấy file.")
    return FileResponse(path, filename=clean)


@app.get("/api/health")
def health():
    return {"ok": True, "app": "DG Music Splitter"}
