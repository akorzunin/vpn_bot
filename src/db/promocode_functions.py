from datetime import datetime
from uuid import UUID
from tinydb import Query

from src.db.db_conn import users, payments, promocodes
from src.db.schemas import Money, PromoCode, PromocodeId


def use_check_promocode(
    user_id: int,
    promocode_alias: str,
    promocode_id: UUID | None = None,
) -> PromocodeId | None:
    """Check promocode by alias or id if alias given then return first promocode id with this alias"""
    promocode = None
    q = Query()
    if promocode_id:
        # check promocode by id
        promocode = promocodes.get(q.id == promocode_id)  # type: ignore
    if promocode_id is None:
        # get one not redeemed promocode by alias
        promocode = promocodes.get(q.alias == promocode_alias and q.is_redemed == False)  # type: ignore

    if not promocode:
        raise ValueError("Promocode not found")
    return use_promocode(PromoCode(**promocode), user_id)


def use_promocode(promocode: PromoCode, user_id: int) -> PromocodeId:
    if promocode.is_redemed:
        raise ValueError("Promocode already redemed")
    if promocode.function == "add_balance":
        return add_balance(user_id, Money(promocode.value), promocode.id)
    if promocode.function == "activate_user":
        # return activate_user(user_id, promocode.value, promocode.id)
        ...
    # TODO move all promocode function to one file and check them w/ inspect module
    raise ValueError("Promocode function not found")


def add_balance(
    user_id: int, amount: Money, promo_code_id: PromocodeId
) -> PromocodeId:
    User = Query()
    if user := users.get(User.telegram_id == user_id):  # type: ignore
        # add balance to user
        users.update(
            {"balance": user["balance"] + amount},
            User.telegram_id == user_id,  # type: ignore
        )
        # set promocode as reedemed
        promocodes.update(
            {
                "is_redemed": True,
                "user_id": user_id,
                "redeemed_at": datetime.now(),
            },
            Query().id == promo_code_id,  # type: ignore
        )
        return promo_code_id
    else:
        raise ValueError("User not found")


def activate_user(user_id: int, user_name: str, promo_code_id: PromocodeId):
    ...


def create_promocode(promocode: PromoCode) -> int:
    return promocodes.insert(promocode.dict())
