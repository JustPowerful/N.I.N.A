# this file defines the structure of the tools
# it provides the right description for the agent to execute the right tool
from dataclasses import dataclass
from typing import Callable

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    function: Callable