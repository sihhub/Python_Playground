from fastapi import APIRouter


router = APIRouter()


@router.get("/", summary="XML to HTML")
async def xml_to_html():
    return {"message": "XML to HTML"}
