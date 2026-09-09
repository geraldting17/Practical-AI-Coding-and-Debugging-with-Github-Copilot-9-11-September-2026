from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TicketStatus(StrEnum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=2000)
    requester: str = Field(min_length=2, max_length=80)
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, min_length=3, max_length=2000)
    requester: str | None = Field(default=None, min_length=2, max_length=80)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None

    @model_validator(mode="after")
    def reject_null_updates(self) -> "TicketUpdate":
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Updated fields cannot be null")
        return self


class Ticket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    requester: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime


class TicketFilters(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    search: str | None = None
