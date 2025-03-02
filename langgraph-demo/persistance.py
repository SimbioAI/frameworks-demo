from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict
from typing import Annotated
import uuid

memory = MemorySaver()
model = ChatOpenAI(model="gpt-4o-mini")

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
# input_message = {"type": "user", "content": "hi! I'm bob"}
# for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
#     chunk["messages"][-1].pretty_print()

# input_message = {"type": "user", "content": "what's my name?"}
# for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
#     chunk["messages"][-1].pretty_print()



##### CROSS THREAD PERSISTANCE #####
def call_model(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("memories", user_id)
    memories = store.search(namespace)
    info = "\n".join([d.value["data"] for d in memories])
    system_msg = f"You are a helpful assistant talking to the user. User info: {info}"

    # Store new memories if the user asks the model to remember
    last_message = state["messages"][-1]
    if "remember" in last_message.content.lower():
        memory = "User name is Bob"
        store.put(namespace, str(uuid.uuid4()), {"data": memory})

    response = model.invoke(
        [{"type": "system", "content": system_msg}] + state["messages"]
    )
    return {"messages": response}

in_memory_store = InMemoryStore()

builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")

graph = builder.compile(checkpointer=MemorySaver(), store=in_memory_store)

config = {"configurable": {"thread_id": "1", "user_id": "1"}}
input_message = {"type": "user", "content": "Hi! Remember: my name is Bob"}
for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

config = {"configurable": {"thread_id": "2", "user_id": "1"}}
input_message = {"type": "user", "content": "what is my name?"}
for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

for memory in in_memory_store.search(("memories", "1")):
    print(memory.value)