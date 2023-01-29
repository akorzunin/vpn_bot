"""fastapi router for user routes"""
from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.db import crud
from src.db import promocode_functions
from src.db.schemas import User, UserUpdate, VpnConfig
from src.fastapi_app import pivpn_wrapper as pivpn

router = APIRouter()


@router.get("/get_user/{user_id}")
async def get_user_by_id(user_id: int):
    user = await crud.find_user_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/create_user")
async def create_user(user: User):
    """create user"""
    if await crud.find_user_by_telegram_id(user.telegram_id):
        # return 400
        return JSONResponse(status_code=400, content="User already exists")
    await crud.create_user(user)
    return JSONResponse(status_code=201, content={"message": "User created"})


# update user
@router.put("/update_user/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    """update user"""
    if await crud.find_user_by_telegram_id(user_id):
        await crud.update_user(user_id, user)
        return JSONResponse(
            status_code=200, content={"message": "User updated"}
        )
    return JSONResponse(status_code=400, content="User not found")


@router.get("/users")
async def get_all_users():
    """get all users"""
    return await crud.get_all_users()


# delete user
@router.delete("/delete_user/{user_id}")
async def delete_user(telegram_id: int):
    """delete user"""
    user = await crud.get_user_by_telegram_id(telegram_id)
    if not user:
        return JSONResponse(status_code=400, content="User not found")
    await crud.delete_user(user)
    return JSONResponse(status_code=200, content={"message": "User deleted"})


@router.post("/add_vpn_config/{user_id}")
async def add_vpn_config(user_id: int, vpn_config: VpnConfig):
    """add vpn config"""
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
async def remove_vpn_config(user_id: int, vpn_user: str):
    """remove vpn config"""
    if await crud.get_user_by_telegram_id(user_id):
        crud.remove_vpn_config(user_id, vpn_user)
        return JSONResponse(
            status_code=200, content={"message": "Vpn config removed"}
        )
    return JSONResponse(status_code=400, content="User not found")


@router.get("/get_vpn_config/{file_path}")
async def get_vpn_config(file_path: str):
    """get vpn config from PIVPN"""
    try:
        return pivpn.get_config_by_filepath(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/redeem_code")
async def redeem_code(
    user_id: int,
    code_alias: str = "",
    code_id: UUID | None = None,
):
    """redeem code"""
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
