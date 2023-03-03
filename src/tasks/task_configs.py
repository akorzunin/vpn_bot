"""Don't import env variables directly, use src module instead"""
from datetime import timedelta
import os

from src.db.schemas import Money

BILL_PERIOD = timedelta(
    seconds=int(os.getenv("BILL_PERIOD", 30 * 24 * 60 * 60))
)  # 1 month by default
NO_REVIVE_PERIOD = timedelta(
    seconds=int(os.getenv("NO_REVIVE_PERIOD", 2 * 30 * 24 * 60 * 60))
)  # 2 months by default
# time to pick up missed job after downtime when next payment is missed
ALLOWED_DOWNTIME_DELAY = timedelta(
    seconds=int(os.getenv("ALLOWED_DOWNTIME_DELAY", 30 * 24 * 60 * 60))
)  # 1 month by default
MAX_CONFIGS = int(os.getenv("MAX_CONFIGS", 3))
PAYMENT_AMOUNT = Money(os.getenv("PAYMENT_AMOUNT", 100.0))
