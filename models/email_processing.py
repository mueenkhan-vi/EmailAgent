from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ProcessingMode(str, Enum):
    COUNT = "count"
    PERIOD = "period"
    DATE_RANGE = "date_range"
    UNREAD = "unread"
    SINCE_LAST_SYNC = "since_last_sync"
    ALL = "all"


class EmailProcessingRequest(BaseModel):
    mode: ProcessingMode

    max_count: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Maximum number of emails to process. "
            "Acts as a safety limit regardless of the processing mode."
        ),
    )

    period_days: int | None = Field(
        default=None,
        gt=0,
        description="Number of previous days to process.",
    )

    start_date: datetime | None = Field(
        default=None,
        description="Start of the email date range.",
    )

    end_date: datetime | None = Field(
        default=None,
        description="End of the email date range.",
    )

    include_read: bool = Field(
        default=True,
        description="Whether read emails should be included.",
    )

    include_unread: bool = Field(
        default=True,
        description="Whether unread emails should be included.",
    )

    @model_validator(mode="after")
    def validate_request(self):

        if self.mode == ProcessingMode.COUNT:
            if self.max_count is None:
                raise ValueError(
                    "max_count is required when mode is 'count'"
                )

        elif self.mode == ProcessingMode.PERIOD:
            if self.period_days is None:
                raise ValueError(
                    "period_days is required when mode is 'period'"
                )

        elif self.mode == ProcessingMode.DATE_RANGE:
            if self.start_date is None or self.end_date is None:
                raise ValueError(
                    "start_date and end_date are required "
                    "when mode is 'date_range'"
                )

            if self.start_date > self.end_date:
                raise ValueError(
                    "start_date cannot be later than end_date"
                )

        elif self.mode in {
            ProcessingMode.UNREAD,
            ProcessingMode.SINCE_LAST_SYNC,
            ProcessingMode.ALL,
        }:

            if self.period_days is not None:
                raise ValueError(
                    f"period_days is not valid when "
                    f"mode is '{self.mode.value}'"
                )

            if self.start_date is not None:
                raise ValueError(
                    f"start_date is not valid when "
                    f"mode is '{self.mode.value}'"
                )

            if self.end_date is not None:
                raise ValueError(
                    f"end_date is not valid when "
                    f"mode is '{self.mode.value}'"
                )

        if not self.include_read and not self.include_unread:
            raise ValueError(
                "At least one of include_read or include_unread "
                "must be True"
            )

        return self