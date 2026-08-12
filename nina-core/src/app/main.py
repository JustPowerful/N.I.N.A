from fastapi import FastAPI

from app.api.routes.chat import router as chat_router


app = FastAPI(
    title="N.I.N.A Assistant Core API",
    version="0.1.0",
)

app.include_router(chat_router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ev-core",
    }