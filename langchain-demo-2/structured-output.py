from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Note: we could include the schema in the prompt and ask nicely to use it but it is not recommended

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: str = Field(description="The answer to the user's question")
    followup_question: str = Field(description="A followup question the user could ask")


# we could also use model_kwargs={ "response_format": { "type": "json_object" } } to return the response in a json object (it returns a string so we need to parse it)
model = ChatOpenAI(model="gpt-4o", temperature=0)

model_with_tools = model.bind_tools([ResponseFormatter])

print(model_with_tools.invoke("What is the capital of France?").tool_calls[0])



### OR we could use langchain's helper functions ###

model_with_structure = model.with_structured_output(ResponseFormatter)

structured_output = model_with_structure.invoke("What is the powerhouse of the cell?")

print(structured_output)