from fastapi import APIRouter

from app.agent.engine import Agent
from app.agent.service import AgentService
from pydantic import BaseModel


router = APIRouter(prefix='/chat', tags=['chat'])

agent_service = AgentService(
    agent=Agent()
)

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest): 
    response = await agent_service.chat(request.message)
    return ChatResponse(response=response)