from .knowledge import KnowledgeTools, KnowledgeService
from .gmail import GmailTools, GmailService
from .calendar import CalendarTools, CalendarService
from .browser import BrowserTools
from .tasks import TasksTools

from app.browser.registery import get_browser_manager
from app.embeddings.service import get_embedding_service
from app.tasks.service import TasksService

from sqlalchemy.ext.asyncio import AsyncSession


class ToolsRegistery:
    def __init__(
        self,
        knowledge_tools: KnowledgeTools,
        gmail_tools: GmailTools,
        calendar_tools: CalendarTools,
        browser_tools: BrowserTools,
        tasks_tools: TasksTools,
    ) -> None:
        self.knowledge_tools = knowledge_tools
        self.gmail_tools = gmail_tools
        self.calendar_tools = calendar_tools
        self.browser_tools = browser_tools
        self.tasks_tools = tasks_tools

    def get_tools(self):
        return [
            *self.knowledge_tools.get_tools(),
            *self.gmail_tools.get_tools(),
            *self.calendar_tools.get_tools(),
            *self.browser_tools.get_tools(),
            *self.tasks_tools.get_tools(),
        ]


def get_tools_registery(
    session: AsyncSession,
    session_id: str,
):
    # -------------------------
    # Knowledge
    # -------------------------

    knowledge_service = KnowledgeService(
        embeddingService=get_embedding_service(),
        session=session,
    )

    knowledge_tools = KnowledgeTools(
        knowledgeService=knowledge_service,
    )

    # -------------------------
    # Gmail
    # -------------------------

    gmail_service = GmailService()

    gmail_tools = GmailTools(
        gmail_service=gmail_service,
    )

    # -------------------------
    # Calendar
    # -------------------------

    calendar_service = CalendarService()

    calendar_tools = CalendarTools(
        calendar_service=calendar_service,
    )

    # -------------------------
    # Browser
    # -------------------------

    # IMPORTANT:
    # Get the BrowserManager associated with this chat session.
    #
    # This does NOT create a new BrowserManager if one already exists.
    browser_manager = get_browser_manager(session_id)

    browser_tools = BrowserTools(
        browser=browser_manager,
    )

    # -------------------------
    # Tasks
    # -------------------------

    tasks_service = TasksService(
        db=session,
    )

    tasks_tools = TasksTools(
        tasksService=tasks_service,
    )

    # -------------------------
    # Registry
    # -------------------------

    return ToolsRegistery(
        knowledge_tools=knowledge_tools,
        gmail_tools=gmail_tools,
        calendar_tools=calendar_tools,
        browser_tools=browser_tools,
        tasks_tools=tasks_tools,
    )