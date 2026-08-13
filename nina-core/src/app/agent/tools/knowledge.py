from app.knowledge.service import KnowledgeService, get_knowledge_service
from app.agent.tool import Tool
from functools import lru_cache 


class KnowledgeTools:
    def __init__(self, knowledgeService: KnowledgeService) -> None:
        self.knowledgeService = knowledgeService

    async def save_knowledge(self, content: str):
        """
        Save an important piece of information to NINA's long-term knowledge memory.

        Args:
            content: The information that should be remembered.
        """
        knowledge = await self.knowledgeService.save(content)
        return {
            "id": knowledge.id,
            "content": knowledge.content
        }


    async def search_knowledge(self, query: str, limit: int = 5):
        results = await self.knowledgeService.search(query, limit)
        return [
            {
                "id": knowledge.id,
                "content": knowledge.content,
            }
            for knowledge in results
        ]

    # Used to get all the tools
    # Every tool created must be exported from here and included in the tool registery
    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name='save_knowledge',
                description="Save information to NINA's long-term memory.",
                parameters={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Information to remember.",
                        }
                    },
                    "required": ["content"],
                },
                function=self.save_knowledge
            ),
            Tool(
                name='search_knowledge',
                description='Get important information from NINA\' long-term memory',
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Information to search.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results to return.",
                        }
                    }
                },
                function=self.search_knowledge
            )
        ]
