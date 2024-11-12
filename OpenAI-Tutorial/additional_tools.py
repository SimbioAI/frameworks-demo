# --------------------------------------------------------------
# Reasoning models: Explore advanced reasoning and problem-solving
# models using o1-preview and o1-mini. The o1 models are currently
# in beta with limited features as of 12-Nov-2024.
# --------------------------------------------------------------


# --------------------------------------------------------------
# Batch API (12-Nov-2024)
# --------------------------------------------------------------
# * Batch API to send asynchronous groups of requests with 50% lower
# * costs, a separate pool of significantly higher rate limits, and
# * a clear 24-hour turnaround time. Mainly used for:
# * 1. running evaluations
# * 2. classifying large datasets
# * 3. embedding content repositories (RAG)
# * For now, the available endpoints are /v1/chat/completions
# * (Chat Completions API) and /v1/embeddings (Embeddings API).


# --------------------------------------------------------------
# Predicted Outputs
# --------------------------------------------------------------

# * Predicted Outputs are particularly useful for regenerating text documents
# * and code files with small modifications. It speed up API responses from
# * Chat Completions when many of the output tokens are known ahead of time.

from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()

code = """
class User {
  firstName: string = "";
  lastName: string = "";
  username: string = "";
}

export default User;
"""

refactor_prompt = """
Replace the "username" property with an "email" property. Respond only 
with code, and with no markdown formatting.
"""

start_time = time.time()

# * use prediction request parameter in Chat Completions
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": refactor_prompt},
        {"role": "user", "content": code},
    ],
    prediction={"type": "content", "content": code},
    stream=True,
    # * The latency gains of Predicted Outputs are even greater when you
    # * use streaming for API responses.
)

end_time = time.time()

execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
# with prediction and stream: Execution time: 0.8894791603088379 seconds
# without prediction and stream: Execution time: 2.185335636138916 seconds

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

# ! Check the OpenAI API documentation for more information on limitations
