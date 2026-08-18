from pathlib import Path
from typing import Union
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

class GmailService:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    BASE_DIR = BASE_DIR = Path(__file__).resolve().parents[3] # Adjust the path to point to the root of your project
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
    TOKEN_FILE = CREDENTIALS_DIR / "token.json"


    def __init__(self) -> None:
        # Load credentials from the tokens.json file if it exists, if it doesn't exist create one on initialization
        self.credentials = self._get_credentials()
        self.service = build(
            "gmail",
            "v1",
            credentials=self.credentials
        )


    # Private get credentials method
    def _get_credentials(self) -> Union[Credentials, ExternalAccountCredentials]:
        """Get valid credentials for Gmail API."""
        credentials = None
        # 1. Try existing token if it exists
        if self.TOKEN_FILE.exists():
            credentials = Credentials.from_authorized_user_file(
                self.TOKEN_FILE,
                self.SCOPES
            )

        # 2. Refresh expired credentials
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        # 3. First time Oauth
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.CLIENT_SECRET_FILE,
                self.SCOPES
            )

            credentials = flow.run_local_server(
                port=0
            )

        # 4. Persist credentials for future startups
        self.TOKEN_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.TOKEN_FILE.write_text(
            credentials.to_json()
        )

        return credentials

    async def search_messages(
        self,
        query: str = "",
        max_results: int = 5      
    ):
        try:
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                return (
                    f"No messages found matching "
                    f"the search query: '{query}'"
                )

            output = []

            for message in messages:
                detail = (
                    self.service
                    .users()
                    .messages()
                    .get(
                        userId="me",
                        id=message["id"]
                    )
                    .execute()
                )

                headers = detail.get(
                    "payload",
                    {}
                ).get(
                    "headers",
                    []
                )

                subject = next(
                    (
                        h["value"]
                        for h in headers
                        if h["name"].lower() == "subject"
                    ),
                    "No Subject"
                )

                sender = next(
                    (
                        h["value"]
                        for h in headers
                        if h["name"].lower() == "from"
                    ),
                    "Unknown Sender"
                )

                output.append(
                    f"--- Email ID: {message['id']} ---\n"
                    f"From: {sender}\n"
                    f"Subject: {subject}\n"
                    f"Snippet: {detail.get('snippet', '')}\n"
                )

                return "\n".join(output)
            
        except Exception as e:
            return f"An error occurred during search: {e}"
            
def get_gmail_service() -> GmailService:
    return GmailService()