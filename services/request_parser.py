from llm.factory import get_llm
from models.email_processing import EmailProcessingRequest


def parse_processing_request(
    user_request: str,
) -> EmailProcessingRequest:

    llm = get_llm()

    structured_llm = llm.with_structured_output(
        EmailProcessingRequest
    )

    result = structured_llm.invoke(
        f"""
        Convert the user's email-processing request into
        a structured EmailProcessingRequest.

        Supported processing modes:

        1. count
           Use when the user specifies the number of latest emails.

        2. period
           Use when the user specifies a relative period such as:
           last 7 days, last 30 days, last 3 months.

        3. date_range
           Use when the user specifies explicit start and end dates.

        4. unread
           Use when the user wants unread emails.

        5. since_last_sync
           Use when the user wants emails received since
           the previous synchronization.

        6. all
           Use when the user explicitly asks to process
           all available emails.

        Important rules:

        - max_count is an optional safety limit.
        - If the user specifies a number of emails,
          use max_count.
        - If the user specifies both a period and a maximum
          count, use both.
        - Do not invent dates or counts.
        - Do not invent missing information.
        - If information required by a mode is missing,
          do not guess.

        User request:
        {user_request}
        """
    )

    return result