""""""

from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from src.db.schemas import Money, VpnPayment, VpnPaymentId

router = APIRouter()


@router.post("/create_user_invoice")
async def create_user_invoice(
    amount: Money,
    user_id: int,
    payment_method: Literal["crypto", "FPS"],
):
    """Create payment"""
    return VpnPayment(
        id=VpnPaymentId(uuid4()),
        amount=amount,
        user_id=user_id,
        payment_method=payment_method,
        is_confirmed=False,
    )
