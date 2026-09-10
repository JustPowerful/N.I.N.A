from app.agent.engine import Agent, get_agent
from app.session.service import (
    SessionService,
    get_session_service,
    MessageRole,
)
from app.agent.state import (
    AgentState,
    Message,
    MessageRole as AgentMessageRole,
    AgentEvent,
)
from app.agent.eventmanager import event_manager
from app.agent.tools.registery import get_tools_registery
from app.db.engine import get_session

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from typing import cast


class AgentService:
    def __init__(
        self,
        session: AsyncSession,
        session_service: SessionService,
    ):
        self.session = session
        self.session_service = session_service

    def parse_role(self, raw_role: object) -> AgentMessageRole:
        val = (
            raw_role.value
            if isinstance(raw_role, MessageRole)
            else str(raw_role)
        ).lower()

        if val in ("user", "assistant", "system", "developer"):
            return cast(AgentMessageRole, val)

        raise ValueError(f"Invalid message role: {raw_role}")

    async def chat(
        self,
        message: str,
        session_uuid: str,
    ) -> str:

        print(
            "[DEBUG] AgentService.chat called with message:",
            message,
            "and session_uuid:",
            session_uuid,
        )

        # --------------------------------------------------
        # IMPORTANT:
        # Create/get tools for THIS chat session.
        #
        # The BrowserManager is retrieved using session_uuid,
        # so subsequent messages reuse the same browser.
        # --------------------------------------------------

        tools_registery = get_tools_registery(
            session=self.session,
            session_id=session_uuid,
        )

        agent = get_agent(
            tools_registery=tools_registery,
        )

        # --------------------------------------------------
        # Load previous messages
        # --------------------------------------------------

        past_db_messages = (
            await self.session_service.get_session_n_last_messages(
                session_uuid=session_uuid,
                n=10,
            )
        )

        # Save user's message
        await self.session_service.add_message(
            session_uuid=session_uuid,
            role=MessageRole.USER,
            content=message,
        )

        # --------------------------------------------------
        # Build agent state
        # --------------------------------------------------

        state_messages = [
            Message(
                role=self.parse_role(msg.role),
                content=msg.content,
            )
            for msg in past_db_messages
        ]

        state_messages.append(
            Message(
                role="user",
                content=message,
            )
        )

        print(
            "[DEBUG] AgentService.chat state_messages "
            "being sent to agent:",
            state_messages,
        )

        state = AgentState(
            messages=state_messages,
        )

        # --------------------------------------------------
        # Events
        # --------------------------------------------------

        async def event_handler(event: AgentEvent):
            await event_manager.publish(
                session_id=session_uuid,
                event=event,
            )

        # --------------------------------------------------
        # Run agent
        # --------------------------------------------------

        result = await agent.run(
            state,
            event_handler=event_handler,
        )

        # --------------------------------------------------
        # Save assistant response
        # --------------------------------------------------

        await self.session_service.add_message(
            session_uuid=session_uuid,
            role=MessageRole.ASSISTANT,
            content=result,
        )

        return result


async def get_agent_service(
    session: AsyncSession = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> AgentService:
    return AgentService(
        session=session,
        session_service=session_service,
    )