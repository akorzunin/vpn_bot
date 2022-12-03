import logging
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.fastapi_app import shemas

# from src.metadata import tags_metadata
from src.logger import format as log_format
from src.tasks.scheduler import scheduler
from src.fastapi_app.user_routes import router as user_router

app = FastAPI(
    # openapi_tags=tags_metadata,
)

# include router for users
app.include_router(user_router, prefix="/user", tags=["user"])


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    # add logs to stdout
    logger.removeHandler(logger.handlers[0])
    logger.addHandler(handler)


@app.get(
    "/test",
    response_model=shemas.Message,
    status_code=status.HTTP_202_ACCEPTED,
)
async def test_endpoint(
    message: str,
):
    def tick():
        print(f"Tick! The time is: {datetime.now()}")
        raise NotImplementedError

    scheduler.add_job(tick, "interval", seconds=3, name="pepe")
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=shemas.Message(message=message).dict(),
    )


@app.post(
    "/create_task",
    response_model=shemas.Message,
    status_code=status.HTTP_201_CREATED,
)
async def test_endpoint(
    task: shemas.Task,
):

    # test_task.count_words.send("http://google.com")
    message = "Task created... i guess"
    # scheduler.remove_job()
    a = scheduler.get_jobs()
    scheduler.remove_job(next(i.id for i in a if i.name == "pepe"))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=shemas.Message(message=message).dict(),
    )
