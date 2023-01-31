import asyncio

import src

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

if src.DEBUG:
    loop.set_debug(True)
