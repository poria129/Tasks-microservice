from enum import Enum


class StatusChoices(str, Enum):
    backlog = "backlog"
    cancelled = "cancelled"
    compeleted = "compeleted"
    open = "open"
    overdue = "overdue"
    pending_review = "pending_review"
    template = "template"
    working = "working"


class PriorityChoices(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
