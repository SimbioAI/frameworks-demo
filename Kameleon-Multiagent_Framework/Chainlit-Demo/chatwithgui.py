from typing import Any, Dict, List
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, AIMessageChunk, ToolMessage
import chainlit as cl
import asyncio
import prompt

# Load environment variables
from dotenv import load_dotenv
load_dotenv("F:\\Social AI\\multiagent-framework\\.venv\\.env")

prompt_template = ChatPromptTemplate([
    ("system", prompt.SALES_AGENT_PROMPT + "{chat_history}"),
    ("human", "{user_message}"),
])
prompt_template

#* Callback
class MyCustomChainAsyncHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""

    async def on_chat_model_start(self, serialized: Dict[str, Any], 
    messages: List[List[BaseMessage]], **kwargs) -> None:
        class_name = serialized["name"]
        print(f"{class_name} model started\n")

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        print(f"LLM model ended, response: {response}\n")

    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        print(f"Chain {serialized["name"]} started\n")

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print(f"Chain ended, outputs: {outputs}\n")

#* Model 
llm = ChatOpenAI(model="gpt-4o-mini", 
                   temperature=0.4,
                   timeout=60,
                   max_retries=3,
                   )
#* Structured Output Pydantic 
class SalesAgentResponse(BaseModel):
    intent: str = Field(description="The intent of the user's message")
    sales_stage: str = Field(description="The current stage of the sales conversation")
    reason : str = Field(description="The reason for the answer")    
    answer: str = Field(description="The answer to the user's question")


llm_with_structure = llm.with_structured_output(SalesAgentResponse)
chain = prompt_template | llm_with_structure

callbacks = [MyCustomChainAsyncHandler()]
chain_with_callbacks = chain.with_config(callbacks=callbacks) # reuse callbacks across multiple chain executions

#----------------------------
# Chat
#----------------------------

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="I'm Kameleon, your AI sales team. How can I help you today?").send()

history = "Chat History: "
@cl.on_message
async def on_message(message):

    global history
    message_content = message.content
    # msg = cl.Message(content="")
    # async for chunk in chain.astream({"chat_history": history, "user_message": message_content}): 
    #     # , config={"callbacks": callbacks} specific for this execution
    #     print(chunk)
    #     await msg.stream_token(token=chunk.content)
    response = await chain.ainvoke({"chat_history": history, "user_message": message_content})
    print(response)
    await cl.Message(content=response.answer).send()
    history += "\n" + "User: " + message_content + "\n" + "Assistant: " + response.answer
    await message.update()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
