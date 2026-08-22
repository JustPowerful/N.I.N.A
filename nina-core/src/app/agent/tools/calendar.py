from app.calendar.service import CalendarService
from typing import Any
from datetime import datetime
from app.agent.tool import Tool

class CalendarTools:
    def __init__(self, calendar_service: CalendarService):
            self.calendar_service = calendar_service

    def search_events(self, time_min: datetime, time_max: datetime, query: str = "", max_results: int = 50, calendar_id: str = "primary"):
        """
        Search for events in the user's calendar based on a time range and an optional query.

        Args:
            time_min: The start of the time range to search for events (datetime).
            time_max: The end of the time range to search for events (datetime).
            query: An optional search query to filter events (default is an empty string).
            max_results: The maximum number of event results to return (default is 50).
            calendar_id: The ID of the calendar to search in (default is "primary").
        """

        results = self.calendar_service.search_events(
            time_min=time_min,
            time_max=time_max,
            query=query,
            max_results=max_results,
            calendar_id=calendar_id
        )
        return results

    async def get_event_details(self, event_id: str, calendar_id: str = "primary"):
        """
        Get details of a specific event in the user's calendar.

        Args:
            event_id: The ID of the event to retrieve details for.
            calendar_id: The ID of the calendar to search in (default is "primary").
        """

        result = self.calendar_service.get_event_details(
            event_id=event_id,
            calendar_id=calendar_id
        )
        return result

    def create_event(self, summary: str, start: datetime, end: datetime, description: str | None = None, location: str | None = None, attendees: list[str] | None = None, calendar_id: str = "primary"):
        """
        Create a new event in the user's calendar.

        Args:
            summary: The title or summary of the event.
            start: The start time of the event (datetime).
            end: The end time of the event (datetime).
            description: An optional description of the event (default is None).
            location: An optional location for the event (default is None).
            attendees: An optional list of email addresses for attendees (default is None).
            calendar_id: The ID of the calendar to create the event in (default is "primary").
        """

        result = self.calendar_service.create_event(
            summary=summary,
            start=start,
            end=end,
            description=description,
            location=location,
            attendees=attendees,
            calendar_id=calendar_id
        )
        return result

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
        """
        Update an existing event in the user's calendar.

        Args:
            event_id: The ID of the event to update.
            summary: An optional new title or summary for the event (default is None).
            start: An optional new start time for the event (datetime, default is None).
            end: An optional new end time for the event (datetime, default is None).
            description: An optional new description for the event (default is None).
            location: An optional new location for the event (default is None).
            calendar_id: The ID of the calendar containing the event (default is "primary").
        """
         
        result = await self.calendar_service.update_event(
            event_id=event_id,
            summary=summary,
            start=start,
            end=end,
            description=description,
            location=location,
            calendar_id=calendar_id
        )
        return result

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> None:  
        """
        Delete an existing event from the user's calendar.

        Args:
                event_id: The ID of the event to delete.
                calendar_id: The ID of the calendar containing the event (default is "primary").
        """
        await self.calendar_service.delete_event(
                event_id=event_id,
                calendar_id=calendar_id
            )   

    async def check_availability(
        self,
        time_min: datetime,
        time_max: datetime,
        calendar_id: str = "primary",
    ) -> list[dict[str, Any]]:
        """
        Check the availability of the user's calendar within a specified time range.

        Args:
            time_min: The start of the time range to check for availability (datetime).
            time_max: The end of the time range to check for availability (datetime).
            calendar_id: The ID of the calendar to check availability in (default is "primary").
        """

        results = await self.calendar_service.check_availability(
            time_min=time_min,
            time_max=time_max,
            calendar_id=calendar_id
        )
        return results

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name='search_events',
                description='Search for events in the user\'s calendar based on a time range and an optional query.',
                parameters={
                    "type": "object",
                    "properties": {
                        "time_min": {
                            "type": "string",
                            "format": "date-time",
                            "description": "The start of the time range to search for events (datetime)."
                        },
                        "time_max": {
                            "type": "string",
                            "format": "date-time",
                            "description": "The end of the time range to search for events (datetime)."
                        },
                        "query": {
                            "type": "string",
                            "description": "An optional search query to filter events (default is an empty string)."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "The maximum number of event results to return (default is 50)."
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to search in (default is "primary").'
                        }
                    },
                    "required": ["time_min", "time_max"]
                },
                function=self.search_events
            ),
            Tool(
                name='get_event_details',
                description='Get details of a specific event in the user\'s calendar.',
                parameters={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": 'The ID of the event to retrieve details for.'
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to search in (default is "primary").'
                        }
                    },
                },
                function=self.get_event_details
            ),
            Tool(
                name='create_event',
                description='Create a new event in the user\'s calendar.',
                parameters={
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": 'The title or summary of the event.',
                        },
                        "description": {
                            "type": "string",
                            "description": 'The description of the event.'
                        },
                        "start": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The start time of the event (datetime).'
                        },
                        "end": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The end time of the event (datetime).'
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to create the event in (default is "primary").'
                        }
                    },
                    "required": ["summary", "start", "end"]
                },
                function=self.create_event
            ),
            Tool(
                name='update_event',
                description='Update an existing event in the user\'s calendar.',
                parameters={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": 'The ID of the event to update.'
                        },
                        "summary": {
                            "type": "string",
                            "description": 'The title or summary of the event.'
                        },
                        "description": {
                            "type": "string",
                            "description": 'The description of the event.'
                        },
                        "start": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The start time of the event (datetime).'
                        },
                        "end": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The end time of the event (datetime).'
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to update the event in (default is "primary").'
                        }
                    }
                },
                function=self.update_event
            ),
            Tool(
                name='delete_event',
                description='Delete an existing event from the user\'s calendar.',
                parameters={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": 'The ID of the event to delete.'
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to delete the event from (default is "primary").'
                        }
                    }
                },
                function=self.delete_event
            ),
            Tool(
                name='check_availability',
                description='Check the availability of the user\'s calendar within a specified time range.',
                parameters={
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The start time of the time range (datetime).'
                        },
                        "end": {
                            "type": "string",
                            "format": "date-time",
                            "description": 'The end time of the time range (datetime).'
                        },
                        "calendar_id": {
                            "type": "string",
                            "description": 'The ID of the calendar to check availability for (default is "primary").'
                        }
                    },
                    "required": ["start", "end"]
                },
                function=self.check_availability
            ),
        ]
    