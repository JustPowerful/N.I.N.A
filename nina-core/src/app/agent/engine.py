from openai import AsyncOpenAI
from app.agent.state import AgentState
from app.config import settings
from openai.types.responses import ResponseInputParam

class Agent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    async def run(self, state: AgentState) -> str:
        input_messages: ResponseInputParam = [
            {
                "role": message.role,
                "content": message.content
            } for message in state.messages
        ]

        response = await self.client.responses.create(
            model=settings.model,
            instructions="""
            You are NINA, a personal AI assistant.

            Your job is to help the user accomplish tasks,
            answer questions, and interact with available tools.

            Be concise and useful.
            """,
            input=input_messages
        )
        
        return response.output_text