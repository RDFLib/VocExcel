from fastapi import APIRouter, UploadFile, HTTPException, status

from vocexcel.convert import excel_to_rdf
from vocexcel.web.response import TurtleResponse

router = APIRouter()


@router.get("/")
def home_route():
    return "Home"


@router.post("/convert", response_class=TurtleResponse)
async def convert_route(upload_file: UploadFile):
    try:
        file = upload_file.file
        result = excel_to_rdf(file)
        return TurtleResponse(result)
    except Exception as err:
        import traceback
        tb = traceback.format_exception(err)
        print(tb)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='There was an error processing the file.'
        ) from err
