from typing import Optional

from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from saxonche import PySaxonApiError, PySaxonProcessor

from tools import get_error_details


router = APIRouter()


@router.get("/", summary="XML to HTML")
async def xml_to_html(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    print("xml_to_html", file, text)
    try:
        if file is not None:
            xml_text = await file.read()
            xml_text = xml_text.decode("utf-8")
        elif text is not None:
            xml_text = text
        else:
            raise HTTPException(status_code=400, detail="No file or text provided")
        html_string = convert(xml_text)
        return HTMLResponse(
            status_code=201,
            content=html_string,
        )

    except PySaxonApiError as e:
        raise HTTPException(status_code=422, detail=get_error_details(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=get_error_details(e))


def convert(xml_text: str) -> str:
    xsl_file = "../assets/templates/isosts2html_standalone.xsl"
    with PySaxonProcessor(license=False) as proc:
        xslt_proc = proc.new_xslt30_processor()
        document = proc.parse_xml(xml_text=xml_text)
        executable = xslt_proc.compile_stylesheet(stylesheet_file=xsl_file)
        return executable.transform_to_string(xdm_node=document)
