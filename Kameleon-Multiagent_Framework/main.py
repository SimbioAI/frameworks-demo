from typing import List, Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

#* Load environment variables
from dotenv import load_dotenv, find_dotenv    
load_dotenv(find_dotenv())

#* Load Chat Model
model = ChatOpenAI(model="gpt-4o-mini", 
                   temperature=0.4,
                   timeout=60,
                   max_retries=3,
                   )

#* Structured Output Pydantic 
class ResponseFormatter(BaseModel):
    answer: List[str] = Field(description="The answer to the user's question")
    followup_question: str = Field(description="A followup question the user could ask")

model_with_structure = model.with_structured_output(ResponseFormatter)
# response.json()


#* Tool creation
# can add chain to inject tool argument without the llm knowing about it
@tool
def multiply(a: Annotated[int,"first number"], b: Annotated[int,"second number"]) -> int:
    """
    Multiply two numbers.
    """
    return a * b

class AddInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

def add(a: int, b: int) -> int:
    return a + b

def _handle_error(error: ToolException) -> str:
    return f"The following errors occurred during tool execution: `{error.args[0]}`"

add = StructuredTool.from_function(
    func=add,
    name="add",
    description="Add two numbers.",
    args_schema=AddInput,
    return_direct=True,
    handle_tool_error=_handle_error,
)

tools = [multiply, add]
tools_map = {tool.name.lower(): tool for tool in tools}
# Tool binding
model_with_tools = model.bind_tools(tools)

result = model_with_tools.invoke("Hello world!")

messages = [HumanMessage(content="What is 2 plus 3? What is 2 times 3?")]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)
for tool_call in ai_message.tool_calls:
    selected_tool = tools_map[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

model_with_tools.invoke(messages)