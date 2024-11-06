from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

from routes import xml_to_html_router  # routes 폴더에서 불러온 라우트 사용
from pathlib import Path

app = FastAPI(
    docs_url="/docs",
    openapi_url="/openapi.json",
    title="fast Convert API",
    description="fast Convert API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# 기본 경로
@app.get("/", tags=["Root"], summary="Root")
async def root():
    return {"message": "Welcome to the Fast Convert API!"}


app.include_router(xml_to_html_router, prefix="/xml-to-html", tags=["XML, HTML"])


@app.get("/uploads/xml/{file_path:path}")
async def get_file(file_path: str):
    file_location = Path(__file__).parent / "uploads/xml" / file_path
    if not file_location.exists() or not file_location.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_location)
