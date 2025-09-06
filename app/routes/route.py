from fastapi import APIRouter, Request
from ..utils.responses import response

router = APIRouter(tags=["test"])

@router.get("/test")
async def get_rout(request: Request):
    return response.success(None ,"Test works successfully", 200)