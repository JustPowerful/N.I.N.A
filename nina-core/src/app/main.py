from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.session import router as session_router


app = FastAPI(
    title="N.I.N.A Assistant Core API",
    version="0.1.0",
)

# Origins can be configured to allow requests from a specific ip or domain later.

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(session_router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ev-core",
    }