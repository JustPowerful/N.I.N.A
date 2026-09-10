import json

from fastapi import APIRouter, Depends

from app.agent.service import AgentService, get_agent_service
from app.agent.state import AgentEvent
from app.session.service import SessionService, get_session_service, MessageRole
from pydantic import BaseModel
from app.agent.eventmanager import event_manager
from app.agent.voice import VoiceClient, get_voice_client
import base64

# Import ServerSentEvent from sse_starlette
from sse_starlette import ServerSentEvent, EventSourceResponse

router = APIRouter(prefix='/chat', tags=['chat'])

class ChatRequest(BaseModel):
    session_id: str
    message: str
    generated_audio: bool = True  # Optional field to indicate if audio should be generated

class ChatResponse(BaseModel):
    response: str
    audio: str | None # Base64 encoded audio data that can be played in the frontend


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
    voice_service: VoiceClient = Depends(get_voice_client),
): 
    response = await agent_service.chat(message=request.message, session_uuid=request.session_id) 
    json_response = ChatResponse(response=response, audio=None)
    if request.generated_audio:
        if request.generated_audio:
                audio_context = await voice_service.generate_tts(text=response, voice='en-US-EmmaNeural')
                with audio_context as tts_response: 
                    audio_bytes = tts_response.read() # Read the audio data from the response
                    audio_b64_string = base64.b64encode(audio_bytes).decode('utf-8')
                json_response.audio = audio_b64_string

    return json_response


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
