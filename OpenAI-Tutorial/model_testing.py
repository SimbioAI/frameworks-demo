from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# --------------------------------------------------------------
# Test and improve model outputs through evaluations.
# --------------------------------------------------------------

# * Check OpenAI dashboard to create and run evals on test datasets.
# * If your model is tested with data that's not representative of the
# * types of requests it's going to get, you can't be confident in how
# * it will perform on new, unknown inputs.


# * Representative test datasets can be generated using real production
# * requests from users.
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a corporate IT support expert."},
        {"role": "user", "content": "How can I hide the dock on my Mac?"},
    ],
    # * Completions are stored for 30 days.
    store=True,
    # * Used later to filter your completions
    metadata={"role": "manager", "department": "accounting", "source": "homepage"},
)

print(response.choices[0])

#! Check Stored Completions in Dashboard. The content should be
#! moderated to check whether text or images are potentially harmful.

response = client.moderations.create(
    model="omni-moderation-latest",
    input=[
        {
            "type": "text",
            "text": "I feel it's time to hurt Madison Johns and her family.",
        },
        # {
        #     "type": "image_url",
        #     "image_url": {
        #         "url": "https://example.com/image.png",
        #         # can also use base64 encoded image URLs
        #         # "url": "data:image/jpeg;base64,abcdefg..."
        #     }
        # },
    ],
)

print(response.results[0].model_dump_json(indent=2))
{
    "categories": {
        "harassment": True,
        "harassment_threatening": True,
        "hate": False,
        "hate_threatening": False,
        "illicit": False,
        "illicit_violent": False,
        "self_harm": False,
        "self_harm_instructions": False,
        "self_harm_intent": False,
        "sexual": False,
        "sexual_minors": False,
        "violence": True,
        "violence_graphic": False,
        "harassment/threatening": True,
        "hate/threatening": False,
        "illicit/violent": False,
        "self-harm/intent": False,
        "self-harm/instructions": False,
        "self-harm": False,
        "sexual/minors": False,
        "violence/graphic": False,
    },
    "category_scores": {
        "harassment": 0.4021429298797443,
        "harassment_threatening": 0.5482329695029127,
        "hate": 0.013662113102918563,
        "hate_threatening": 0.005447216605964923,
        "illicit": 0.16775325250257275,
        "illicit_violent": 0.08939618417883125,
        "self_harm": 0.0005006106934840828,
        "self_harm_instructions": 0.00022011622820665742,
        "self_harm_intent": 0.00024050606249465073,
        "sexual": 0.0007545114546835822,
        "sexual_minors": 0.000023782205064034188,
        "violence": 0.8669971029081931,
        "violence_graphic": 0.0023907288913721705,
        "harassment/threatening": 0.5482329695029127,
        "hate/threatening": 0.005447216605964923,
        "illicit/violent": 0.08939618417883125,
        "self-harm/intent": 0.00024050606249465073,
        "self-harm/instructions": 0.00022011622820665742,
        "self-harm": 0.0005006106934840828,
        "sexual/minors": 0.000023782205064034188,
        "violence/graphic": 0.0023907288913721705,
    },
    "flagged": True,
}

# * There are a number of evaluation criteria to choose from (sometimes
# * called graders) - these tests will help assess the quality of your
# * model responses. One flexible option is a model grader, which you
# * can prompt to grade model outputs as you see fit.

# --------------------------------------------------------------
# Finetuning or Distillation on the Dashboard
# --------------------------------------------------------------

# * Fine-tuning lets you get more out of the models available through the
# * API by providing:
# * 1. Higher quality results than prompting
# *      I. Correcting failures to follow complex prompts
# *      II. Handling many edge cases in specific ways
# * 2. Ability to train on more examples than can fit in a prompt
# *      I. Performing a new skill or task that’s hard to articulate in a prompt
# * 3. Token savings due to shorter prompts (eliminate "few-shot learning")
# * 4. Lower latency requests
# * 5. Setting the style, tone, format, or other qualitative aspects

# * Can finetune structured output and function calling! Including a long list
# * of tools in the completions API can consume a considerable number of prompt
# * tokens and sometimes the model hallucinates or does not provide valid JSON output.

#! We typically see best results when using a good prompt in the fine-tuning
#! data (or combining prompt chaining / tool use with fine-tuning)
#! Check cookbook for more details on validation.

# * 1. Evaluate the stored completions with both the large and the small
# *     model to establish a baseline.
# * 2. Select the stored completions that you'd like to use from the more complex
# *      model to for distillation and use them to fine-tune the smaller model
# * 3. Evaluate the performance.
# * Note: A few hundred samples might be sufficient, but sometimes a
# * more diverse range of thousands of samples can yield better results.
