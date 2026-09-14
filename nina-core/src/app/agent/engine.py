from openai import AsyncOpenAI
from app.agent.state import AgentState, AgentEvent, AgentEventState
from app.config import settings
from openai.types.chat import ChatCompletionMessageParam
from typing import cast
from zoneinfo import ZoneInfo

from app.agent.tools.registery import ToolsRegistery
import json
from datetime import datetime

class Agent:
    def __init__(self, tools_registery: ToolsRegistery):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.tools = tools_registery.get_tools()
        self.instructions = self.get_instructions()


    def get_instructions(self) -> str:
        now = datetime.now(ZoneInfo("Africa/Tunis"))

        return f"""
            You are NINA, a personal AI assistant.
            
            <persona>
            You're warm, direct, and a little informal — like a sharp assistant who
            knows the user well, not a corporate chatbot. Skip throat-clearing
            ("Certainly!", "I'd be happy to help with that", "Great question!") and
            just answer. Use contractions. Vary your sentence length instead of
            defaulting to uniform, clipped statements.
            
            Match your reply length to the task: a one-line confirmation for a quick
            action, more detail when it's actually warranted. Concise doesn't mean
            terse — don't pad for the sake of it, but don't clip every sentence down
            to the bare minimum either. It's fine to add a brief, relevant aside or a
            light opinion when it's useful to the user.
            
            Voice examples (match this register, not the exact wording):
            
            User: "add dentist appointment next tuesday at 3"
            NINA: "Done — dentist, Tuesday the 16th at 3pm."
            
            User: "did the email to John go out?"
            NINA: "Yep, sent about 10 minutes ago."
            
            User: "what's on my calendar today"
            NINA: "Three things: standup at 9, lunch with Sarah at 12:30, and the
            Ruvelo client call at 4. Nothing back-to-back, so you've got breathing
            room."
            
            The sections below (in <rules>) are operational constraints you follow
            silently — they shape what you do, not how you talk. Never let their
            register (checklists, "NEVER", numbered steps) leak into your replies.
            </persona>
            
            <rules>
            
            <knowledge_section>
            If an operation requires creating knowledge in your Knowledge base:
            - Search for existing similar records using search_knowledge first.
            - If a strongly similar record exists, update it with update_knowledge.
            - If no similar record exists, create one with save_knowledge.
            </knowledge_section>
            
            <email_section>
            EMAIL COMPOSITION RULES:
            
            Information priority when composing an email:
            1. Information explicitly provided by the user in the current conversation.
            2. Information available in the current conversation context.
            3. If required information is missing, search the user's Knowledge base
            with search_knowledge.
            4. If search_knowledge doesn't have it either, DO NOT invent it. Don't
            call send_email — ask the user for the missing information instead.
            5. If the missing information is essential to the user's explicit
            request, ask for it rather than sending an incomplete email.
            
            NEVER use placeholders such as:
            - [your name]
            - [your location]
            - [company name]
            - [recipient name]
            - <name>
            - [insert ...]
            
            Example:
            User: "Send an email introducing me to John and mention where I live."
            If the user's location is unknown:
            - Search Knowledge for it.
            - If found, use it.
            - If not found, don't write "[your location]" — omit the location unless
            it's essential to the request. If essential, ask before sending.
            
            Before calling send_email, confirm the subject and body are complete,
            natural, and contain no unresolved placeholders.
            </email_section>
            
            <calendar_section>
            CURRENT DATE AND TIME: {now.isoformat()}
            CURRENT YEAR: {now.year}
            
            - Use the current date/time above as the reference for all scheduling.
            - Resolve relative dates ("tomorrow", "next Monday", "next week") against
            it.
            - If the user gives a date without a year, infer the year relative to the
            current date.
            - Before creating a calendar event, double-check the resulting date is
            consistent with the current date.
            </calendar_section>
            
            <browser_section>
            When using browser tools:
            - `content` holds the textual information visible on the current page —
            read and use it when answering questions or deciding what to do next.
            - `elements` holds interactive elements you can act on via their IDs.
            - Don't assume information must live in an interactive element; it may
            only exist in `content`.
            - Use `content` to understand the page and `elements` to act on it.
            - After a browser action, inspect the returned page observation before
            choosing the next action.
            </browser_section>
            
            </rules>
        """

    async def emit(
        self,
        event_handler,
        event_type: str,
        data: dict,
    ):
        if event_handler:
            await event_handler(
                AgentEvent(
                    type=event_type,
                    data=data,
                )
            )

    async def execute_tool(self, tool_name: str, arguments: str, call_id: str,event_handler=None):
        tool = next((tool for tool in self.tools if tool.name == tool_name), None)

        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid arguments for tool '{tool_name}': {arguments}"
            ) from e

        # Convert datetime strings to datetime objects based on tool schema
        for param_name, param_value in parsed_arguments.items():
            if param_name in tool.parameters.get("properties", {}):
                param_schema = tool.parameters["properties"][param_name]
                if param_schema.get("format") == "date-time" and isinstance(param_value, str):
                    try:
                        # Parse ISO 8601 datetime string
                        parsed_arguments[param_name] = datetime.fromisoformat(param_value.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        pass  # Keep original value if parsing fails

        await self.emit(
            event_handler=event_handler,
            event_type=AgentEventState.TOOL_STARTED,
            data={
                "tool": tool_name,
                "call_id": call_id,
                "arguments": parsed_arguments
            }
        )

        result = tool.function(**parsed_arguments)
        if hasattr(result, "__await__"):
            result = await result

        await self.emit(
            event_handler=event_handler,
            event_type=AgentEventState.TOOL_EXECUTED,
            data={
                "tool": tool_name,
                "call_id": call_id,
                "result": result
            }
        )

        return result

    def get_openai_tools(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self.tools
        ]
    

    async def run(self, state: AgentState, event_handler=None) -> str:
        
        print("[DEBUG] Agent.run called with state:", state)

        input_messages: list[ChatCompletionMessageParam] = [
            cast(ChatCompletionMessageParam, {
                "role": "system",
                "content": self.get_instructions()
            })
        ]

        input_messages.extend([
            cast(ChatCompletionMessageParam, {
                "role": message.role,
                "content": message.content  })
            for message in state.messages
        ])

        now = datetime.now().astimezone()

        response = await self.client.chat.completions.create(
            model=settings.model,
            messages=input_messages,
            tools=self.get_openai_tools(),
        )

        print("[DEBUG] checking if tool call is present in the response")

        while True:
            tool_calls = [
                tool_call
                for tool_call in response.choices[0].message.tool_calls or []
                if tool_call.type == "function"
            ]

            if not tool_calls:
                return response.choices[0].message.content or ""

            tool_call_payload = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in tool_calls
            ]

            input_messages.append(
                cast(
                    ChatCompletionMessageParam,
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_call_payload,
                    },
                )
            )

            for tool_call in tool_calls:
                result = await self.execute_tool(
                    tool_name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                    call_id=tool_call.id,
                    event_handler=event_handler,
                )

                input_messages.append(
                    cast(
                        ChatCompletionMessageParam,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result),
                        },
                    )
                )

            response = await self.client.chat.completions.create(
                model=settings.model,
                messages=input_messages,
                tools=self.get_openai_tools(),
            )

    async def humanize_for_voice(self, text: str) -> str:
        """Convert text to a more human-friendly format for voice output."""
        prompt = f"""
        Humanize the text in quotes for voice output according to the following rules:
         1. Put the text in a single, natural-sounding paragraph.
         2. Use commas and periods to break up long sentences.
         3. Avoid overly formal or technical language; make it sound conversational.
         4. Remove any unnecessary filler words, phrases or punctuation.

         Text: "{text}"
        """
        response = await self.client.chat.completions.create(
            model=settings.model,
            messages=[
                cast(ChatCompletionMessageParam, {
                    "role": "system",
                    "content": "You are a helpful assistant that humanizes text for voice output."
                }),
                cast(ChatCompletionMessageParam, {
                    "role": "user",
                    "content": prompt
                })
            ]
        )
        return response.choices[0].message.content or ""
def get_agent(tools_registery: ToolsRegistery):
    return Agent(tools_registery=tools_registery)