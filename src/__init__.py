# load .env variables
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(eval(os.getenv("DEBUG", "False")))
PROTECT_DOCS = bool(eval(os.getenv("PROTECT_DOCS", "False")))
PIVPN_HOST = os.getenv("PIVPN_HOST", "localhost:7070")

from src.tasks.task_configs import (
    MAX_CONFIGS,
    BILL_PERIOD,
    NO_REVIVE_PERIOD,
    ALLOWED_DOWNTIME_DELAY,
    PAYMENT_AMOUNT,
)
