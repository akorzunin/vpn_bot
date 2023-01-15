from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Money = NewType('Money', float)
class Money(float):
    ...


class VpnPaymentId(str):
    ...


class PromocodeId(str):
    ...


class VpnConfig(BaseModel):
    path: str
    user_name: str


class VpnPayment(BaseModel):
    id: VpnPaymentId
    user_id: int
    amount: Money
    date: datetime = datetime.now()
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


class PromoCode(BaseModel):
    id: PromocodeId
    function: str
    alias: str = ""
    user_id: int | None = None
    value: str = ""
    is_redemed: bool = False
    created_at: datetime = datetime.now()
    redemed_at: Optional[datetime] = None
    # TODO: add validator for acvivate_user: value(user_name) can't be empty
