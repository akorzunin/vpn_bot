'''fastapi router for user routes'''
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.db import crud
from src.db.schemas import User

router = APIRouter()


@router.get("/get_user/{user_id}")
async def get_user_by_id(user_id: int):
    user = await crud.get_user_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/create_user")
async def create_user(user: User):
    '''create user'''
    if await crud.get_user_by_telegram_id(user.telegram_id):
        # return 400
        return JSONResponse(status_code=400, content="User already exists")
    await crud.create_user(user)
    return JSONResponse(status_code=201, content={"message": "User created"})

@router.get("/users")
async def get_all_users():
    '''get all users'''
    return await crud.get_all_users()

# delete user
@router.delete("/delete_user/{user_id}")
async def delete_user(telegram_id: int):
    '''delete user'''
    user = await crud.get_user_by_telegram_id(telegram_id)
    if not user:
        return JSONResponse(status_code=400, content="User not found")
    await crud.delete_user(user)
    return JSONResponse(status_code=200, content={"message": "User deleted"})
