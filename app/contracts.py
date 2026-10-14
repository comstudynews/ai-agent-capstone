"""Shared contracts: API boundary does not leak internal exceptions."""
from typing import Literal
from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    id: str
    title: str
    excerpt: str
    score: float = Field(ge=0, le=1)
    source: str


class Ticket(BaseModel):
    ticket_id: str
    title: str
    description: str
    status: Literal["open", "closed"] = "open"
    created: bool


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = Field(default=None, max_length=120)


class ChatOut(BaseModel):
    thread_id: str
    answer: str
    events: list[dict] = Field(default_factory=list)


class CreateTicketIn(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    request_id: str = Field(min_length=8, max_length=120)


class ErrorPayload(BaseModel):
    code: str
    message: str
    retryable: bool = False
