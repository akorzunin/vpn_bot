"""
Demonstrates how to use the asyncio compatible scheduler to schedule a job that executes on 3
second intervals.
"""

from datetime import datetime
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import asyncio


def tick():
    print(f"Tick! The time is: {datetime.now()}")


import contextlib

scheduler = AsyncIOScheduler()

if __name__ == "__main__":
    # scheduler.add_job(tick, 'interval', seconds=3)
    scheduler.start()
    # scheduler.add_job(tick, 'interval', seconds=3)
    print("Press Ctrl+{0} to exit".format("Break" if os.name == "nt" else "C"))

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.get_event_loop().run_forever()
