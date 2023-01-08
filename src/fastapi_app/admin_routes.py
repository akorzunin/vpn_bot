from io import BytesIO
from typing import Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# import pivpn_wrapper
from src.fastapi_app import pivpn_wrapper as pivpn

router = APIRouter()
# TODO add authentication for admin routes


@router.post("/add_client/{client}")
async def add_client(client: str):
    """add client"""
    try:
        return pivpn.add_client(client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/backup_clients")
async def backup_clients():
    """backup clients"""
    return pivpn.backup_clients()


@router.post("/disable_client/{client}")
async def disable_client(client: str):
    """disable client"""
    try:
        return pivpn.disable_client(client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/enable_client/{client}")
async def enable_client(client: str):
    """enable client"""
    try:
        return pivpn.enable_client(client)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/list_clients")
async def list_clients():
    """list clients"""
    return pivpn.list_clients()


@router.get("/pivpn_user")
async def pivpn_user():
    """pivpn user"""
    return pivpn.whoami()


@router.get("/get_all_users")
async def get_all_users():
    """get all users"""
    return pivpn.get_all_users()


@router.get("/get_user_qr/{client}")
async def get_user_qr(client: str):
    """get user qr"""
    data = pivpn.get_qr_client(client)
    bio = BytesIO()
    bio.name = "image.jpeg"
    data.save(bio, "JPEG")
    bio.seek(0)
    return StreamingResponse(bio, media_type="image/jpeg")


@router.get("/speed_test")
async def speed_test(type: Literal["full", ""] = ""):
    """speed test"""
    return pivpn.get_speed_test(type)
