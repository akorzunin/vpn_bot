"""fastapi router for user routes"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials

from src.db import crud, promocode_functions
from src.db.schemas import User, UserUpdate, VpnConfig
from src.fastapi_app import pivpn_wrapper as pivpn
from src.fastapi_app.auth import check_credentials, security


router = APIRouter()


@router.get("/get_user/{user_id}")
async def get_user_by_id(
    user_id: int,
    credentials: HTTPBasicCredentials = Depends(security),
):
    check_credentials(credentials)
    user = await crud.find_user_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/create_user")
async def create_user(
    user: User,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """create user"""
    check_credentials(credentials)
    if await crud.find_user_by_telegram_id(user.telegram_id):
        # return 400
        return JSONResponse(status_code=400, content="User already exists")
    await crud.create_user(user)
    return JSONResponse(status_code=201, content={"message": "User created"})


# update user
@router.put("/update_user/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """update user"""
    check_credentials(credentials)
    if await crud.find_user_by_telegram_id(user_id):
        await crud.update_user(user_id, user)
        return JSONResponse(
            status_code=200, content={"message": "User updated"}
        )
    return JSONResponse(status_code=400, content="User not found")


@router.get("/get_all_users")
async def get_all_users(credentials: HTTPBasicCredentials = Depends(security)):
    """get all users"""
    check_credentials(credentials)
    return await crud.get_all_users()


# delete user
@router.delete("/delete_user/{telegram_id}")
async def delete_user(
    telegram_id: int,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """delete user"""
    check_credentials(credentials)
    user = await crud.find_user_by_telegram_id(telegram_id)
    if not user:
        return JSONResponse(status_code=404, content="User not found")
    await crud.delete_user(user)
    return JSONResponse(status_code=200, content={"message": "User deleted"})


@router.post("/add_vpn_config/{user_id}")
async def add_vpn_config(
    user_id: int,
    vpn_config: VpnConfig,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """add given vpn config to user by its telegram_id"""
    check_credentials(credentials)
    if await crud.get_user_by_telegram_id(user_id):
        try:
            crud.add_vpn_config(user_id, vpn_config)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return JSONResponse(
            status_code=200, content={"message": "Vpn config added"}
        )
    return JSONResponse(status_code=400, content="User not found")


@router.delete("/remove_vpn_config/{user_id}")
async def remove_vpn_config(
    user_id: int,
    vpn_user: str,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """remove vpn config"""
    check_credentials(credentials)
    if await crud.get_user_by_telegram_id(user_id):
        crud.remove_vpn_config(user_id, vpn_user)
        return JSONResponse(
            status_code=200, content={"message": "Vpn config removed"}
        )
    return JSONResponse(status_code=400, content="User not found")


@router.get("/get_vpn_config/{file_path}")
async def get_vpn_config(
    file_path: str,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """get vpn config from PIVPN"""
    check_credentials(credentials)
    try:
        return pivpn.get_config_by_filepath(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/redeem_code")
async def redeem_code(
    user_id: int,
    code_alias: str = "",
    code_id: UUID | None = None,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """redeem code"""
    check_credentials(credentials)
    try:
        if prmocode_id := promocode_functions.use_check_promocode(
            user_id,
            code_alias,
            code_id,
        ):
            return JSONResponse(
                status_code=200,
                content={"message": "Code redeemed", "id": prmocode_id},
            )
        raise HTTPException(status_code=401, detail="Failed to redeem code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
