from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.session.models import Session, ChatMessage, MessageRole
from fastapi import Depends
from app.db.engine import get_session
class SessionService:
    def __init__(
            self, 
            db: AsyncSession,
    ):
        
        self.db = db

    async def create_session(self, title: Optional[str] = "New Chat") -> Session:
        """Create and return a new chat session."""
        session = Session(title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    # Fetching all sessions is useful for UI to display a list of sessions for the user to select from
    async def get_all_session(self) -> List[Session]:
        """Fetch all chat sessions."""
        stmt = select(Session).order_by(Session.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


    async def get_session_by_uuid(self, session_uuid: str) -> Optional[Session]:
        """Fetch session metadata by UUID"""
        stmt = select(Session).where(Session.id == session_uuid)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # This is usually used to fetch messages in UI chat systems for user readability
    # WARNING: don't pass all the messages to the agent, this will be token consuming
    async def get_session_messages(self, session_uuid: str) -> List[ChatMessage]:
        """Fetch chronologically ordered messages for a session"""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_uuid)
            .order_by(ChatMessage.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Instead of using get_session_messages we can use something like get_session_n_last_messages
    # Note that the messages should be formatted to the way the agent client understands it
    async def get_session_n_last_messages(self, session_uuid: str, n: int) -> List[ChatMessage]:
        """Fetch the last n messages for a session"""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_uuid)
            .order_by(ChatMessage.created_at.desc())
            .limit(n)
        )
        result = await self.db.execute(stmt)
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Reverse to maintain chronological order


    async def add_message(self, session_uuid: str, role: MessageRole, content: str) -> ChatMessage:
        """
        Add a single message (user or assistant) to a session.
        This is a helper function and can be used to add messages to a session.
        Could be imported and used in other services like ChatService or AgentService to add messages to a session.
        """
        message = ChatMessage(session_id=session_uuid, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message


    async def delete_session(self, session_uuid: str) -> bool:
        """Delete session and cascade delete all associated messages."""
        stmt = select(Session).where(Session.id == session_uuid)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True
        return False


def get_session_service(db: AsyncSession = Depends(get_session)) -> SessionService:
    """Get an instance of the chat session service"""
    return SessionService(db)