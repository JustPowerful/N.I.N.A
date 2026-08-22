from openai import AsyncOpenAI
from app.agent.state import AgentState, AgentEvent, AgentEventState
from app.config import settings
from openai.types.responses import ResponseInputParam

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
        self.instructions = """
            You are NINA, a personal AI assistant.

            Your job is to help the user accomplish tasks,
            answer questions, and interact with available tools.

            Be concise and useful.
            """,

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
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        }
        for tool in self.tools
        ]
    

    async def run(self, state: AgentState, event_handler=None) -> str:
        
        print("[DEBUG] Agent.run called with state:", state)
        input_messages: ResponseInputParam = [
            {
                "role": message.role,
                "content": message.content
            } for message in state.messages
        ]

        now = datetime.now().astimezone()

        response = await self.client.responses.create(
            model=settings.model,
            tools=self.get_openai_tools(),
            instructions=f"""
            You are NINA, a personal AI assistant.

            Your job is to help the user accomplish tasks,
            answer questions, and interact with available tools.

            You have to follow the following rules sections:

            [Knowledge Section]
            If an operation requires creating knowledge in your Knowledge base:
            - Search for existing similar records in using search_knowledge tool first
            - If a strongly similar record exists update it using update_knowledge tool
            - If there's no similar record create a new one using the save_knowledge tool

            Be concise and useful.

            [Email Section]
            EMAIL COMPOSITION RULES:

            When composing an email, use the following information priority:

            1. Information explicitly provided by the user in the current conversation.
            2. Information available in the current conversation context.
            3. If required information is not available, use the `search_knowledge` tool to search the user's Knowledge base.
            4. If `search_knowledge` does not contain the requested information, DO NOT invent it. Don't run the `send_email` and instead ask the user for the missing information.
            5. If the missing information is essential to fulfilling the user's explicit request, ask the user for it instead of sending an incomplete email.

            NEVER use placeholders such as:
            - [your name]
            - [your location]
            - [company name]
            - [recipient name]
            - <name>
            - [insert ...]

            For example:

            User: "Send an email introducing me to John and mention where I live."

            If the user's location is not known:
            - Search Knowledge for the user's location.
            - If found, use it.
            - If not found, DO NOT write "[your location]".
            - Instead, omit the location from the email unless the location is essential to the user's request. If it is essential, ask the user for their location before sending.

            Before calling `send_email`, ensure that the subject and body are complete, natural, and contain no unresolved placeholders.

            [Calendar Section]
            CURRENT DATE AND TIME: 
            {now.isoformat()}

            CURRENT YEAR:
            {now}

            IMPORTANT DATE RULES:
            - The current date and time is provided above. Use it as a reference for scheduling and date-related tasks.
            - When the user says "tomorrow", "next Monday", "next week", etc., resolve the date relative to the CURRENT DATE AND TIME above.
            - When the user gives a date without a year, use the year that is appropriate relative to the current date.
            - Before creating a calendar event, verify that the resulting date is consistent with the current date.
            """,
            input=input_messages
        )

        

        print("[DEBUG] checking if tool call is present in the response")

        while True:
            tool_calls = [
                item
                for item in response.output 
                if item.type == "function_call"
            ]

            if not tool_calls:
                return response.output_text

            for tool_call in tool_calls:

                input_messages.append({
                    "type": "function_call",
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                })

                result = await self.execute_tool(
                                    tool_name=tool_call.name,
                                    arguments=tool_call.arguments,
                                    call_id=tool_call.call_id,
                                    event_handler=event_handler
                                )

                input_messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result),
                })

                response = await self.client.responses.create(
                    model=settings.model,
                    tools=self.get_openai_tools(),
                    instructions="""
                    You are NINA, a personal AI assistant.

                    Your job is to help the user accomplish tasks,
                    answer questions, and interact with available tools.

                    Be concise and useful.
                    """,
                    input=input_messages
                )

def get_agent(tools_registery: ToolsRegistery):
    return Agent(tools_registery=tools_registery)