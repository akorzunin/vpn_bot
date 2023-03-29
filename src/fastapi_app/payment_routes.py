""""""

from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from src.db.schemas import Money, UserPayment, VpnPayment, VpnPaymentId

router = APIRouter()


@router.post("/create_user_invoice")
async def create_user_invoice(user_payment: UserPayment):
    """Create payment"""
    ...
