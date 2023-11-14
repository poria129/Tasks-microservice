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

    class config:
        allow_population_by_field_name = True


class UpdateTasks(BaseModel):
    subject: str
    status: StatusChoices
    project: str
    is_group: bool
    priority: PriorityChoices
    detail: str
    updated_at: datetime

    def update_timestamp(self):
        self.updated_at = datetime.now()


class CreateTasks(Tasks):
    def create_timestamp(self):
        self.updated_at = str(datetime.now())
        self.created_at = str(datetime.now())


class JoinTask(BaseModel):
    participators: list[str] | None = None
    updated_at: datetime | None = None

    def update_timestamp(self):
        self.updated_at = datetime.now()
