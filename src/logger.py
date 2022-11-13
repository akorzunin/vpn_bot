import logging
import os


format = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    format=format,
    encoding="utf-8",
    level=logging.DEBUG if bool(eval(os.getenv("DEBUG"))) else logging.INFO,
)
logger = logging.getLogger(__name__)
