from typing import List
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_openai import ChatOpenAI

#* Load environment variables
from dotenv import load_dotenv

load_dotenv("F:\\Social AI\\multiagent-framework\\.venv\\.env")

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
@tool
def my_tool(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def my_2_tool(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

tools = [my_tool, my_2_tool]
# Tool binding
model_with_tools = model.bind_tools(tools)

result = model_with_tools.invoke("Hello world!")

result_1 = model_with_tools.invoke("What is 2 times 3?")

result_2 = model_with_tools.invoke("What is 2 plus 3?")