from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from compressGhostScript import compress_pdf
import uvicorn
import os
import shutil
from pathlib import Path

app = Fastapi = FastAPI(title="PDF Compressor")

QUALITY_MAP = ['screen','ebook','printer','prepress']

print("Running from:", os.getcwd())
BASE_DIR = os.getcwd()
# BASE_DIR = Path(__file__).resolve().parent

@app.post("/compress", response_class=FileResponse)
def compress( file: UploadFile = File(...), quality: str = Form("screen")):

    # validate mime
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # validate quality
    if quality not in QUALITY_MAP:
        raise HTTPException(status_code=400, detail=f"quality must be one of {list(QUALITY_MAP.keys())}")
    
    file_size_kb = file.size / 1024 # convert to kbs
    file_size_mb = file_size_kb / 1024 # convert to mbs
    
    file_path = os.path.join(BASE_DIR+'/files/', file.filename)
    
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    output_path = Path(file_path.replace('.pdf','_compressed.pdf'))

    compress_pdf(file_path, output_path=output_path, quality=quality)

    compressed_file_size_kb = Path(output_path).stat().st_size / 1024
    compressed_file_size_mb = compressed_file_size_kb / 1024

    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=file.filename.replace('.pdf','_compressed.pdf'),
        headers={
            "X-File-Size-MB": f"{file_size_mb:.4f} mb",
            "X-File-Size-Compressed-MB": f"{compressed_file_size_mb:.4f} mb",
            "X-Compression-Status": "success"
        }
    )
    
        

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8084,
        log_level="debug",
    )