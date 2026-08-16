from openai import AsyncOpenAI
from app.agent.state import AgentState
from app.config import settings
from openai.types.responses import ResponseInputParam
from app.agent.tools.registery import ToolsRegistery
import json

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

    async def execute_tool(self, tool_name: str, arguments: str):
        tool = next((tool for tool in self.tools if tool.name == tool_name), None)

        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        try:
            parsed_arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid arguments for tool '{tool_name}': {arguments}"
            ) from e

        result = tool.function(**parsed_arguments)
        if hasattr(result, "__await__"):
            result = await result

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
    

    async def run(self, state: AgentState) -> str:
        print("[DEBUG] Agent.run called with state:", state)
        input_messages: ResponseInputParam = [
            {
                "role": message.role,
                "content": message.content
            } for message in state.messages
        ]

        response = await self.client.responses.create(
            model=settings.model,
            tools=self.get_openai_tools(),
            instructions="""
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
                                    arguments=tool_call.arguments
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