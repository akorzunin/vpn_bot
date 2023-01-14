import logging
import os


format = "%(asctime)s [%(levelname)s] <%(name)s> %(message)s"
log_level = (
    logging.DEBUG if bool(eval(os.getenv("DEBUG", "False"))) else logging.INFO
)
logging.basicConfig(
    format=format,
    encoding="utf-8",
    level=log_level,
)
logger = logging.getLogger(__name__)
