from langsmith.evaluation import evaluate_comparative
from langchain import hub
from langchain_openai import ChatOpenAI
from langsmith.schemas import Run, Example
prompt = hub.pull("langchain-ai/pairwise-evaluation-2")

def evaluate_pairwise(runs: list[Run], example: Example):
    scores = {}
    
    # Create the model to run your evaluator
    model = ChatOpenAI(model_name="gpt-4")
    
    runnable = prompt | model
    response = runnable.invoke({
        "question": example.inputs["question"],
        "answer_a": runs[0].outputs["output"] if runs[0].outputs is not None else "N/A",
        "answer_b": runs[1].outputs["output"] if runs[1].outputs is not None else "N/A",
    })
    score = response["Preference"]
    if score == 1:
        scores[runs[0].id] = 1
        scores[runs[1].id] = 0
    elif score == 2:
        scores[runs[0].id] = 0
        scores[runs[1].id] = 1
    else:
        scores[runs[0].id] = 0
        scores[runs[1].id] = 0
    return {"key": "ranked_preference", "scores": scores}
    
    
evaluate_comparative(
    # Replace the following array with the names or IDs of your experiments
    ["e4b92827-a42a-418d-8368-a3ed36e467a3"],
    evaluators=[evaluate_pairwise],
)