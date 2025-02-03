from datetime import datetime, timezone
from typing import Dict, List, Literal, cast
from IPython.display import Image, display

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from configuration import Sales_Agent_Configuration, Understanding_Agent_Configuration, \
Intent_Router_Configuration, Product_Agent_Configuration, Configuration
from state import InputState, State
from tools import TOOLS, Route
from utils import load_chat_model
import prompts

#! initatiate the conversation
#! events may not be sent in case he rejected cookies
#! mem0 and Inmemorysaver

    # """Call the LLM powering our "agent".

    # This function prepares the prompt, initializes the model, and processes the response.

    # Args:
    #     state (State): The current state of the conversation.
    #     config (RunnableConfig): Configuration for the model run.

    # Returns:
    #     dict: A dictionary containing the model's response message.
    # """                  

# Nodes
async def route_conversation(state: State) -> str:
    """Start with a user message or behavioral events"""

    if state["messages"] is None:
        return "understanding_agent"
    else:
        return "intent_agent_router"

async def understanding_agent(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Handles Event messages and understands customers"""

    configuration = Understanding_Agent_Configuration.from_runnable_config(config)

    # Initialize the model. Change the model or add more tools here.
    llm = load_chat_model(configuration)

    # Format the system prompt. Customize this to change the agent's behavior.
    print("Events", state["events"])
    system_message = configuration.system_prompt.format(
        EVENTS=state["events"] or "",
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_message}, *state["messages"]], config
        ),
    )
    # (return product id)
    return {"intermediate_output": response}


async def product_agent(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Handles everything related to the ecommerce products"""
    configuration = Product_Agent_Configuration.from_runnable_config(config)

    # Initialize the model. Change the model or add more tools here.
    llm = load_chat_model(configuration)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        time=datetime.now(tz=timezone.utc).isoformat()
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_message}, *state["messages"]], config
        ),
    )
    # (return product id)
    return {"intermediate_output": response}


async def sales_agent(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Main chatbot. Direct contact with the user"""

    configuration = Sales_Agent_Configuration.from_runnable_config(config)

    # Initialize the model. Change the model or add more tools here.
    llm = load_chat_model(configuration)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        COMPANY_NAME=prompts.COMPANY_NAME,
        COMPANY_DESCRIPTION=prompts.COMPANY_DESCRIPTION
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await llm.ainvoke(
            [{"role": "system", "content": system_message}, *state["messages"] + 
            ([state['intermediate_output']] if state['decision'] == 'sales_agent' else [])], config
        ),
    )
    return {"messages": [response]}


async def intent_agent_router(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Route the input to the appropriate node"""
    configuration = Intent_Router_Configuration.from_runnable_config(config)

    # Initialize the model. Change the model or add more tools here.
    llm = load_chat_model(configuration)
    # Run the augmented LLM with structured output to serve as routing logic
    router = llm.with_structured_output(Route)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        COMPANY_NAME=prompts.COMPANY_NAME,
    )
    
    # Get the model's decision
    decision = cast(
        AIMessage,
        await router.ainvoke(
            [{"role": "system", "content": system_message}, *state["messages"]], config
        ),
    )

    return {"decision": decision.step}


# Conditional edge function to route to the appropriate node
async def route_decision(state: State) -> Route:
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
router_builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Add nodes
router_builder.add_node("understanding_agent", understanding_agent)
router_builder.add_node("product_agent", product_agent)
router_builder.add_node("sales_agent", sales_agent)
router_builder.add_node("intent_agent_router", intent_agent_router)
# router_builder.add_node("tools", ToolNode(TOOLS))

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

# Add memory
memory = MemorySaver()

# Compile the builder into an executable graph
# You can customize this by adding interrupt points for state updates
router_workflow = router_builder.compile(
    checkpointer=memory,
    interrupt_before=[],  # Add node names here to update state before they're called
    interrupt_after=[],  # Add node names here to update state after they're called
)

router_workflow.name = "KameleonAI Sales Team"  # This customizes the name in LangSmith

# Show the workflow
# try:
#     display(Image(router_workflow.get_graph().draw_mermaid_png()))
# except Exception as e:
#     print(f"Unable to display workflow graph in non-notebook environment. Error{e}")
