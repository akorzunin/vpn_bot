# load .env variables
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = bool(eval(os.getenv("DEBUG", "False")))
PROTECT_DOCS = bool(eval(os.getenv("PROTECT_DOCS", "False")))
