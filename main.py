from models.email_processing import EmailProcessingRequest
from providers.gmail import GmailProvider

def main():

    gmail = GmailProvider()

    request = EmailProcessingRequest(
        mode="count",
        max_count=600,
    )

    emails = gmail.fetch_emails(
        request
    )

    print(
        f"\nFetched {len(emails)} emails\n"
    )

    for index, email in enumerate(
        emails,
        start=1,
    ):

        print("=" * 70)
        print(f"Email #{index}")
        print("From:", email.sender)
        print("Subject:", email.subject)
        print("Received:", email.received_at)
        print("Read:", email.is_read)
        print("Important:", email.is_important)


if __name__ == "__main__":
    main()