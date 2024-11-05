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
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever

def getDocumentFromWeb(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return chunks

def createVectorStore(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings) # in memory vector store for simplicity
    return vector_store

def createChain(vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4) # lower the temperature to make the model more factual and less creative

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's question based on the context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])

    chain = create_stuff_documents_chain(llm, prompt)

    vector_store_retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # retrieve 3 most relevant documents

    history_aware_retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get more information relevant to the conversation.")
    ])
                                                                      
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=vector_store_retriever,
        prompt=history_aware_retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(history_aware_retriever, chain) # create retrieval chain and pass the documents directly to the chain

    return retrieval_chain

def processChat(chain, question, chat_history):
    response = chain.invoke({"input": question, "chat_history": chat_history})
    return response['answer']

if __name__ == "__main__":
    chunks = getDocumentFromWeb("https://ethresear.ch/t/local-fee-markets-in-ethereum/20754")
    vector_store = createVectorStore(chunks)
    chain = createChain(vector_store)

    chat_history = []

    while True:
        userInput = input("You: ")
        if userInput.lower() == "exit":
            break
        
        response = processChat(chain, userInput, chat_history)
        chat_history.append(HumanMessage(content=userInput))
        chat_history.append(AIMessage(content=response))
        print("Assistant:", response)
