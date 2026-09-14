from pathlib import Path
from typing import Union, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from zoneinfo import ZoneInfo

tzinfo = ZoneInfo("Africa/Tunis")
TIMEZONE_NAME = tzinfo.key


def _to_timezone_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=tzinfo)
    else:
        value = value.astimezone(tzinfo)
    return value.isoformat()


def _normalize_datetime(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    if value.tzinfo is None:
        return value.replace(tzinfo=tzinfo)

    return value.astimezone(tzinfo)

class CalendarService:
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.freebusy'
    ]
    BASE_DIR = Path(__file__).resolve().parents[3] # Adjust the path to point to the root of your project
    CREDENTIALS_DIR = BASE_DIR / "credentials"
    CLIENT_SECRET_FILE = CREDENTIALS_DIR / "client_secret.json"
    TOKEN_FILE = CREDENTIALS_DIR / "calendar_token.json"


    def __init__(self) -> None:
        self.credentials = self._get_credentials()
        self.service = build(
            "calendar",
            "v3",
            credentials=self.credentials
        )


    def _get_credentials(self) -> Union[Credentials, ExternalAccountCredentials]:
            """Get valid credentials for Calendar API."""
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

    def search_events(self, time_min: datetime | str, time_max: datetime | str, query: str = "", max_results: int = 50, calendar_id: str = "primary"):
        """Search for events in the specified calendar."""

        time_min = _to_timezone_iso(_normalize_datetime(time_min))
        time_max = _to_timezone_iso(_normalize_datetime(time_max))

        events_result = self.service.events().list(
            calendarId=calendar_id,
            q=query,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            maxResults=max_results
        ).execute()
        return events_result.get('items', [])

    def get_event_details(self, event_id: str, calendar_id: str = "primary"):
        """Get details of a specific event."""
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        return event    

    def create_event(self, summary: str, start: datetime, end: datetime, description: str | None = None, location: str | None = None, attendees: list[str] | None = None, calendar_id: str = "primary"):
        """Create a new event in the specified calendar."""
        
        event_body = {
            "summary": summary,
            "start": {"dateTime": _to_timezone_iso(start), "timeZone": TIMEZONE_NAME},
            "end": {"dateTime": _to_timezone_iso(end), "timeZone": TIMEZONE_NAME},
        }
        if description:
            event_body["description"] = description
        if location:
            event_body["location"] = location
        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        event = self.service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()
        return event

    async def update_event(
        self,
        event_id: str,
        summary: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        description: str | None = None,
        location: str | None = None,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        event = self.get_event_details(
            event_id=event_id,
            calendar_id=calendar_id,
        )

        if summary is not None:
            event["summary"] = summary

        if description is not None:
            event["description"] = description

        if location is not None:
            event["location"] = location

        if start is not None:
            event["start"] = {
                "dateTime": _to_timezone_iso(start),
                "timeZone": TIMEZONE_NAME,
            }

        if end is not None:
            event["end"] = {
                "dateTime": _to_timezone_iso(end),
                "timeZone": TIMEZONE_NAME,
            }

        return (
            self.service.events()
            .update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates="all",
            )
            .execute()
        )

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> None:
        (
            self.service.events()
            .delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates="all",
            )
            .execute()
        )

    async def check_availability(
        self,
        time_min: datetime | str,
        time_max: datetime | str,
        calendar_id: str = "primary",
    ) -> list[dict[str, Any]]:
        response = (
            self.service.freebusy()
            .query(
                body={
                    "timeMin": _to_timezone_iso(_normalize_datetime(time_min)),
                    "timeMax": _to_timezone_iso(_normalize_datetime(time_max)),
                    "items": [
                        {
                            "id": calendar_id,
                        }
                    ],
                }
            )
            .execute()
        )

        calendars = response.get("calendars", {})

        return calendars.get(calendar_id, {}).get("busy", [])


def get_calendar_service() -> CalendarService:
    return CalendarService()