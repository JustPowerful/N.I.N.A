from openai import AsyncOpenAI
from app.config import settings
from functools import lru_cache

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    
    # Temporary function until I code the logic
    async def embed(self, content: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=content,
            encoding_format='float'
        )
        embedding = response.data[0].embedding
        print("[DEBUG] embedding dimensions are the following:", len(embedding))
        return embedding

@lru_cache
def get_embedding_service():
    return EmbeddingService()