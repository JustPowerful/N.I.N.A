from app.gmail.service import GmailService, get_gmail_service
from app.agent.tool import Tool

class GmailTools:
    def __init__(self, gmail_service: GmailService):
        self.gmail_service = gmail_service

    async def search_emails(self, query: str, limit: int):
        """
        Search for emails in the user's Gmail account based on a query.

        Args:
            query: The search query (e.g., "from:<email_address>", "subject:<subject_text>", etc.).
            limit: The maximum number of email results to return.
        """

        results = await self.gmail_service.search_messages(query=query, max_results=limit)
        return results


        # TODO: implement mail sending functionality


    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name='search_emails',
                description='Search for emails in the user\'s Gmail account based on a query.',
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query (e.g., 'from:<email_address>', 'subject:<subject_text>', etc.)."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "The maximum number of email results to return."
                        }
                    },
                },
                function=self.search_emails
            )
        ]