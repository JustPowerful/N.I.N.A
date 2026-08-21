import asyncio
import json

from fastapi import APIRouter, Depends

from app.agent.service import AgentService, get_agent_service
from app.agent.state import AgentEvent
from app.session.service import SessionService, get_session_service, MessageRole
from pydantic import BaseModel
from app.agent.eventmanager import event_manager

# Import ServerSentEvent from sse_starlette
from sse_starlette import ServerSentEvent, EventSourceResponse

router = APIRouter(prefix='/chat', tags=['chat'])

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str


class GetMessagesResponse(BaseModel):
    response: str
    messages: list


@router.get("/events/{session_id}")
async def events(session_id: str):
    queue = event_manager.subscribe(session_id)

    async def event_stream():
        try:
            while True:
                event: AgentEvent = await queue.get()
                payload = json.dumps(event.data) if event.data is not None else "{}"
                yield ServerSentEvent(event=event.type, data=payload)
        finally:
            event_manager.unsubscribe(session_id, queue)

    return EventSourceResponse(event_stream())

@router.post("/send", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
): 
    response = await agent_service.chat(message=request.message, session_uuid=request.session_id) 
    return ChatResponse(response=response)


@router.get("/getmessages/{session_id}", response_model=GetMessagesResponse)
async def get_messages(session_id: str, session_service: SessionService = Depends(get_session_service)):
    messages = await session_service.get_session_messages(session_id)
    response = [{
        "role": message.role,
        "content": message.content,
        "timestamp": message.created_at.isoformat()
    } for message in messages]
    return GetMessagesResponse(
        response=f"Successfully fetched messages for session {session_id}",
        messages=response
    )
