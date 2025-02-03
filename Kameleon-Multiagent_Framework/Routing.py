from typing import List, Annotated, TypedDict, Literal, Any, Sequence
from pydantic import BaseModel, Field
import operator
from typing_extensions import TypedDict
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from IPython.display import Image, display
import time
import asyncio

#* Load environment variables
from dotenv import load_dotenv    
load_dotenv("..\\.venv\\.env")

memory = MemorySaver()

#! initatiate the conversation
#! events may not be sent in case he rejected cookies
#! mem0 and Inmemorysaver

#* Load Chat Model
llm = ChatOpenAI(model="gpt-4o-mini", 
                   temperature=0.4,
                   timeout=60,
                   max_retries=3,
                   )

# Schema for structured output to use as routing logic
class Route(BaseModel):
    step: Literal["understanding_agent", "product_agent", "sales_agent"] = Field(
        None, description="The next step in the routing process"
    )

# Augment the LLM with schema for structured output
router = llm.with_structured_output(Route)


# State
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intermediate_output : AnyMessage
    decision: str


# Nodes
async def route_conversation(state: State):
    """Start with a user message or behavioral events"""

    if state["messages"] is None:
        return "understanding_agent"
    else:
        return "intent_agent_router"

async def understanding_agent(state: State): #!story
    """Handles Event messages and understands customers"""

    result = await llm.ainvoke(state["messages"])
    return {"intermediate_output": result}


async def product_agent(state: State):#! joke
    """Handles everything related to the ecommerce products"""

    result = await llm.ainvoke(state["messages"])
    # (return product id)
    return {"intermediate_output": result}


async def sales_agent(state: State):#! poem
    """Main chatbot. Direct contact with the user"""
    result = ""
    print(state['decision'])
    if state['decision'] == 'product_agent':
        result = await llm.ainvoke(state["messages"] + [state['intermediate_output']])
    elif state['decision'] == 'understanding_agent':
        result = await llm.ainvoke(state["messages"] + [state['intermediate_output']])
    else:
        result = await llm.ainvoke(state["messages"])

    return {"messages": [result]}


async def intent_agent_router(state: State):
    """Route the input to the appropriate node"""

    # Run the augmented LLM with structured output to serve as routing logic
    prompt = prompt_template.invoke(state["messages"])
    decision = await router.ainvoke(prompt)

    return {"decision": decision.step}


# Conditional edge function to route to the appropriate node
async def route_decision(state: State):
    # Return the node name you want to visit next
    print(state["decision"])
    if state["decision"] == "understanding_agent":
        return "understanding_agent"
    elif state["decision"] == "product_agent":
        return "product_agent"
    elif state["decision"] == "sales_agent":
        state['current_agent'] = 'sales_agent'
        return "sales_agent"


# Build workflow
router_builder = StateGraph(State)

# Add nodes
router_builder.add_node("understanding_agent", understanding_agent)
router_builder.add_node("product_agent", product_agent)
router_builder.add_node("sales_agent", sales_agent)
router_builder.add_node("intent_agent_router", intent_agent_router)

# Add edges to connect nodes
router_builder.add_conditional_edges(
    START, 
    route_conversation, 
    {  # Name returned by route_decision : Name of next node to visit
        "understanding_agent": "understanding_agent",
        "intent_agent_router": "intent_agent_router",
    },
    )
router_builder.add_conditional_edges(
    "intent_agent_router",
    route_decision,
    {  # Name returned by route_decision : Name of next node to visit
        "understanding_agent": "understanding_agent",
        "product_agent": "product_agent",
        "sales_agent": "sales_agent",
    },
)
router_builder.add_edge("understanding_agent", "sales_agent")
router_builder.add_edge("product_agent", "sales_agent")
router_builder.add_edge("sales_agent", END)

# Compile workflow
router_workflow = router_builder.compile(checkpointer=memory)

# Show the workflow
# try:
#     display(Image(router_workflow.get_graph().draw_mermaid_png()))
# except Exception as e:
#     print(f"Unable to display workflow graph in non-notebook environment. Error{e}")

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Route the user input message to story, joke, or poem based on the user's request. "
            "If uncertainty is detected, let the understanding_agent ask clarifying questions directly to the user."
            "First explain your reasoning, then provide your selection.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

async def arun_workflow():
    print("Welcome to KameleonAI! \n Enter x or l to stop.")
    events = ""


    while True:
        user_input = input("User: ")
        if user_input.lower() in ["x", "l"]:
            print("Goodbye!")
            break
        a = time.time()
        config = {"configurable": {"thread_id": "abc123"}}
        state = await router_workflow.ainvoke({"messages": [HumanMessage(content=user_input)]}, config)
        print("Time-Elapsed", time.time()-a)
        for message in state["messages"]:
            message.pretty_print()



async def astream_workflow_events():
    config = {"configurable": {"thread_id": "abc123"}}
    async for event in router_workflow.astream_events({"messages": [HumanMessage(content="tell me one joke")]}, config, version='v2'):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end=" |")
        elif kind == "on_tool_start":
            print("--")
            print(
                f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
            )
        elif kind == "on_tool_end":
            print(f"Done tool: {event['name']}")
            print(f"Tool output was: {event['data'].get('output')}")
            print("--")

async def main():
    # Run the main workflow
    await arun_workflow()
    
    # Uncomment to also run the streaming events
    # await astream_workflow_events()

if __name__ == "__main__":
    asyncio.run(main())