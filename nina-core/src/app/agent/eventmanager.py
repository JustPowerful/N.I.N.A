import asyncio

from app.agent.state import AgentEvent


class AgentEventManager:

    def __init__(self):
        self.subscribers: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, session_id: str):
        queue = asyncio.Queue()

        self.subscribers.setdefault(session_id, []).append(queue)

        return queue

    def unsubscribe(
        self,
        session_id: str,
        queue: asyncio.Queue,
    ):
        subscribers = self.subscribers.get(session_id)

        if not subscribers:
            return

        if queue in subscribers:
            subscribers.remove(queue)

        if not subscribers:
            del self.subscribers[session_id]

    async def publish(
        self,
        session_id: str,
        event: AgentEvent,
    ):
        subscribers = self.subscribers.get(session_id, [])

        for queue in subscribers:
            await queue.put(event)

event_manager = AgentEventManager()