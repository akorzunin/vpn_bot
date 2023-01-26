from io import BytesIO
import logging
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBasicCredentials
from src.db.schemas import Money, PromoCode, PromocodeId, User

# import pivpn_wrapper
from src.fastapi_app import pivpn_wrapper as pivpn
from src.fastapi_app.auth import check_credentials, security
from src.db import crud
from src.db import promocode_functions

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
async def backup_clients(
    credentials: HTTPBasicCredentials = Depends(security),
):
    """backup clients"""
    check_credentials(credentials)
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


# TODO add diasble user


@router.post("/enable_user/{user_id}")
async def enable_user(user_id: int):
    """enable user"""
    try:
        user = await crud.get_user_by_telegram_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_enabled:
            raise HTTPException(status_code=400, detail="User already enabled")
        await crud.enable_user(user_id)
        return JSONResponse(
            status_code=200, content={"message": "User enabled"}
        )
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


@router.post("/create_payment")
async def create_payment(
    amount: Money,
    user_name: str = "",
    user_id: int | None = None,
):
    """create payment"""
    # if user_id is dfeined, then user_name is ignored
    if user_id is None:
        user = await crud.get_user_by_user_name(user_name)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="User not found and user id is not provided",
            )
        user_id = user.telegram_id
    if user_id:
        await crud.create_payment(user_id, amount)
        return JSONResponse(status_code=200, content={"status": "ok"})
    raise HTTPException(status_code=400, detail="User of user id not found")


@router.post("/create_invoice")
async def create_invoice(
    amount: Money,
    user_name: str = "",
    user_id: int | None = None,
):
    """create invoice"""
    # if user_id is dfeined, then user_name is ignored
    if user_id is None:
        user = await crud.get_user_by_user_name(user_name)
        if not user:
            raise HTTPException(
                status_code=400,
                detail="User not found and user id is not provided",
            )
        user_id = user.telegram_id
    if user_id:
        await crud.create_invoice(user_id, amount)
        return JSONResponse(status_code=200, content={"status": "ok"})
    raise HTTPException(status_code=400, detail="User of user id not found")


@router.post("/create_promocode")
async def create_promocode(
    function: Literal["add_balance", "activate_user"],
    value: str = "",
    quantity: int = 1,
    alias: str = "",
):
    """create promocode"""
    promocodes = [
        PromoCode(
            id=PromocodeId(uuid4()),
            function=function,
            value=value,
            alias=alias,
        )
        for _ in range(quantity)
    ]

    for promocode in promocodes:
        data = promocode_functions.create_promocode(promocode)
        if data > 1:
            logging.warning(f"Promocode {promocode.id} already exists")
    return JSONResponse(status_code=200, content={"status": "ok"})
