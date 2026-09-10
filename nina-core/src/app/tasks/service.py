from datetime import datetime
from typing import Optional
from app.tasks.models import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.db.engine import get_session

class TasksService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_task(self, title: str, description: str | None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Task:
        # if isinstance(start_date, str):
        #     start_date = datetime.fromisoformat(start_date)

        # if isinstance(end_date, str):
        #     end_date = datetime.fromisoformat(end_date)

        task = Task(title=title, description=description, start_date=start_date, end_date=end_date)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: int) -> Optional[Task]:
        return await self.db.get(Task, task_id)


    async def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[Task]:
        task = await self.get_task(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if start_date is not None:
                setattr(task, 'start_date', start_date)
            if end_date is not None:
                setattr(task, 'end_date', end_date)
            await self.db.commit()
            await self.db.refresh(task)
            return task
        return None


    async def delete_task(self, task_id: int):
        task = await self.get_task(task_id)
        if task:
            await self.db.delete(task)
            await self.db.commit()
            return True
        return False

    async def search_tasks(self, title: Optional[str] = None, description: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) :
        query = select(Task)
        if title:
            query = query.where(Task.title.ilike(f"%{title}%"))
        if description:
            query = query.where(Task.description.ilike(f"%{description}%"))
        if start_date and end_date:
            query = query.where(Task.start_date >= start_date, Task.end_date <= end_date)
        elif start_date:
            query = query.where(Task.start_date >= start_date)
        elif end_date:
            query = query.where(Task.end_date <= end_date)
        result = await self.db.execute(query)
        return result.scalars().all()

def get_tasks_service(db: AsyncSession = Depends(get_session)) -> TasksService:
    return TasksService(db)