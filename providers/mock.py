from datetime import datetime, timezone

from models.email import Email
from models.email_processing import EmailProcessingRequest
from providers.base import EmailProvider

class MockEmailProvider(EmailProvider):

    def authenticate(self) -> None:
        print("Mock authentication successful.")

    def fetch_emails(
        self,
        request: EmailProcessingRequest,
    ) -> list[Email]:

        emails = [
            Email(
                id="1",
                provider="mock",
                thread_id="thread-1",
                sender="customer@example.com",
                recipients=["owner@example.com"],
                subject="Request for quotation",
                body=(
                    "Please send us your quotation "
                    "for the requested items."
                ),
                received_at=datetime.now(timezone.utc),
            ),
            Email(
                id="2",
                provider="mock",
                thread_id="thread-2",
                sender="marketing@example.com",
                recipients=["owner@example.com"],
                subject="50% discount available!",
                body=(
                    "Get 50% off our products "
                    "for a limited time."
                ),
                received_at=datetime.now(timezone.utc),
            ),
        ]

        if request.max_count is not None:
            return emails[:request.max_count]

        return emails

    def get_email(
        self,
        email_id: str,
    ) -> Email:

        emails = self.fetch_emails(
            EmailProcessingRequest(
                mode="all",
                max_count=None,
            )
        )

        for email in emails:
            if email.id == email_id:
                return email

        raise ValueError(
            f"Email not found: {email_id}"
        )

    def mark_important(
        self,
        email_id: str,
    ) -> None:

        print(
            f"Mock: marking email {email_id} as important."
        )

    def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        thread_id: str | None = None,
    ) -> None:

        print(
            f"Mock: sending email to {to}"
        )
        print(
            f"Subject: {subject}"
        )

    def delete_email(
        self,
        email_id: str,
    ) -> None:

        print(
            f"Mock: moving email {email_id} to trash."
        )