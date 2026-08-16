from app.embeddings.service import EmbeddingService, get_embedding_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from functools import lru_cache
from app.knowledge.models import Knowledge

from fastapi import Depends
from app.db.engine import get_session

class KnowledgeService:
    
    def __init__(
            self,
            embeddingService: EmbeddingService,
            session: AsyncSession
    ):
        self.embeddingServie = embeddingService
        self.session = session

    async def save(self, content: str):
        embedding = await self.embeddingServie.embed(content)
        knowledge = Knowledge(
            content=content,
            embedding=embedding,
        )

        self.session.add(knowledge) # creates the object in memory
        await self.session.commit() # finally commits the transaction (clears data from the knowledge object to remove stale data)
        await self.session.refresh(knowledge) # refetches the knowledge object from the database

        return knowledge


    async def search(self, query: str, limit: int = 5):
        embedding = await self.embeddingServie.embed(query)
        result = await self.session.execute(
            select(Knowledge)
            .order_by(
                Knowledge.embedding.cosine_distance(embedding)
            )
            .limit(limit)
        )
        return result.scalars().all()


    async def delete(self, knowledge_id: int) -> bool:
        knowledge = await self.session.get(Knowledge, knowledge_id)
        if knowledge is None:
            return False
        await self.session.delete(knowledge)
        await self.session.commit()
        return True


    async def update(self, knowledge_id: int, content: str) -> Knowledge | None:
        knowledge = await self.session.get(Knowledge, knowledge_id)
        if knowledge is None:
            return None
        new_embedding = await self.embeddingServie.embed(content)
        knowledge.content = content
        knowledge.embedding = new_embedding
        await self.session.commit()
        await self.session.refresh(knowledge)
        return knowledge


async def get_knowledge_service(session: AsyncSession = Depends(get_session)):
    return KnowledgeService(embeddingService=get_embedding_service(), session=session)