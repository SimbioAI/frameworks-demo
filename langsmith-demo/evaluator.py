from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from langsmith import traceable, wrappers, Client as langClient
from openai import Client


#####  EVALUATOR #####

openai = wrappers.wrap_openai(Client())
client = langClient()

@traceable
def label_text(text):
    messages = [
        {
            "role": "system",
            "content": "Please review the user query below and determine if it contains any form of toxic behavior, such as insults, threats, or highly negative comments. Respond with 'Toxic' if it does, and 'Not toxic' if it doesn't.",
        },
        {"role": "user", "content": text},
    ]
    result = openai.chat.completions.create(
        messages=messages, model="gpt-4o-mini", temperature=0
    )
    return result.choices[0].message.content

examples = client.list_examples(dataset_id="c9ace0d8-a82c-4b6c-13d2-83401d68e9ab")

def correct_label(root_run: Run, example: Example) -> dict:
  score = root_run.outputs.get("output") == example.outputs.get("label")
  return {"score": int(score), "key": "correct_label"}



dataset_name = "Toxic Queries"

results = evaluate(
    lambda inputs: label_text(inputs["text"]),
    data=dataset_name,
    evaluators=[correct_label],
    experiment_prefix="Toxic Queries",
    description="Testing the baseline system.",  # optional
)