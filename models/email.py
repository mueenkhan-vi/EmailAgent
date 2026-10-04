from datetime import datetime
from pydantic import BaseModel, Field

class Email(BaseModel):
    id: str
    provider: str

    thread_id: str | None = None

    sender: str
    recipients: list[str] = Field(default_factory=list)

    cc: list[str] = Field(default_factory=list)

    subject: str = ""

    body: str = ""

    received_at: datetime

    is_read: bool = True

    is_starred: bool = False

    is_important: bool = False

    labels: list[str] = Field(default_factory=list)

    has_attachments: bool = False

    attachments: list[str] = Field(default_factory=list)