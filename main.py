import asyncio
from datetime import datetime
import os
import uvicorn

from src.aiogram_app import app as aiogram_app
from src.fastapi_app.app import app
from src.fastapi_app.uvicrorn_confgis import uvicorn_conf
from src.tasks.scheduler import scheduler

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # create fastapi task
    config = uvicorn.Config(**uvicorn_conf, loop=loop)
    server = uvicorn.Server(config)
    loop.create_task(server.serve())
    # start scheduler
    scheduler.start()

    # tasks

    # setup debug console to work w/ awaitables
    if bool(eval(os.getenv('DEBUG'))):
        # import nest_asyncio
        # nest_asyncio.apply(loop) 
        # loop.set_debug(1)
        ...

    # message_handler.setup(aiogram_app.dp)
    aiogram_app.executor.start_polling(aiogram_app.dp, skip_updates=True)
    if 1:
        loop.run_forever()