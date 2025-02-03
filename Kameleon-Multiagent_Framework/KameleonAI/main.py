from graph import router_workflow
import time
import asyncio
from langchain_core.messages import HumanMessage

#* Load environment variables
from dotenv import load_dotenv  
load_dotenv("F:\\Social AI\\multiagent-framework\\.venv\\.env")

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