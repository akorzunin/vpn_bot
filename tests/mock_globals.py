# mock global variables for testing
from datetime import timedelta

from src.db.schemas import Money

DEBUG = False
PROTECT_DOCS = False
PIVPN_HOST = "test-vpn-crm-bot.duckdns.org:10002"
BILL_PERIOD = timedelta(seconds=10)
NO_REVIVE_PERIOD = timedelta(seconds=10)
ALLOWED_DOWNTIME_DELAY = timedelta(seconds=10)
PAYMENT_AMOUNT = Money(10)
