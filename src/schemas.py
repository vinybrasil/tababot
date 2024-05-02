import uuid
from typing import Any

from pydantic import BaseModel


class Element(BaseModel):
    type: str
    payload: Any


class Request(BaseModel):
    request_id: str = str(uuid.uuid4())
    question: str
    answer: str = None
    error: str = None
