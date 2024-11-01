from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader

def getDocumentFromWeb(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4) # lower the temperature to make the model more factual and less creative

prompt = ChatPromptTemplate.from_template(template="""
    Answer the following questions as best you can.
    Context: {context}
    Question: {input}
""")

chain = prompt | llm

response = chain.invoke({"input": "What is this proposal about?", "context": getDocumentFromWeb("https://ethresear.ch/t/local-fee-markets-in-ethereum/20754")})
print(response)