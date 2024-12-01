from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_core.runnables import chain
from operator import attrgetter
from typing_extensions import Annotated
from copy import deepcopy
from pydantic import BaseModel, Field


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)

# Model has the option to call tools
model_with_tools = model.bind_tools([multiply])

result = model_with_tools.invoke("What is 5 times 7?")

print(multiply.invoke(result.tool_calls[0]))


### OR we can use a chain to do the same thing ###

tmpChain = model_with_tools | attrgetter("tool_calls") | multiply.map()

print(tmpChain.invoke("What is 5 times 7?"))


### Example of injecting runtime arguments ###

@tool
def multiply_with_user_id(a: int, b: int, user_id: Annotated[str, InjectedToolArg]) -> int:
    """Multiply two numbers and return the result."""
    return a * b + int(user_id)

@chain
def inject_user_id(ai_msg):
    tool_calls = []
    for tool_call in ai_msg.tool_calls:
        tool_call_copy = deepcopy(tool_call)
        tool_call_copy["args"]["user_id"] = "123"
        tool_calls.append(tool_call_copy)
    return tool_calls

@chain
def tool_router(tool_call):
    return tool_map[tool_call["name"]]


tools = [multiply_with_user_id]

model_with_tools = model.bind_tools(tools)

tool_map = {tool.name: tool for tool in tools}

chain = model_with_tools | inject_user_id | tool_router.map()

print(chain.invoke("What is 5 times 7?"))


### Example of structuring the tools ###

# 1. we can parse the docstring to get the tool name and args by @tool(parse_docstring=True)
# 2. we can use Annotated[str, "description of the argument"] to explain the argument
# 3. we can use pydantic class for the inputs using as example @tool("multiplication-tool", args_schema=CalculatorInput, return_direct=True)

# 4. we can also use StructuredTool with pydantic for more complex inputs and better configurability like below

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def _handle_error(error: ToolException) -> str:
    return f"The following errors occurred during tool execution: `{error.args[0]}`"

calculator_tool = StructuredTool.from_function(
    func=add,
    name="calculator",
    description="useful for adding two numbers",
    args_schema=CalculatorInput,
    return_direct=True,
    handle_tool_error=_handle_error,
)

print(calculator_tool.invoke({"a": 5, "b": 7}))