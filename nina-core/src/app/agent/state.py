"""
This module defines how the agent state is represented and managed.
It doesn't contain any logic for interacting with the OpenAI API or processing messages; that is handled in the engine module.
But it provides a structured way to store and manage the messages exchanged between the user and the assistant, which is crucial for maintaining context in conversations.
"""

from dataclasses import dataclass, field
from typing import Literal

# Literal hint is used to create a type that can only take on specific string values, which is useful for defining the role of a message in the conversation.
# In TypeScript its something like this: type MessageRole = "user" | "assistant" | "system" | "developer"
# Literal is not a runtime check, but it helps with type checking and code clarity.
MessageRole = Literal["user", "assistant", "system", "developer"]

@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class AgentState:
    messages: list[Message] = field(default_factory=list)

@dataclass
class AgentEvent:
    type: str
    data: dict

class AgentEventState:
    AGENT_STARTED = "agent.started"
    TOOL_STARTED = "agent.tool_started"
    TOOL_EXECUTED = "agent.tool_executed"
    TOOL_FAILED = "agent.tool_failed"
    AGENT_COMPLETED = "agent.completed"
    

