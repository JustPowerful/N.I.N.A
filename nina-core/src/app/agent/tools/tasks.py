from app.tasks.service import TasksService
from app.agent.tool import Tool
from datetime import datetime

class TasksTools:
    def __init__(self, tasksService: TasksService):
        self.tasksService = tasksService

    async def get_task(self, task_id: int):
        """
        Retrieve a task by its ID.

        Args:
            task_id: The ID of the task to be retrieved.
        """
        task = await self.tasksService.get_task(task_id)
        if not task:
            return {
                "success": False,
                "message": "Task not found."
            }

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None
        }

    async def search_tasks(self, title: str | None = None, description: str | None = None, start_date: str | None = None, end_date: str | None = None):
        """
        Search for tasks based on various criteria.

        Args:
            title: The title of the task (optional).
            description: The description of the task (optional).
            start_date: The start date of the task (optional).
            end_date: The end date of the task (optional).
        """

        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        

        tasks = await self.tasksService.search_tasks(title, description, start, end)
        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None
            }
            for task in tasks
        ]

    async def create_task(self, title: str, description: str | None = None, start_date: str | None = None, end_date: str | None = None):
        """
        Create a new task.

        Args:
            title: The title of the task.
            description: The description of the task. (optional)
            start_date: The start date of the task (optional).
            end_date: The end date of the task (optional).
        """
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        task = await self.tasksService.create_task(title, description, start, end)
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None
        }

    async def delete_task(self, task_id: int):
        """
        Delete a task by its ID.

        Args:
            task_id: The ID of the task to be deleted.
        """

        deleted = await self.tasksService.delete_task(task_id)
        if not deleted:
            return {
                "success": False,
                "message": "Task not found."
            }

        return {
            "success": True,
            "task_id": task_id
        }


    async def update_task(self, task_id: int, title: str | None = None, description: str | None = None, start_date: str | None = None, end_date: str | None = None):
        """
        Update a task by its ID.

        Args:
            task_id: The ID of the task to be updated.
            title: The new title of the task (optional).
            description: The new description of the task (optional).
            start_date: The new start date of the task (optional).
            end_date: The new end date of the task (optional).
        """
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        task = await self.tasksService.update_task(task_id, title, description, start, end)
        if not task:
            return {
                "success": False,
                "message": "Task not found."
            }

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None
        }

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name='get_task',
                description='Retrieve a task by its ID',
                function=self.get_task,
                parameters={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to be retrieved."
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name='search_tasks',
                description='Search for tasks based on various criteria',
                function=self.search_tasks,
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the task (optional)."
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the task (optional)."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the task (optional)."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date of the task (optional)."
                        }
                    }
                }
            ),
            Tool(
                name='create_task',
                description='Create a new task',
                function=self.create_task,
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the task."
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the task. (optional)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The start date of the task (optional)."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The end date of the task (optional)."
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name='delete_task',
                description='Delete a task by its ID',
                function=self.delete_task,
                parameters={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to be deleted."
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name='update_task',
                description='Update a task by its ID',
                function=self.update_task,
                parameters={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to be updated."
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title of the task (optional)."
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description of the task (optional)."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "The new start date of the task (optional)."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "The new end date of the task (optional)."
                        }
                    },
                    "required": ["task_id"]
                }
            )
        ]