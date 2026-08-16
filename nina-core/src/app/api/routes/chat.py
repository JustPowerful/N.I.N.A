from fastapi import APIRouter, Depends

from app.agent.service import AgentService, get_agent_service
from pydantic import BaseModel

router = APIRouter(prefix='/chat', tags=['chat'])

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, agent_service: AgentService = Depends(get_agent_service)): 
    response = await agent_service.chat(request.message)
    return ChatResponse(response=response)