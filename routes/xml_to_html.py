import io
import os
import re
import zipfile
from typing import Optional
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from saxonche import PySaxonApiError, PySaxonProcessor
from tools import get_error_details
from pathlib import Path


router = APIRouter()

STYLESHEET_DIR = Path(__file__).parent.parent / "stylesheets"
STYLESHEET_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_XML_DIR = Path(__file__).parent.parent / "uploads" / "xml"
UPLOAD_XML_DIR.mkdir(parents=True, exist_ok=True)

HOST = "http://127.0.0.1:8000"

# <link rel="stylesheet" type="text/css" href="isosts.css" />


@router.post("/", summary="XML to HTML")
async def xml_to_html(zip_file: UploadFile = File(...)):
    try:

        zip_file_name = zip_file.filename.rsplit(".", 1)[0]
        upload_dir = UPLOAD_XML_DIR / zip_file_name
        upload_dir.mkdir(parents=True, exist_ok=True)

        xml_text = None

        with zipfile.ZipFile(io.BytesIO(await zip_file.read())) as z:
            for file_path in z.namelist():
                # __MACOSX 폴더 및 ._로 시작하는 파일 무시
                if file_path.startswith("__MACOSX") or file_path.startswith("._"):
                    continue

                if file_path.endswith(".xml"):
                    with z.open(file_path) as f:

                        xml_text = f.read().decode("utf-8")
                        file_name = Path(file_path).name
                        xml_path = upload_dir / file_name

                        with open(xml_path, "w") as xml_out:
                            xml_out.write(xml_text)
                elif file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    with z.open(file_path) as image_file:
                        file_name = Path(file_path).name
                        image_path = upload_dir / file_name

                        with open(image_path, "wb") as img_out:
                            img_out.write(image_file.read())

            if xml_text is None:
                raise HTTPException(status_code=400, detail="No XML file found in zip")

        html_string = convert(xml_text)

        html_string = update_html_paths(html_string, zip_file_name)
        return JSONResponse(
            status_code=201,
            content={
                "xml_text": xml_text,
                "html_string": html_string,
            },
        )

    except PySaxonApiError as e:
        raise HTTPException(status_code=422, detail=get_error_details(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=get_error_details(e))


def convert(xml_text: str) -> str:
    xsl_file = str(STYLESHEET_DIR / "isosts2html_standalone.xsl")

    # 경로가 올바른지 로그로 출력
    print(f"Using XSL file at: {xsl_file}")
    print(f"File exists: {os.path.exists(xsl_file)}")

    if not os.path.exists(xsl_file):
        raise FileNotFoundError(f"The XSL file was not found at path: {xsl_file}")

    with PySaxonProcessor(license=False) as proc:
        xslt_proc = proc.new_xslt30_processor()
        document = proc.parse_xml(xml_text=xml_text)
        executable = xslt_proc.compile_stylesheet(stylesheet_file=xsl_file)
        return executable.transform_to_string(xdm_node=document)


def update_html_paths(html_string: str, zip_file_name: str) -> str:
    """
    HTML 문자열 내 이미지와 CSS 경로를 업데이트합니다.
    """
    html_string = html_string.replace(
        'src="', f'src="{HOST}/uploads/xml/{zip_file_name}/'
    )

    css_url = f"{HOST}/stylesheets/isosts.css"

    html_string = html_string.replace(
        '<link rel="stylesheet" type="text/css" href="isosts.css" />',
        f'<link rel="stylesheet" type="text/css" href="{css_url}" />',
    )

    return html_string
