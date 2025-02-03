from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import numpy as np
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import InMemoryVectorStore
from typing import List, Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolArg, StructuredTool, ToolException
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

#* Load environment variables
from dotenv import load_dotenv, find_dotenv    
load_dotenv(find_dotenv())

#* Load Chat Model
model = ChatOpenAI(model="gpt-4o-mini", 
                   temperature=0.4,
                   timeout=60,
                   max_retries=3,
                   )

#* Structured Output Pydantic 
class ResponseFormatter(BaseModel):
    answer: List[str] = Field(description="The answer to the user's question")
    followup_question: str = Field(description="A followup question the user could ask")

model_with_structure = model.with_structured_output(ResponseFormatter)
# response.json()


#* Tool creation
# can add chain to inject tool argument without the llm knowing about it
@tool
def multiply(a: Annotated[int,"first number"], b: Annotated[int,"second number"]) -> int:
    """
    Multiply two numbers.
    """
    return a * b

class AddInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

def add(a: int, b: int) -> int:
    return a + b

def _handle_error(error: ToolException) -> str:
    return f"The following errors occurred during tool execution: `{error.args[0]}`"

add = StructuredTool.from_function(
    func=add,
    name="add",
    description="Add two numbers.",
    args_schema=AddInput,
    return_direct=True,
    handle_tool_error=_handle_error,
)

tools = [multiply, add]
tools_map = {tool.name.lower(): tool for tool in tools}
# Tool binding
model_with_tools = model.bind_tools(tools)

result = model_with_tools.invoke("Hello world!")

messages = [HumanMessage(content="What is 2 plus 3? What is 2 times 3?")]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)
for tool_call in ai_message.tool_calls:
    selected_tool = tools_map[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

model_with_tools.invoke(messages)


#* Vector Store
vector_store = InMemoryVectorStore(embedding=OpenAIEmbeddings())

document_1 = Document(
    page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

documents = [document_1, document_2]

vector_store.add_documents(documents=documents, ids=["doc1", "doc2"])

query = "my query"
docs = vector_store.similarity_search(query, k=3, filter={"source": "tweet"})
# or 
vs_retriever = vector_store.as_retriever()
docs = vs_retriever.invoke(query)

# Initialize the ensemble retriever
ensemble_retriever = EnsembleRetriever(
    # lexical retriever or graph db
    retrievers=[BM25Retriever(), vs_retriever], weights=[0.5, 0.5]
)

#* Text Splitters
document =     [
        "Hi there!",
        "Oh, hello!",
        "What's your name?",
        "My friends call me World",
        "Hello World!"
    ]

# split based on hierarchical units such as paragraphs, sentences, and words
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, chunk_overlap=0
)
texts = text_splitter.split_text(document)

# HTML, Markdown, or JSON files

# Semantic Meaning Splitting is based on a sliding window approach to generate embeddings, 
# and compare the embeddings to find significant differences

#* Embeddings Model
embeddings_model = OpenAIEmbeddings()
doc_embeddings = embeddings_model.embed_documents(texts)

query_embedding = embeddings_model.embed_query("What is the meaning of life?")

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

similarity = cosine_similarity(query_embedding, doc_embeddings)
print("Cosine Similarity:", similarity)