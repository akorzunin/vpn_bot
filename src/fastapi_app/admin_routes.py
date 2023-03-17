from datetime import datetime, timezone
from io import BytesIO
import logging
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBasicCredentials
from src.db.schemas import (
    Money,
    PromoCode,
    PromocodeId,
    User,
    UserUpdate,
    VpnConfig,
)

# import pivpn_wrapper
from src.fastapi_app import pivpn_wrapper as pivpn
from src.fastapi_app.auth import check_credentials, security
from src.db import crud
from src.db import promocode_functions
from src import PAYMENT_AMOUNT
from src.tasks.user_tasks import create_user_billing_task

router = APIRouter()
# TODO add authentication for admin routes


@router.post("/add_vpn_config/{vpn_config}")
async def add_vpn_config(vpn_config: str):
    """add vpn_config"""
    try:
        return pivpn.add_vpn_config(vpn_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/backup_vpn_configs")
async def backup_vpn_data(
    credentials: HTTPBasicCredentials = Depends(security),
):
    """backup vpn_configs"""
    check_credentials(credentials)
    return pivpn.backup_vpn_configs()


@router.post("/disable_vpn_config/{vpn_config}")
async def disable_vpn_config(vpn_config: str):
    """disable vpn_config"""
    try:
        return pivpn.disable_vpn_config(
            VpnConfig(user_name=vpn_config, path="")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/enable_vpn_config/{vpn_config}")
async def enable_vpn_config(vpn_config: str):
    """enable vpn_config"""
    try:
        return pivpn.enable_vpn_config(vpn_config)
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


@router.get("/list_vpn_configs")
async def list_vpn_configs():
    """list vpn_configs"""
    return pivpn.list_vpn_configs()


@router.get("/pivpn_user")
async def pivpn_user():
    """pivpn user"""
    return pivpn.whoami()


@router.get("/get_all_users")
async def get_all_users():
    """get all users"""
    return pivpn.get_all_users()


@router.get("/get_vpn_config_qr/{vpn_config}")
async def get_vpn_config_qr(vpn_config: str):
    """get vpn_config qr"""
    data = pivpn.get_vpn_config_qr(vpn_config)
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
    # TODO change UUID to ULID and check number of actually created promocodes
    # TODO crete promocodes for O(n) not O(2n)
    for promocode in promocodes:
        promocode_functions.create_promocode(promocode)
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "created": len(promocodes),
        },
    )


@router.post("/hard_enable_user")
async def hard_enable_user(
    user_id: int,
    balance: Money = PAYMENT_AMOUNT,
    next_payment: datetime = datetime.now(timezone.utc),
):
    """hard enable user"""
    try:
        user = await crud.get_user_by_telegram_id(user_id)
        if user.balance <= 0 or balance != PAYMENT_AMOUNT:
            logging.warning(
                f"User {user_id} balanse changed from {user.balance} to {balance}"
            )
            await crud.update_user(
                user_id,
                UserUpdate(balance=balance),
            )
        if not user.is_enabled:
            logging.warning(f"User {user_id} enabled")
            await crud.enable_user(user_id)
        if user.next_payment is None or user.next_payment < datetime.now(
            timezone.utc
        ):
            logging.warning(
                f"User {user_id} next payment changed from {user.next_payment} to {next_payment}"
            )
            await crud.update_user(
                user_id,
                UserUpdate(next_payment=next_payment),
            )
        await create_user_billing_task(
            await crud.get_user_by_telegram_id(user_id)
        )
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
