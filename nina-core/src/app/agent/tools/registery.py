
from .knowledge import KnowledgeTools, KnowledgeService
from .gmail import GmailTools, GmailService
from .calendar import CalendarTools, CalendarService
from app.embeddings.service import get_embedding_service
from sqlalchemy.ext.asyncio import AsyncSession

class ToolsRegistery:
    def __init__(self, knowledge_tools: KnowledgeTools, gmail_tools: GmailTools, calendar_tools: CalendarTools) -> None:
        self.knowledge_tools = knowledge_tools
        self.gmail_tools = gmail_tools
        self.calendar_tools = calendar_tools

    # (*) used to get all tools and flatten the list of tools from each tool class into a single list
    # (*) is like ... in javascript
    def get_tools(self):
        return [
            *self.knowledge_tools.get_tools(),
            *self.gmail_tools.get_tools(),
            *self.calendar_tools.get_tools()
        ]

def get_tools_registery(session: AsyncSession):
    knowledge_service = KnowledgeService(
        embeddingService=get_embedding_service(),
        session=session,
    )

    knowledge_tools = KnowledgeTools(
        knowledgeService=knowledge_service
    )

    gmail_service = GmailService()
    gmail_tools = GmailTools(
        gmail_service=gmail_service
    )

    calendar_service = CalendarService()
    calendar_tools = CalendarTools(
        calendar_service=calendar_service
    )

    return ToolsRegistery(
        knowledge_tools=knowledge_tools,
        gmail_tools=gmail_tools,
        calendar_tools=calendar_tools
    )