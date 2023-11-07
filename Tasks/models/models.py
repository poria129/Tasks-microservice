from datetime import datetime
from pydantic import BaseModel


from Tasks.validators.validators import StatusChoices, PriorityChoices


class Tasks(BaseModel):
    subject: str
    status: StatusChoices
    project: str
    is_group: bool
    priority: PriorityChoices
    detail: str
    participators: list[str]
    updated_at: datetime
    created_at: datetime

    def update_timestamp(self):
        self.updated_at = datetime.now()

    def create_timestamp(self):
        self.updated_at = datetime.now()
        self.created_at = datetime.now()
