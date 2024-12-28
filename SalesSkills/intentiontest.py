from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv
import json
from openai import OpenAI

# import re
import pandas as pd
from difflib import SequenceMatcher

load_dotenv()
client = OpenAI()


class Intent(str, Enum):
    FIND_ATTRACTION = "FindAttraction"
    FIND_RESTAURANTS = "FindRestaurants"
    FIND_MOVIE = "FindMovie"
    LOOK_UP_MUSIC = "LookUpMusic"
    SEARCH_HOTEL = "SearchHotel"
    FIND_EVENTS = "FindEvents"


class Thought(Enum):
    NIMPINT = "The user did not implicitly mention any potential intent, I should continue the chit-chat."
    IMPINT = "The user implicitly mentioned the intent of {intent}. I should smoothly pivot the conversation to the topic of {intent}"
    NOCHANGEINT = (
        "The user did not change the topic of {intent}. I should continue the topic."
    )
    EXPINT = "The user has explicitly shown his/her intent of {intent}."


class cot(BaseModel):
    intent: Intent
    thought: Thought = Field(description="Your thought on the intent of the customer.")
    response: str = Field(
        description="The final response that will be send to the customer."
    )


format = {
    "type": "json_schema",
    "json_schema": {
        "name": "cot",
        "schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "FindAttraction",
                        "FindRestaurants",
                        "FindMovie",
                        "LookUpMusic",
                        "SearchHotel",
                        "FindEvents",
                    ],
                    "description": "The intent of the customer.",
                },
                "thought": {
                    "type": "string",
                    "enum": [
                        "The user implicitly mentioned the intent of {intent}. I should smoothly pivot the conversation to the topic of {intent}.",
                        "The user did not change the topic of {intent}. I should continue the topic.",
                        "The user has explicitly shown his/her intent of {intent}."
                        "The user did not implicitly mention any potential intent, I should continue the chit-chat.",
                    ],
                    "description": "Your thought on the intent of the customer.",
                },
                "response": {
                    "type": "string",
                    "description": "The final response that will be sent to the customer.",
                },
            },
            "required": ["intent", "thought", "response"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}

# system_prompt = "Think carefully to determine the potential intent in the Dialog history between a user and an agent and provide suitable response."

# with open("test_CoT.json", "r") as f:
#     data = json.load(f)
# len(data)
# item = data[6]
# # Extract the middle number from id using regex
# match = re.search(r"merge_(\d+)_", item["id"])
# if match:
#     custom_id = match.group(1)

#     # Extract dialog history from the conversation
#     dialog_text = item["conversations"][0]["value"]
#     # Remove the intent list and format instruction from the dialog
#     user_content = dialog_text.split("Here is a list of")[0].strip()

# completion = client.beta.chat.completions.parse(
#     model="gpt-4o",
#     response_format=format,
#     messages=[
#         {
#             "role": "system",
#             "content": system_prompt,
#         },
#         {"role": "user", "content": user_content},
#     ],
# )
# # .parsed in case of pydantic
# reply = completion.choices[0].message.content


# def replace_intent_in_thought(response_data):
#     # add .value to access the enum in pydantic case
#     thought_template = (
#         "Thought: "
#         + response_data["thought"]
#         + "\nResponse: "
#         + response_data["response"]
#     )
#     thought_with_intent = thought_template.format(
#         intent=response_data["intent"]
#     )  # Replace {intent}
#     return thought_with_intent


# Replace intent in both examples
# reply.model_dump() in case of pydantic
# updated_response_data = replace_intent_in_thought(json.loads(reply))

# ----------------------------------------------------------------
# * Create batch file
# ----------------------------------------------------------------


def create_jsonl_from_dataset(input_file, output_file):
    # Read the input JSON file
    with open(input_file, "r") as f:
        data = json.load(f)

    # Define the system content
    system_content = (
        "Think carefully to determine the potential intent in the Dialog history "
        "between a user and an agent and provide suitable response."
    )

    # Process each conversation and write to JSONL
    with open(output_file, "w") as f:
        for item in data[-100:]:  # get the last 100 conversations out of 27208
            # Extract dialog history from the conversation
            dialog_text = item["conversations"][0]["value"]
            # Remove the intent list and format instruction from the dialog
            user_content = dialog_text.split("Here is a list of")[0].strip()

            # Create the output format
            output = {
                "custom_id": item["id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "response_format": format,
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": user_content},
                    ],
                    "max_tokens": 1000,
                },
            }

            # Write to JSONL format (one JSON object per line)
            f.write(json.dumps(output) + "\n")


# Example usage
input_file = "train_CoT.json"
output_file = "batch1.jsonl"
create_jsonl_from_dataset(input_file, output_file)
create_jsonl_from_dataset("test_CoT.json", "batch2.jsonl")

# ----------------------------------------------------------------
# * Uploading Your Batch Input File
# ----------------------------------------------------------------

batch_input_file = client.files.create(file=open("batch2.jsonl", "rb"), purpose="batch")

print(batch_input_file)
# file1 id: file-XgCE8WEhe6rM5qW8r4nzMv
# file2 id: file-6wSrhQCnpLZHxNRg2PR473

# ----------------------------------------------------------------
# * Creating the batch request
# ----------------------------------------------------------------

batch_input_file_id = batch_input_file.id
batch = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={"description": "intent analysis 2"},
)

# * Checking the status of the batch
batch_status = client.batches.retrieve("batch_676f249a142c81909657ca9ce908d06e")
# batch id: batch_676f249a142c81909657ca9ce908d06e
# batch 2 id: batch_676f255e0b2c81908ca62d32bb9481fa
print(batch_status.status)

client.batches.list(limit=10)

# ----------------------------------------------------------------
# * Retrieving the Results
# ----------------------------------------------------------------

# output file id 1: file-1Y9DcqF4raqzTPc2odW1Zq
# output file id 2: file-JMLMXL7wrtSWoe883edpVC
file_response = client.files.content("file-1Y9DcqF4raqzTPc2odW1Zq")

with open("response1.jsonl", "w") as f:
    f.write(file_response.content.decode("utf-8"))

comparison_df_1 = pd.read_json("response1.jsonl", lines=True)
comparison_df_2 = pd.read_json("response2.jsonl", lines=True)


def replace_intent_in_thought(response_data):
    response_data = json.loads(
        response_data["body"]["choices"][0]["message"]["content"]
    )
    # add .value to access the enum in pydantic case
    thought_template = (
        "Thought: "
        + response_data["thought"]
        + "\nResponse: "
        + response_data["response"]
    )
    thought_with_intent = thought_template.format(
        intent=response_data["intent"]
    )  # Replace {intent}
    return thought_with_intent


comparison_df_1["response"] = comparison_df_1["response"].apply(
    replace_intent_in_thought
)
comparison_df_1 = comparison_df_1.drop(columns=["id", "error"]).rename(
    columns={"custom_id": "id"}
)
comparison_df_2["response"] = comparison_df_2["response"].apply(
    replace_intent_in_thought
)
comparison_df_2 = comparison_df_2.drop(columns=["id", "error"]).rename(
    columns={"custom_id": "id"}
)


def get_response_from_df(df):
    return df.loc[df.index[-1], "conversations"][1]["value"]


train_Evaluation = (
    pd.read_json("train_CoT.json")
    .iloc[-100:]
    .groupby("id", sort=False)
    .apply(get_response_from_df)
    .to_frame("target_response")
    .reset_index()
    .merge(comparison_df_1, on="id", how="inner")
)
test_Evaluation = (
    pd.read_json("test_CoT.json")
    .iloc[-100:]
    .groupby("id", sort=False)
    .apply(get_response_from_df)
    .to_frame("target_response")
    .reset_index()
    .merge(comparison_df_2, on="id", how="inner")
)


def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Add similarity column
train_Evaluation["similarity"] = train_Evaluation.apply(
    lambda row: calculate_similarity(row["target_response"], row["response"]), axis=1
)
test_Evaluation["similarity"] = test_Evaluation.apply(
    lambda row: calculate_similarity(row["target_response"], row["response"]), axis=1
)

# Add a comparison column to check if they are "similar enough" (e.g., threshold = 0.8)
similarity_threshold = 0.5
train_Evaluation["is_similar"] = train_Evaluation["similarity"] >= similarity_threshold
test_Evaluation["is_similar"] = test_Evaluation["similarity"] >= similarity_threshold
train_Evaluation["is_similar"].sum()
test_Evaluation["is_similar"].sum()
