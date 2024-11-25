from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o", temperature=0)


##### Enable Tracing Dynamically #####

tracer = LangChainTracer()

model.invoke("What is the capital of France?", config={"callbacks": [tracer]})

# LangChain Python also supports a context manager for tracing a specific block of code.
from langchain_core.tracers.context import tracing_v2_enabled
with tracing_v2_enabled():
  model.invoke("What is the capital of Germany?")

# This will NOT be traced (assuming LANGCHAIN_TRACING_V2 is not set)
model.invoke("What is the capital of Syria?")


##### Add Metadata, Tags & Run Name to Traces #####

model = ChatOpenAI(model="gpt-4o", temperature=0).with_config({"tags": ["model-tag"], "metadata": {"model-key": "model-value"}, "run_name": "MyCustomModel"})

with tracing_v2_enabled():
  try:
    model.invoke("What is the meaning of life?", {"tags": ["invoke-tag"], "metadata": {"invoke-key": "invoke-value", "run_name": "MyCustomChain"}})
  finally:
    wait_for_all_tracers()

@traceable(
    tags=["openai", "chat"],
    metadata={"foo": "bar"}
)
def invoke_runnnable(question):
    model.invoke(question)

invoke_runnnable("How much does a Porsche 911 cost?")


##### Distribute Tracing #####
# https://docs.smith.langchain.com/observability/how_to_guides/tracing/trace_with_langchain#distributed-tracing-with-langchain-python

