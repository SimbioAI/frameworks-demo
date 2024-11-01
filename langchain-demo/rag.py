from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain

def getDocumentFromWeb(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    return chunks

def createVectorStore(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings) # in memory vector store for simplicity
    return vector_store

def createChain(vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4) # lower the temperature to make the model more factual and less creative

    prompt = ChatPromptTemplate.from_template(template="""
        Answer the following questions as best you can.
        Context: {context}
        Question: {input}
    """)

    chain = create_stuff_documents_chain(llm, prompt)

    retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # retrieve 3 most relevant documents

    retrieval_chain = create_retrieval_chain(retriever, chain)

    return retrieval_chain


docs = getDocumentFromWeb("https://ethresear.ch/t/local-fee-markets-in-ethereum/20754")
vector_store = createVectorStore(docs)
chain = createChain(vector_store)

response = chain.invoke({"input": "What is this proposal about?"})
print(response)