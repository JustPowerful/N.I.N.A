from app.agent.engine import Agent, get_agent
from app.agent.state import AgentState, Message
from app.agent.tools.registery import get_tools_registery
from app.db.engine import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


class AgentService:
    def __init__(self, agent: Agent):
        self.agent = agent

    
    async def chat(self, message: str) -> str:
        print("[DEBUG] AgentService.chat called with message:", message)
        state = AgentState(messages=[
            Message(role='user', content=message)
        ])
        
        return await self.agent.run(state)


async def get_agent_service(session: AsyncSession = Depends(get_session)):
    tools_registery = get_tools_registery(session=session)
    agent = get_agent(tools_registery=tools_registery)
    return AgentService(agent=agent)