from io import BytesIO
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# import pivpn_wrapper
from src.fastapi_app import pivpn_wrapper as pivpn

router = APIRouter()
# TODO add authentication for admin routes


@router.get("/get_all_users")
async def get_all_users():
    """get all users"""
    return pivpn.get_all_users()


@router.get("/get_user_qr/{client}")
async def get_user_qr(client: int):
    """get user qr"""
    data = pivpn.get_qr_client(client)
    bio = BytesIO()
    bio.name = "image.jpeg"
    data.save(bio, "JPEG")
    bio.seek(0)
    return StreamingResponse(bio, media_type="image/jpeg")
