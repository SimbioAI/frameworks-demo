from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.tools import TavilySearchResults
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Setup Retriever
loader = WebBaseLoader("https://eth2book.info/capella/part4/history/")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(chunks, embeddings) # in memory vector store for simplicity
vector_store_retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # retrieve 3 most relevant documents

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant called Max"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

search_tool = TavilySearchResults()
retrieval_tool = create_retriever_tool(vector_store_retriever, "ethereum_upgrades_search", "Use this tool when searching for information about Ethereum upgrades history")
tools = [search_tool, retrieval_tool]

agent = create_openai_tools_agent(llm=llm, prompt=prompt, tools=tools)

agentExecutor = AgentExecutor(agent=agent, tools=tools)

def processChat(agentExecutor, userInput, chat_history):
    response = agentExecutor.invoke({"input": userInput, "chat_history": chat_history})
    return response['output']

if __name__ == "__main__":
    chat_history = []

    while True:
        userInput = input("You: ")
        if userInput.lower() == "exit":
            break
        
        response = processChat(agentExecutor, userInput, chat_history)
        chat_history.append(HumanMessage(content=userInput))
        chat_history.append(AIMessage(content=response))
        print("Assistant:", response)
