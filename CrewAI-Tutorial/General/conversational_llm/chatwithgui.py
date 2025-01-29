from crewai import Process
from langchain_openai import ChatOpenAI

# Warning control
import warnings
import chainlit as cl
import yaml
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# Load environment variables
import os
from dotenv import load_dotenv

load_dotenv(r"F:\Social AI\multiagent-framework\.venv\.env")
warnings.filterwarnings("ignore")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"

# Define file paths for YAML configurations
files = {"agents": "config/agents.yaml", "tasks": "config/tasks.yaml"}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, "r") as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs["agents"]
tasks_config = configs["tasks"]

# internet_research_assistant_agent = Agent(
#     config=agents_config["internet_research_assistant_agent"],
#     tools=[SerperDevTool()],
# )

offline_knowledge_assistant_agent = Agent(
    config=agents_config["offline_knowledge_assistant_agent"],
)

# conduct_online_research = Task(
#     config=tasks_config["conduct_online_research"],
#     agent=internet_research_assistant_agent,
# )

# generate_knowledge_based_response = Task(
#     config=tasks_config["generate_knowledge_based_response"],
#     agent=offline_knowledge_assistant_agent,
# )

helful_assistant_agent = Agent(
    config=agents_config["helful_assistant_agent"],
)

helpful_response = Task(
    config=tasks_config["helpful_response"],
    agent=helful_assistant_agent,
)

# Define the crew with agents and tasks
user_assisstant_crew = Crew(
    agents=[  # internet_research_assistant_agent,
        # offline_knowledge_assistant_agent
        helful_assistant_agent
    ],
    tasks=[  # conduct_online_research,
        # generate_knowledge_based_response
        helpful_response
    ],
    # manager_llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.2),
    # process=Process.hierarchical,
    verbose=True,
    memory=True,
)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Hey buddy, what's up?").send()


@cl.on_message
async def on_message(message):
    message_content = message.content
    result = user_assisstant_crew.kickoff({"topic": message_content})
    await cl.Message(content=result.raw).send()


@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")


@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")
