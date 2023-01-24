from datetime import timedelta
import os

from src.db.schemas import Money

BILL_PERIOD = timedelta(
    seconds=int(os.getenv("BILL_PERIOD", 30 * 24 * 60 * 60))
)  # 1 month by default
MAX_CONFIGS = int(os.getenv("MAX_CONFIGS", 3))
PAYMENT_AMOUNT = Money(os.getenv("PAYMENT_AMOUNT", 100.0))
