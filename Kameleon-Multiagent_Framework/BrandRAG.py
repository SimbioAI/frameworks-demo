from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import numpy as np
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import InMemoryVectorStore

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