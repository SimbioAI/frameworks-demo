from langsmith import traceable, unit
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o", temperature=0)


@traceable
def sayHi():
    return model.invoke("Say Hi")

@unit
def test_says_hi():
    response = sayHi()
    # LangSmith logs any exception raised by `assert` / `pytest.fail` / `raise` / etc.
    # as a test failure
    assert response == "Hi"

test_says_hi()