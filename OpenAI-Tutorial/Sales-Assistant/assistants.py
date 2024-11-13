from openai import OpenAI
import shelve
from dotenv import load_dotenv
import time
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
# Create assistant
# --------------------------------------------------------------
def create_assistant(files):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="Sales Assistant",
        instructions=prompt.prompt,
        # *  Code Interpreter, File Search, and Function calling
        tools=[{"type": "retrieval"}, {"type": "code_interpreter"}],
        model="gpt-4o-mini",
        file_ids=files,
    )
    return assistant


sales_assistant = create_assistant(files)


# --------------------------------------------------------------
# Thread management
# --------------------------------------------------------------

# *Thread is a conversation session between an Assistant and a user.


def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# --------------------------------------------------------------
# Generate response
# --------------------------------------------------------------
def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread)
    print(f"To {name}:", new_message)
    return new_message


# --------------------------------------------------------------
# Run assistant
# --------------------------------------------------------------
# * As part of a Run (invocation of an Assistant on a Thread), the Assistant
# * appends Messages to the Thread and uses its configuration and the Thread’s
# * Messages to perform tasks by calling models and tools. Examining Run Steps
# * allows you to introspect how the Assistant is getting to its final results.
def run_assistant(thread):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve("asst_7Wx2nQwoPWSf710jrdWTDlfE")

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    return new_message


# --------------------------------------------------------------
# Test assistant
# --------------------------------------------------------------

new_message = generate_response("What's the check in time?", "123", "John")

new_message = generate_response("What's the pin for the lockbox?", "456", "Sarah")

new_message = generate_response("What was my previous question?", "123", "John")

new_message = generate_response("What was my previous question?", "456", "Sarah")
