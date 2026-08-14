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

    async def delete_knowledge(self, knowledge_id: int):
        deleted = await self.knowledgeService.delete(knowledge_id)
        if not deleted:
            return {
                "success": False,
                "message": "Knowledge not found."
            }

        return {
            "success": True,
            "knowledge_id": knowledge_id
        }

    async def update_knowledge(self, knowledge_id: int, content: str):
        knowledge = await self.knowledgeService.update(knowledge_id, content)
        if not knowledge:
            return {
                "success": False,
                "message": "Knowledge not found."
            }

        return {
            "id": knowledge.id,
            "content": knowledge.content
        }

    # Used to get all the tools
    # Every tool created must be exported from here and included in the tool registery
    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name='save_knowledge',
                description="""
                Store a new piece of information in the user's knowledge base.

                Use this ONLY when the information is genuinely new and there
                is no existing knowledge that should be modified.

                If the user is correcting, changing, or updating existing information,
                first search the knowledge base and then use update_knowledge.
                """,
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
                description='Get important information from NINA\'s long-term memory',
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
            ),
            Tool(
                name='delete_knowledge',
                description='Delete knowledge from NINA\'s long-term memory',
                parameters={
                    "type": "object",
                    "properties": {
                        "knowledge_id": {
                            "type": "integer",
                            "description": "The ID of the knowledge data to delete"
                        }
                    }
                },
                function=self.delete_knowledge
            ),
            Tool(
                name="update_knowledge",
                description="""
                Update an existing knowledge entry.

                Use this when the user corrects, changes, or modifies information
                that is already stored in the knowledge base.

                Before using this tool, use search_knowledge to find the existing
                knowledge entry and obtain its ID.

                Do not create a new knowledge entry when an existing entry represents
                the same fact.
                """,
                parameters={
                    "type": "object",
                    "properties": {
                        "knowledge_id": {
                            "type": "integer",
                            "description": "The ID of the knowledge data to update"
                        },
                        "content": {
                            "type": "string",
                            "description": "The new knowledge data"
                        }
                    }
                },
                function=self.update_knowledge
            )
        ]
