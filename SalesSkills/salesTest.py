from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

gpt_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

system = """You are a helpful assistant that generates multiple sub-questions related to an input question. \n
The goal is to break down the input into a set of sub-problems / sub-questions that can be answers in isolation. \n"""

question = """What are the main components of an LLM-powered autonomous agent system?"""
questions = gpt_llm.invoke(
    [SystemMessage(content=system)] + [HumanMessage(content=question)]
)
