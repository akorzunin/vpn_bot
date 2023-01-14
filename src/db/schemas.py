from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Money = NewType('Money', float)
class Money(float):
    ...


class VpnPaymentId(int):
    ...


class VpnConfig(BaseModel):
    path: str
    user_name: str


class VpnPayment(BaseModel):
    # id: VpnPaymentId
    user_id: int
    amount: Money
    date: datetime
    is_confirmed: bool


class User(BaseModel):
    last_payment: Optional[datetime] = None
    user_name: Optional[str] = None
    created_at: datetime = datetime.now()
    telegram_id: int
    conf_files: Optional[list[VpnConfig]] = None
    is_enabled: bool = True
    strick_time: int = 1
    next_payment: Optional[datetime] = None
    all_payments: list[VpnPaymentId] = []
    balance: Money = Money(0)


class UserUpdate(BaseModel):
    conf_files: Optional[list[VpnConfig]] = None
    is_enabled: Optional[bool] = None
    strick_time: Optional[int] = None
    next_payment: Optional[datetime] = None
    all_payments: Optional[list[VpnPaymentId]] = None
    balance: Optional[Money] = None
