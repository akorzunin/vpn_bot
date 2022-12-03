from src.db.schemas import User


def prepare_user_str(user: User) -> str:
    """format user in human readable format"""
    user_str = "User data:"
    for k, v in user:
        user_str += f"\n  {k}: {v}"
    return user_str
