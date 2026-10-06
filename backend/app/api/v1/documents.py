import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

router = APIRouter(prefix="/documents", tags=["Document Management"])

DOCX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "docx"))

@router.get("/list")
def list_documents():
    """List all PDF and DOCX files currently saved in the docx folder."""
    if not os.path.exists(DOCX_DIR):
        os.makedirs(DOCX_DIR, exist_ok=True)

    files = []
    for fname in os.listdir(DOCX_DIR):
        if fname == ".gitkeep":
            continue
        fpath = os.path.join(DOCX_DIR, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                "name": fname,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": stat.st_mtime,
                "extension": os.path.splitext(fname)[1].lower()
            })
    return sorted(files, key=lambda x: x["modified"], reverse=True)

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Accept one or multiple drag-and-drop uploaded files and save them into the docx directory."""
    if not os.path.exists(DOCX_DIR):
        os.makedirs(DOCX_DIR, exist_ok=True)

    saved = []
    for file in files:
        safe_filename = os.path.basename(file.filename)
        dest_path = os.path.join(DOCX_DIR, safe_filename)
        
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved.append({
            "filename": safe_filename,
            "path": dest_path,
            "size_bytes": os.path.getsize(dest_path)
        })

    return {"message": f"Successfully uploaded {len(saved)} document(s)", "files": saved}

@router.get("/download/{filename}")
def download_document(filename: str):
    """Download or view a document from the docx folder."""
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOCX_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(file_path, filename=safe_filename)

@router.delete("/{filename}")
def delete_document(filename: str):
    """Delete a document from the docx folder."""
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(DOCX_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    os.remove(file_path)
    return {"message": f"File {safe_filename} deleted successfully"}
