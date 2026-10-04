from enum import Enum
from pydantic import BaseModel, Field

class EmailCategory(str, Enum):
    BUSINESS = "business"
    ADVERTISEMENT = "advertisement"
    SPAM = "spam"
    PERSONAL = "personal"
    NEWSLETTER = "newsletter"
    FINANCE = "finance"
    TRANSACTIONAL = "transactional"
    AUTOMATED = "automated"
    IRRELEVANT = "irrelevant"


class EmailPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class EmailAnalysis(BaseModel):
    category: EmailCategory = Field(
        description="The primary category of the email."
    )

    priority: EmailPriority = Field(
        description="The priority of the email."
    )

    requires_reply: bool = Field(
        description="Whether the sender expects a reply."
    )

    requires_action: bool = Field(
        description="Whether the email requires an action from the owner."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )

    summary: str = Field(
        description="A concise summary of the email."
    )

    suggested_action: str | None = Field(
        default=None,
        description="Suggested action for the email owner."
    )