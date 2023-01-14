import asyncio
import uvicorn

from src.aiogram_app import aiogram_app
from src.fastapi_app.fastapi_app import app
from src.fastapi_app.uvicrorn_configs import uvicorn_conf
from src.tasks.scheduler import scheduler

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # create fastapi task
    server = uvicorn.Server(uvicorn_conf)
    loop.create_task(server.serve())
    # start scheduler
    scheduler.start()
    # message_handler.setup(aiogram_app.dp)
    aiogram_app.executor.start_polling(
        aiogram_app.dp,
        skip_updates=True,
    )
