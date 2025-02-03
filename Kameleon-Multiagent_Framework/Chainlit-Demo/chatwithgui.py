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

# Load environment variables
from dotenv import load_dotenv
load_dotenv("F:\\Social AI\\multiagent-framework\\.venv\\.env")

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

prompt_template = ChatPromptTemplate([
    ("system", "You are a helpful assistant! Provide clear and concise responses to user queries, "
    "offering guidance and support in any situation. "
    "{chat_history}"),
    ("human", "{user_message}"),
])

chain = prompt_template | llm

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
    msg = cl.Message(content="")
    global history
    message_content = message.content
    async for chunk in chain_with_callbacks.astream({"chat_history": history, "user_message": message_content}): 
        # , config={"callbacks": callbacks} specific for this execution
        await msg.stream_token(token=chunk.content)
    history += "\n" + "User: " + message_content + "\n" + "Assistant: " + msg.content
    await msg.update()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
