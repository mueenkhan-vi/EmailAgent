from abc import ABC, abstractmethod

from models.email import Email
from models.email_processing import EmailProcessingRequest

class EmailProvider(ABC):

    @abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate with the email provider.
        """
        pass

    @abstractmethod
    def fetch_emails(
        self,
        request: EmailProcessingRequest,
    ) -> list[Email]:
        """
        Fetch emails according to the processing request.
        """
        pass

    @abstractmethod
    def get_email(
        self,
        email_id: str,
    ) -> Email:
        """
        Retrieve a single email.
        """
        pass

    @abstractmethod
    def mark_important(
        self,
        email_id: str,
    ) -> None:
        """
        Mark an email as important.
        """
        pass

    @abstractmethod
    def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        thread_id: str | None = None,
    ) -> None:
        """
        Send an email.
        """
        pass

    @abstractmethod
    def delete_email(
        self,
        email_id: str,
    ) -> None:
        """
        Delete or move an email to trash.
        """
        pass