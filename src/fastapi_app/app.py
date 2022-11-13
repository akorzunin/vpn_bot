import asyncio
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

# from src.metadata import tags_metadata
from src.logger import format as log_format
from src.fastapi_app import shemas
from src.tasks import test_task

app = FastAPI(
    # openapi_tags=tags_metadata,
)


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

    test_task.count_words.send("http://google.com")
    message = 'Task created... i guess'
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=shemas.Message(message=message).dict(),
    )
