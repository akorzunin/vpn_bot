""""""

from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.db.schemas import Money, UserPayment, VpnPayment, VpnPaymentId
from src.db import crud

router = APIRouter()


@router.post("/create_user_invoice")
async def create_user_invoice(
    user_id: int,
    payment_method: Literal["crypto", "FPS"],
    pay_amount: Money,
    pay_comment: str | None = None,
):
    """Create payment"""
    user_payment = UserPayment(
        id=VpnPaymentId(uuid4()),
        user_id=user_id,
        amount=pay_amount,
        payment_method=payment_method,
        pay_comment=pay_comment,
    )
    try:
        payment_id = await crud.create_user_payment(user_payment)
        return JSONResponse(
            status_code=200,
            content=user_payment.json(),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
