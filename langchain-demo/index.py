from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class Country(BaseModel):
    name: str = Field(description="The name of the country")
    capital: str = Field(description="The capital of the country")
    population: int = Field(description="The population of the country")

# Initializations
llm = ChatOpenAI(model="gpt-3.5-turbo")
parser = JsonOutputParser(pydantic_object=Country)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can answer questions. Formatting Instructions: {format_instructions}"),
    ("user", "{input}")
])

# Chain
chain = prompt | llm | parser

response = chain.invoke({"input": "Russia which capital is Moscow has over 120 million people living there", "format_instructions": parser.get_format_instructions()})
print(response)