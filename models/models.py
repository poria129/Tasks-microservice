from pydantic import BaseModel
import datetime


class Tasks(BaseModel):
    subject: str
    status: list[str]
    project: list[str]
    is_group: bool
    priority: list[str]
    detail: str
    participators: list[str]
    created_date: datetime
    updated_date: datetime
