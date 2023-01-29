import logging
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.fastapi_app import shemas
from src.fastapi_app.pivpn_wrapper import check_pivpn_connection

# from src.metadata import tags_metadata
from src.logger import format as log_format
from src.tasks.scheduler import scheduler
from src.fastapi_app.user_routes import router as user_router
from src.fastapi_app.admin_routes import router as admin_router
from src.tasks.user_tasks import recreate_user_billing_tasks

app = FastAPI(
    # openapi_tags=tags_metadata,
)

# include router for users
app.include_router(user_router, prefix="/user", tags=["user"])

# include router for admin
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    # recreate all user billing tasks
    await recreate_user_billing_tasks()
    # add logs to stdout
    logger.removeHandler(logger.handlers[0])
    logger.addHandler(handler)
    logging.info(f"pivpn api connected: {check_pivpn_connection()}")
