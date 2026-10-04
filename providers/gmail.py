import base64
import os
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from models.email import Email
from models.email_processing import (
    EmailProcessingRequest,
    ProcessingMode,
)


class GmailProvider:

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file

        self.credentials = None
        self.service = None

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------

    def authenticate(self) -> Credentials:

        if os.path.exists(self.token_file):
            self.credentials = (
                Credentials.from_authorized_user_file(
                    self.token_file,
                    self.SCOPES,
                )
            )

        if (
            not self.credentials
            or not self.credentials.valid
        ):

            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(
                    Request()
                )

            else:
                flow = (
                    InstalledAppFlow
                    .from_client_secrets_file(
                        self.credentials_file,
                        self.SCOPES,
                    )
                )

                self.credentials = (
                    flow.run_local_server(
                        port=0
                    )
                )

            with open(
                self.token_file,
                "w",
                encoding="utf-8",
            ) as token:

                token.write(
                    self.credentials.to_json()
                )

        self.service = build(
            "gmail",
            "v1",
            credentials=self.credentials,
        )

        return self.credentials

    # ---------------------------------------------------------
    # FETCH EMAILS
    # ---------------------------------------------------------

    def fetch_emails(
        self,
        request: EmailProcessingRequest,
    ) -> list[Email]:

        if self.service is None:
            self.authenticate()

        query = self._build_gmail_query(request)

        max_count = request.max_count

        # If no explicit limit is supplied, use a sensible
        # default for now. We will make this configurable later.
        if max_count is None:
            max_count = 100

        messages = self._list_message_ids(
            query=query,
            max_count=max_count,
        )

        emails = []

        for message in messages:

            email = self.get_email(
                message["id"]
            )

            emails.append(email)

        return emails

    # ---------------------------------------------------------
    # PAGINATED MESSAGE LIST
    # ---------------------------------------------------------

    def _list_message_ids(
        self,
        query: str | None,
        max_count: int,
    ) -> list[dict]:

        messages = []

        page_token = None

        while len(messages) < max_count:

            remaining = max_count - len(messages)

            # Gmail allows maximum 500 per request.
            page_size = min(
                remaining,
                500,
            )

            request_kwargs = {
                "userId": "me",
                "maxResults": page_size,
            }

            if query:
                request_kwargs["q"] = query

            if page_token:
                request_kwargs["pageToken"] = page_token

            response = (
                self.service
                .users()
                .messages()
                .list(
                    **request_kwargs
                )
                .execute()
            )

            page_messages = response.get(
                "messages",
                []
            )

            if not page_messages:
                break

            messages.extend(
                page_messages
            )

            page_token = response.get(
                "nextPageToken"
            )

            if not page_token:
                break

        return messages[:max_count]

    # ---------------------------------------------------------
    # BUILD GMAIL QUERY
    # ---------------------------------------------------------

    def _build_gmail_query(
        self,
        request: EmailProcessingRequest,
    ) -> str | None:

        mode = request.mode

        # ---------------------------------------------
        # COUNT
        # ---------------------------------------------

        if mode == ProcessingMode.COUNT:

            return None

        # ---------------------------------------------
        # PERIOD
        # ---------------------------------------------

        if mode == ProcessingMode.PERIOD:

            start_date = (
                datetime.now(timezone.utc)
                - timedelta(
                    days=request.period_days
                )
            )

            return (
                f"after:{start_date.strftime('%Y/%m/%d')}"
            )

        # ---------------------------------------------
        # DATE RANGE
        # ---------------------------------------------

        if mode == ProcessingMode.DATE_RANGE:

            start_date = request.start_date
            end_date = request.end_date

            # Gmail's before: operator is exclusive.
            # Add one day so the requested end date is included.
            end_date_exclusive = (
                end_date + timedelta(days=1)
            )

            return (
                f"after:{start_date.strftime('%Y/%m/%d')} "
                f"before:{end_date_exclusive.strftime('%Y/%m/%d')}"
            )

        # ---------------------------------------------
        # UNREAD
        # ---------------------------------------------

        if mode == ProcessingMode.UNREAD:

            return "is:unread"

        # ---------------------------------------------
        # SINCE LAST SYNC
        # ---------------------------------------------

        if mode == ProcessingMode.SINCE_LAST_SYNC:

            raise NotImplementedError(
                "SINCE_LAST_SYNC will be implemented "
                "after the synchronization database is added."
            )

        # ---------------------------------------------
        # ALL
        # ---------------------------------------------

        if mode == ProcessingMode.ALL:

            # in:anywhere includes mail that would otherwise
            # be excluded from normal mailbox search.
            return "in:anywhere"

        raise ValueError(
            f"Unsupported processing mode: {mode}"
        )

    # ---------------------------------------------------------
    # GET SINGLE EMAIL
    # ---------------------------------------------------------

    def get_email(
        self,
        email_id: str,
    ) -> Email:

        if self.service is None:
            self.authenticate()

        message = (
            self.service
            .users()
            .messages()
            .get(
                userId="me",
                id=email_id,
                format="full",
            )
            .execute()
        )

        return self._convert_message(
            message
        )

    # ---------------------------------------------------------
    # CONVERT GMAIL MESSAGE → EMAIL
    # ---------------------------------------------------------

    def _convert_message(
        self,
        message: dict,
    ) -> Email:

        headers = {
            header["name"].lower(): header["value"]
            for header in (
                message
                .get("payload", {})
                .get("headers", [])
            )
        }

        sender = headers.get(
            "from",
            "",
        )

        recipients = self._split_addresses(
            headers.get("to", "")
        )

        cc = self._split_addresses(
            headers.get("cc", "")
        )

        subject = headers.get(
            "subject",
            "",
        )

        body = self._extract_body(
            message.get("payload", {})
        )

        received_at = self._convert_timestamp(
            message.get("internalDate")
        )

        label_ids = message.get(
            "labelIds",
            [],
        )

        attachments = (
            self._extract_attachments(
                message.get("payload", {})
            )
        )

        return Email(
            id=message["id"],
            provider="gmail",
            thread_id=message.get(
                "threadId"
            ),
            sender=sender,
            recipients=recipients,
            cc=cc,
            subject=subject,
            body=body,
            received_at=received_at,
            is_read="UNREAD" not in label_ids,
            is_starred="STARRED" in label_ids,
            is_important="IMPORTANT" in label_ids,
            labels=label_ids,
            has_attachments=(
                len(attachments) > 0
            ),
            attachments=attachments,
        )

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _split_addresses(
        addresses: str,
    ) -> list[str]:

        if not addresses:
            return []

        return [
            address.strip()
            for address in addresses.split(",")
            if address.strip()
        ]

    @staticmethod
    def _convert_timestamp(
        timestamp: str | None,
    ) -> datetime:

        if not timestamp:
            return datetime.now(
                timezone.utc
            )

        return datetime.fromtimestamp(
            int(timestamp) / 1000,
            tz=timezone.utc,
        )

    def _extract_body(
        self,
        payload: dict,
    ) -> str:

        body_data = (
            payload
            .get("body", {})
            .get("data")
        )

        if body_data:

            decoded = (
                base64.urlsafe_b64decode(
                    body_data
                )
            )

            return decoded.decode(
                "utf-8",
                errors="replace",
            )

        for part in payload.get(
            "parts",
            [],
        ):

            if part.get(
                "mimeType"
            ) == "text/plain":

                data = (
                    part
                    .get("body", {})
                    .get("data")
                )

                if data:

                    decoded = (
                        base64.urlsafe_b64decode(
                            data
                        )
                    )

                    return decoded.decode(
                        "utf-8",
                        errors="replace",
                    )

            nested_result = (
                self._extract_body(part)
            )

            if nested_result:
                return nested_result

        return ""

    def _extract_attachments(
        self,
        payload: dict,
    ) -> list[str]:

        attachments = []

        filename = payload.get(
            "filename"
        )

        if filename:
            attachments.append(
                filename
            )

        for part in payload.get(
            "parts",
            [],
        ):

            attachments.extend(
                self._extract_attachments(
                    part
                )
            )

        return attachments