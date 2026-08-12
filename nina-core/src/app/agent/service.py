from app.agent.engine import Agent
from app.agent.state import AgentState, Message


class AgentService:
    def __init__(self, agent: Agent):
        self.agent = agent

    async def chat(self, message: str) -> str:
        state = AgentState(messages=[
            Message(role='user', content=message)
        ])
        return await self.agent.run(state)
        