from langsmith import Client

client = Client()

#####  GET DATASET FROM RUNS  #####

# dataset_name = "Dataset from runs"

# runs = client.list_runs(
#   project_name="demo",
#   is_root=True,
#   error=False,
# )

# dataset = client.create_dataset(dataset_name, description="An example dataset")

# inputs = [run.inputs for run in runs]
# outputs = [run.outputs for run in runs]

# client.create_examples(
#   inputs=inputs,
#   outputs=outputs,
#   dataset_id=dataset.id,
# )

#####  OR CREATE A NEW DATASET  #####

# Create a dataset
examples = [
    ("Shut up, idiot", "Toxic"),
    ("You're a wonderful person", "Not toxic"),
    ("This is the worst thing ever", "Toxic"),
    ("I had a great day today", "Not toxic"),
    ("Nobody likes you", "Toxic"),
    ("This is unacceptable. I want to speak to the manager.", "Not toxic"),
]

dataset_name = "Toxic Queries"
dataset = client.create_dataset(dataset_name=dataset_name)
inputs, outputs = zip(
    *[({"text": text}, {"label": label}) for text, label in examples]
)
client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)