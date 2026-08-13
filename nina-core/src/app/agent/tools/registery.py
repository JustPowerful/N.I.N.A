
from .knowledge import KnowledgeTools, KnowledgeService
from app.embeddings.service import get_embedding_service
from sqlalchemy.ext.asyncio import AsyncSession

class ToolsRegistery:
    def __init__(self, knowledge_tools: KnowledgeTools) -> None:
        self.knowledge_tools = knowledge_tools

    
    # (*) used to get all tools and flatten the list of tools from each tool class into a single list
    # (*) is like ... in javascript
    def get_tools(self):
        return [
            *self.knowledge_tools.get_tools()
        ]

def get_tools_registery(session: AsyncSession):
    knowledge_service = KnowledgeService(
        embeddingService=get_embedding_service(),
        session=session,
    )

    knowledge_tools = KnowledgeTools(
        knowledgeService=knowledge_service
    )

    return ToolsRegistery(
        knowledge_tools=knowledge_tools,
    )