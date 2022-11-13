import os
import uvicorn

from src.logger import format as log_format

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = log_format
uvicorn_conf = dict(
    app="main:app",
    host=os.getenv("HOST", '0.0.0.0'),
    port=int(os.getenv("PORT") or 7999),
    log_level="info",
    log_config=log_config,
    reload=bool(eval(os.getenv("DEBUG", "False"))),
)