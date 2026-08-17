from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.session.service import get_session_service, SessionService

router = APIRouter(prefix='/session', tags=['session'])

class CreateSessionRequest(BaseModel):
    title: str

class CreateSessionResponse(BaseModel):
    session_id: str
    response: str

class DeleteSessionResponse(BaseModel):
    response: str

class GetMessagesResponse(BaseModel):
    response: str
    messages: list


class GetSessionDetailsResponse(BaseModel):
    response: str
    session_id: str
    title: str
    created_at: str
    updated_at: str


@router.post('/create', response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest, session_service: SessionService = Depends(get_session_service)):
    session = await session_service.create_session(title=request.title)
    return CreateSessionResponse(session_id=session.id, response="Successfully created a new session")

@router.get("/details/{session_id}", response_model=GetSessionDetailsResponse)
async def get_session_details(session_id: str, session_service: SessionService = Depends(get_session_service)):
    session = await session_service.get_session_by_uuid(session_uuid=session_id)
    if session:
        return GetSessionDetailsResponse(
            response=f"Successfully fetched details for session {session_id}",
            session_id=session.id,
            title=session.title or "Untitled Session",
            created_at=session.created_at.isoformat(),
            updated_at=session.update_at.isoformat()
        )
    raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")

@router.delete("/delete/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str, session_service: SessionService = Depends(get_session_service)):
    success = await session_service.delete_session(session_uuid=session_id)
    if success:
        return DeleteSessionResponse(response=f"Successfully deleted session {session_id}")
    else:
        raise HTTPException(status_code=404, detail=f"Session with ID {session_id} not found")

@router.get("/getmessages/{session_id}", response_model=GetMessagesResponse)
async def get_messages(session_id: str, session_service: SessionService = Depends(get_session_service)):
    messages = await session_service.get_session_messages(session_id)
    return GetMessagesResponse(
        response=f"Successfully fetched messages for session {session_id}",
        messages=messages
    )
