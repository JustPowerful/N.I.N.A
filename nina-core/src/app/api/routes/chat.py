from fastapi import APIRouter, Depends

from app.agent.service import AgentService, get_agent_service
from app.session.service import SessionService, get_session_service, MessageRole
from pydantic import BaseModel

router = APIRouter(prefix='/chat', tags=['chat'])

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str

@router.post("/send", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service),
): 
    response = await agent_service.chat(message=request.message, session_uuid=request.session_id) 
    return ChatResponse(response=response)