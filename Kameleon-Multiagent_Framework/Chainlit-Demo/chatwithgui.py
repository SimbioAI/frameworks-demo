from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import chainlit as cl

# Load environment variables
from dotenv import load_dotenv

load_dotenv("F:\\Social AI\\multiagent-framework\\.venv\\.env")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
system = """You are a helpful assistant! Provide clear and concise responses to user queries, offering guidance and 
    support in any situation."""


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Hey buddy, what's up?").send()


history = ""


@cl.on_message
async def on_message(message):
    global history
    message_content = message.content
    result = model.invoke(
        [SystemMessage(content=history)] + [HumanMessage(content=message_content)]
    )

    history += "User: " + message_content + "\n" + "Assistant: " + result.content + "\n"
    print(history)
    await cl.Message(content=result.content).send()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
