from app.agent.engine import Agent, get_agent
from app.session.service import SessionService, get_session_service, MessageRole
from app.agent.state import AgentState, Message, MessageRole as AgentMessageRole
from app.agent.tools.registery import get_tools_registery
from app.db.engine import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import cast


class AgentService:
    def __init__(self, agent: Agent, session_service: SessionService = Depends(get_session_service)):
        self.agent = agent
        self.session_service = session_service

    def parse_role(self, raw_role: object) -> AgentMessageRole:
        val = (raw_role.value if isinstance(raw_role, MessageRole) else str(raw_role)).lower()
        if val in ("user", "assistant", "system", "developer"):
            return cast(AgentMessageRole, val)
        raise ValueError(f"Invalid message role: {raw_role}")
    
    async def chat(self, message: str, session_uuid: str) -> str:
        print("[DEBUG] AgentService.chat called with message:", message, "and session_uuid:", session_uuid)

        past_db_messages = await self.session_service.get_session_n_last_messages(session_uuid=session_uuid, n=10)

        print("[DEBUG] AgentService.chat saving user message to session:", session_uuid)
        # Save the user's message after fetching the history to avoid duplicating the last message in the history
        await self.session_service.add_message(session_uuid=session_uuid, role=MessageRole.USER, content=message)

        state_messages = [
            Message(
                role=self.parse_role(msg.role),
                content=msg.content
            )
            for msg in past_db_messages
        ]

        state_messages.append(Message(role="user", content=message))

        # Debug the messages being sent to the agent
        print("[DEBUG] AgentService.chat state_messages being sent to agent:", state_messages)

        # Message accept 'user' and not MessageRole.USER because it's a separate model for the agent state, not the session enum logic
        state = AgentState(messages=state_messages)
        
        result = await self.agent.run(state)
        await self.session_service.add_message(session_uuid=session_uuid, role=MessageRole.ASSISTANT, content=result)
        return result

async def get_agent_service(session: AsyncSession = Depends(get_session), session_service: SessionService = Depends(get_session_service)) -> AgentService:
    tools_registery = get_tools_registery(session=session)
    agent = get_agent(tools_registery=tools_registery)
    return AgentService(agent=agent, session_service=session_service)