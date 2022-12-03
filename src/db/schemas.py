from datetime import datetime

from pydantic import BaseModel


# Money = NewType('Money', float)
class Money(float):
    ...


class VpnPaymentId(int):
    ...


class VpnConfig(BaseModel):
    path: str
    user_name: str
    private_key: str
    ip: str
    shared_key: str


class VpnPayment(BaseModel):
    # id: VpnPaymentId
    user_id: int
    amount: Money
    date: datetime
    is_confirmed: bool


class User(BaseModel):
    id: int
    last_payment: datetime
    created_at: datetime
    telegram_id: int
    conf_files: VpnConfig
    is_enbled: bool
    strick_time: int
    next_payment: datetime
    all_payments: list[VpnPaymentId]
    balance: Money
