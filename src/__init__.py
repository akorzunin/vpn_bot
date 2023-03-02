# load .env variables
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(eval(os.getenv("DEBUG", "False")))
PROTECT_DOCS = bool(eval(os.getenv("PROTECT_DOCS", "False")))
PIVPN_HOST = os.getenv("PIVPN_HOST", "localhost:7070")
PIVPN_TOKEN = os.getenv("PIVPN_TOKEN", "")
WG_HOST = os.getenv("WG_HOST", "localhost:7998")
WG_PASSWORD = os.getenv("WG_PASSWORD", "password")

from src.tasks.task_configs import (
    ALLOWED_DOWNTIME_DELAY,
    BILL_PERIOD,
    MAX_CONFIGS,
    NO_REVIVE_PERIOD,
    PAYMENT_AMOUNT,
)
