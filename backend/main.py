from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from compressGhostScript import compress_pdf
from fastapi import BackgroundTasks
from pathlib import Path
from pydantic import BaseModel
import uvicorn
import os
import shutil
import logging
import tempfile
import mimetypes
import subprocess

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Compressor")

QUALITY_MAP = ['screen','ebook','printer','prepress']

print("Running from:", os.getcwd())

# Base directory and ensure paths exist
BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / 'files'
DIST_DIR = BASE_DIR / 'dist'

logger.info(f"Running from: {os.getcwd()}")
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Files directory: {FILES_DIR}")
logger.info(f"Dist directory: {DIST_DIR}")

# Create the directory if it does not exist
FILES_DIR.mkdir(exist_ok=True)  

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition",
        "X-File-Size-MB",
        "X-File-Size-Compressed-MB",
        "X-Compression-Status",
        "X-Filename",
    ],
)

def is_pdf_file(file: UploadFile) -> bool:
    """Validate if the uploaded file is a PDF"""
    # Check content type:
    if file.content_type in ("application/pdf", "application/octet-stream"):
        return True

    # Check file extension as fallback:
    if file.filename and file.filename.lower().endswith('.pdf'):
        return True
    return False

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running"""
    return {"status": "healthy", "service": "PDF Compressor"}

@app.post("/compress", response_class=FileResponse)
async def compress( 
    file: UploadFile = File(...), 
    quality: str = Form("screen")
):

    logger.info(f"Received compression request: file={file.filename}, quality={quality}")

    # Validate file type
    if not is_pdf_file(file):
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a valid PDF file."
        )
    
    # Validate quality
    if quality not in QUALITY_MAP:
        logger.error(f"Invalid quality: {quality}")
        raise HTTPException(
            status_code=400,
            detail=f"Quality must be one of {QUALITY_MAP}"
        )

        # Validate file size
    if not file.size or file.size == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    
    # Check file size limit (50MB)
    max_file_size = 50 * 1024 * 1024 
    if file.size > max_file_size:
        raise HTTPException(
            status_code=400, 
            detail="File too large. Maximum size is 50MB."
        )

    file_size_mb = file.size / (1024 * 1024)
    
    # Generate unique filenames
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{unique_id}_{file.filename}"
    
    input_path = FILES_DIR / safe_filename
    output_path = FILES_DIR / safe_filename.replace('.pdf', '_compressed.pdf')

    try:
        logger.info(f"Saving file to: {input_path}")
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved successfully. Size: {file_size_mb:.2f}MB")
        
        # Compress the PDF
        logger.info(f"Starting compression with quality: {quality}")
        compress_pdf(str(input_path), str(output_path), quality=quality)
        
        # Verify compression was successful
        if not output_path.exists():
            logger.error("Compression failed - output file not created")
            raise HTTPException(status_code=500, detail="PDF compression failed.")
        
        compressed_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"Compression successful. Original: {file_size_mb:.2f}MB, Compressed: {compressed_size_mb:.2f}MB")
        
        # Prepare response filename
        response_filename = file.filename.replace('.pdf', '_compressed.pdf')
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=response_filename,
            headers={
                "X-File-Size-MB": f"{file_size_mb:.4f} MB",
                "X-File-Size-Compressed-MB": f"{compressed_size_mb:.4f} MB",
                "X-Compression-Status": "success",
                "X-Filename": response_filename
            }
        )
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript compression failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail="PDF compression failed. The file may be corrupted or unsupported."
        )
    except Exception as e:
        logger.error(f"Unexpected error during compression: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Processing error: {str(e)}"
        )
    finally:
        # Clean up input file
        try:
            if input_path.exists():
                input_path.unlink()
                logger.info(f"Cleaned up input file: {input_path}")
        except Exception as e:
            logger.error(f"Failed to clean up input file: {e}")

@app.get('/removeFiles')
async def remove_files():
    """Clean up all files in the files directory"""
    try:
        files_removed = 0
        for item in FILES_DIR.iterdir():
            if item.is_file():
                item.unlink()
                files_removed += 1
        
        logger.info(f"Cleaned up {files_removed} files")
        return {"message": f"Successfully removed {files_removed} files."}
    except Exception as e:
        logger.error(f"Failed to clean files: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to clean files: {str(e)}"}
        )

# Mount static files
if DIST_DIR.exists() and DIST_DIR.is_dir():
    logger.info(f"Mounting static files from: {DIST_DIR}")
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="frontend")
else:
    logger.warning(f"Frontend dist directory not found at {DIST_DIR}")
    
    @app.get("/")
    async def root():
        return {"message": "PDF Compressor API is running. Frontend not available."}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8084,
        log_level="debug",
    )