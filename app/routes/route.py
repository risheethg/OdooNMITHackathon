from fastapi import APIRouter, Request
from ..utils.responses import response

router = APIRouter(tage=["test"])

@router.get("/")
async def get_rout(request: Request):
    return response.success(None ,"Test works successfully", 200)