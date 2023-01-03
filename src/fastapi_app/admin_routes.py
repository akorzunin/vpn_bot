from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# import pivpn_wrapper
from src.fastapi_app import pivpn_wrapper as pivpn

router = APIRouter()
# TODO add authentication for admin routes


@router.get("/get_all_users")
async def get_all_users():
    """get all users"""
    return pivpn.get_all_users()
