from openai import OpenAI
import shelve
from dotenv import load_dotenv

# import time
import prompt

load_dotenv()
client = OpenAI()


# --------------------------------------------------------------
# Upload file
# --------------------------------------------------------------
def upload_file(path):
    # Upload a file with an "assistants" purpose
    return client.files.create(file=open(path, "rb"), purpose="assistants")


products = upload_file("../Sales-Assistant/products.json")
faq_support = upload_file("../Sales-Assistant/FAQ-Support.txt")
files = [products.id, faq_support.id]

# --------------------------------------------------------------
# Vector store
# --------------------------------------------------------------
vector_store = client.beta.vector_stores.create(
    name="FAQ-Support",
    chunking_strategy={
        "type": "static",
        "static": {
            "max_chunk_size_tokens": 600,  # must be between 100 and 4096
            "chunk_overlap_tokens": 300,  # must not exceed half of max_chunk_size_tokens
        },
    },
    # * Save costs: first GB is free and beyond that, usage is billed at $0.10/GB/day of vector storage.
    expires_after={"anchor": "last_active_at", "days": 7},
)
# You can add several files to a vector store by creating batches of up to 500 files.
vector_store_file = client.beta.vector_stores.files.create_and_poll(
    vector_store_id=vector_store.id,
    file_id=faq_support.id,
    # * The chunking_strategy can be per file instead of per vector store
)
# Ensuring vector store readiness before creating runs
print(vector_store_file.status)


# --------------------------------------------------------------
# Create assistant
# --------------------------------------------------------------
def create_assistant(files, vector_store):
    assistant = client.beta.assistants.create(
        model="gpt-4o-mini",
        name="Sales Assistant",
        temperature=0.2,
        instructions=prompt.prompt,
        # *  Code Interpreter, File Search, and Function calling
        tools=[
            {
                "type": "file_search",
                "file_search": {
                    "max_num_results": 5,  # Adjust this to control the maximum number of search results, between 1 and 50
                    "ranking_options": {
                        "ranker": "auto",  # Specify a ranker name if you want to override the default
                        "score_threshold": 0.5,  # Set the score threshold between 0 and 1; only results meeting this threshold will be shown
                    },
                },
            },
            {
                "type": "code_interpreter"
            },  # Code Interpreter is charged at $0.03 per session active by default for one hour.
            # ,{"type": "function", "function": {...}}
        ],
        # Files and vector stores that are passed at the Assistant level are accessible by all Runs with this Assistant
        tool_resources=[
            {"file_search": {"vector_store_ids": [vector_store.id]}},
            {"code_interpreter": {"file_ids": [files[0]]}},
        ],
    )
    return assistant


sales_assistant = create_assistant(files, vector_store)


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------
# * Thread is a conversation session between an Assistant and a user.


# * shelve works by creating a key-value byte storage file where each key is a string,
# * and the corresponding value can be any serializable Python object (such as lists,
# * dictionaries, or even custom objects).
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
# * As part of a Run (invocation of an Assistant on a Thread), the Assistant
# * appends Messages to the Thread and uses its configuration and the Thread’s
# * Messages to perform tasks by calling models and tools. Examining Run Steps
# * allows you to introspect how the Assistant is getting to its final results.
def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_7Wx2nQwoPWSf710jrdWTDlfE")

    #! can stream the response
    # * By default, a Run will use the model and tools configuration specified in Assistant object.
    # * but you can override most of these when creating the Run for added flexibility.
    # Run the assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        additional_instructions=f"Please address the user as {name}. The user has a premium account.",
        # tools = ,
        # max_prompt_tokens =,
        # max_completion_tokens =,
        # truncation_strategy=
    )

    # TODO: Check Documentation!
    # * For function calling: the run will enter a requires_action state which indicates that you need
    # * to run tools and submit their outputs to the Assistant to continue Run execution.

    citations = []
    # Wait for completion
    if run.status != "completed":
        # # Be nice to the API
        # time.sleep(0.5)
        # run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        # print("Run status: ", run.status)

        # Retrieve the Messages
        messages = list(client.beta.threads.messages.list(thread_id=thread.id))
        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")
        # print(message_content.value)
        # print("\n".join(citations))
    else:
        print(run.status)

    run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id, run_id=run.id)
    print(run_steps)

    run_step = client.beta.threads.runs.steps.retrieve(
        thread_id=thread.id,
        run_id=run.id,
        step_id=run_steps[0].id,
        # * Inspecting file search chunks
        include=["step_details.tool_calls[*].file_search.results[*].content"],
    )
    print(run_step)

    return message_content.value + "\nCitations:" + "\n".join(citations)


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create(
            # * You can attach vector stores to your Thread that have a default expiration policy of 7 days after they were last active
            # tool_resources=[{
            #         "file_search": {
            #         "vector_store_ids": ["vs_2"]
            #       }
            #   }
        )
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
        # *  Can attach files to the thread message: default expiration policy of 7 days after they were last active
        #           "attachments": [
        #     { "file_id": message_file.id, "tools": [{"type": "code_interpreter"}] }
        #   ],
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread, name)
    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Test assistant
# --------------------------------------------------------------

new_message = generate_response("What's the check in time?", "123", "John")

new_message = generate_response("What's the pin for the lockbox?", "456", "Farah")

new_message = generate_response("What was my previous question?", "123", "John")

user_name = input("Hello, what's your name?: ")
while True:
    user_prompt = input("Write exit to stop the loop. Ask the agent: ")
    if user_prompt == "exit":
        break
    else:
        generate_response(user_prompt, "100", user_name)
