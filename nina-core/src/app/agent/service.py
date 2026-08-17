from app.agent.engine import Agent, get_agent
from app.session.service import SessionService, get_session_service, MessageRole
from app.agent.state import AgentState, Message
from app.agent.tools.registery import get_tools_registery
from app.db.engine import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


class AgentService:
    def __init__(self, agent: Agent, session_service: SessionService = Depends(get_session_service)):
        self.agent = agent
        self.session_service = session_service
    
    async def chat(self, message: str, session_uuid: str) -> str:
        print("[DEBUG] AgentService.chat called with message:", message, "and session_uuid:", session_uuid)
        await self.session_service.add_message(session_uuid=session_uuid, role=MessageRole.USER, content=message)

        # Message accept 'user' and not MessageRole.USER because it's a separate model for the agent state, not the session enum logic
        state = AgentState(messages=[
            Message(role='user', content=message)
        ])
        
        result = await self.agent.run(state)
        await self.session_service.add_message(session_uuid=session_uuid, role=MessageRole.ASSISTANT, content=result)
        return result

async def get_agent_service(session: AsyncSession = Depends(get_session), session_service: SessionService = Depends(get_session_service)) -> AgentService:
    tools_registery = get_tools_registery(session=session)
    agent = get_agent(tools_registery=tools_registery)
    return AgentService(agent=agent, session_service=session_service)