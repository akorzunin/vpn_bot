from typing import Callable, Literal
from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    message: str

class Task(BaseModel):
    start_time: datetime
    # type: Literal['dunno yet']
    # func: Callable