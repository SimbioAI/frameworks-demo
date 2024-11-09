# --------------------------------------------------------------
# Import Modules
# --------------------------------------------------------------

import os
import json
import openai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage


# --------------------------------------------------------------
# Load OpenAI API Token From the .env File
# --------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------------------
# Ask ChatGPT a Question
# --------------------------------------------------------------

completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "When's the next flight from Amsterdam to New York?",
        },
    ],
    max_tokens=150,  # Max number of tokens (words/punctuation)
    temperature=0.7,  # Controls randomness; higher = more random
    top_p=0.9,  # Nucleus sampling: only consider the top 90% of probability mass
    frequency_penalty=0.5,  # Discourages repeated words/phrases
    presence_penalty=0.3,  # Encourages new topic introduction
)

output = completion.choices[0].message.content
print(output)

############ Use OpenAI’s Function Calling Feature ############

# --------------------------------------------------------------
# 1. Add a Function that you want the model to be able to call
# --------------------------------------------------------------


def get_flight_info(loc_origin, loc_destination):
    """
    Get flight information between two locations.
    """

    # Example output returned from an API or database
    flight_info = {
        "loc_origin": loc_origin,
        "loc_destination": loc_destination,
        "datetime": str(datetime.now() + timedelta(hours=2)),
        "airline": "KLM",
        "flight": "KL643",
    }

    return json.dumps(flight_info)


# --------------------------------------------------------------
# 2. Describe your function to the model so it knows how to call it
# --------------------------------------------------------------

function_description = [
    {
        "name": "get_flight_info",
        "description": "Get flight information between two locations",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_origin": {
                    "type": "string",
                    "description": "The departure airport, e.g. DUS",
                },
                "loc_destination": {
                    "type": "string",
                    "description": "The destination airport, e.g. HAM",
                },
            },
            "required": ["loc_origin", "loc_destination"],
            "additionalProperties": False,
        },
    }
]

# --------------------------------------------------------------
# 3. Your application calls the API with your prompt and
# definitions of the functions the LLM can call
# --------------------------------------------------------------

user_prompt = "When's the next flight from Amsterdam to New York?"

completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_prompt}],
    # Add function calling
    functions=function_description,
    function_call="auto",  # the model can pick between generating a message or calling a function
)

# --------------------------------------------------------------
# The API responds to your application specifying the function to
# be called and the arguments to call it with. If the model does not
# generate a function call, then the response will contain a direct
# reply to the user in the normal way that Chat Completions does.
# Note: the function existance is not required!
# --------------------------------------------------------------

output = completion.choices[0].message
print(output)
# ChatCompletionMessage(content=None, refusal=None, role='assistant',
# audio=None, function_call=FunctionCall(arguments='{"loc_origin":"AMS",
# "loc_destination":"JFK"}', name='get_flight_info'), tool_calls=None)


# --------------------------------------------------------------
# 4. Your application executes the function with the given arguments
# --------------------------------------------------------------

# The json.loads function converts the json string to a Python object
origin = json.loads(output.function_call.arguments).get("loc_origin")
destination = json.loads(output.function_call.arguments).get("loc_destination")
params = json.loads(output.function_call.arguments)
type(params)

print(origin)
print(destination)
print(params)
# {'loc_origin': 'AMS', 'loc_destination': 'JFK'}

chosen_function = eval(output.function_call.name)
flight = chosen_function(**params)

print(flight)
# {"loc_origin": "AMS", "loc_destination": "JFK", "datetime": "2024-11-09 21:27:57.352038",
# "airline": "KLM", "flight": "KL643"}

# --------------------------------------------------------------
# 5. Your application calls the API providing your prompt and
# the result of the function call your code just executed
# --------------------------------------------------------------

# The key is to add the function output back to the messages with role: function
second_completion = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": user_prompt},
        {"role": "function", "name": output.function_call.name, "content": flight},
    ],
    functions=function_description,
    function_call="auto",
)
response = second_completion.choices[0].message.content
print(response)


# --------------------------------------------------------------
# Include Multiple Functions
# --------------------------------------------------------------

# Expand on function descriptions (3 functions)

function_descriptions_multiple = [
    {
        "name": "get_flight_info",
        "description": "Get flight information between two locations",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_origin": {
                    "type": "string",
                    "description": "The departure airport, e.g. DUS",
                },
                "loc_destination": {
                    "type": "string",
                    "description": "The destination airport, e.g. HAM",
                },
            },
            "required": ["loc_origin", "loc_destination"],
        },
    },
    {
        "name": "book_flight",
        "description": "Book a flight based on flight information",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_origin": {
                    "type": "string",
                    "description": "The departure airport, e.g. DUS",
                },
                "loc_destination": {
                    "type": "string",
                    "description": "The destination airport, e.g. HAM",
                },
                "datetime": {
                    "type": "string",
                    "description": "The date and time of the flight, e.g. 2023-01-01 01:01",
                },
                "airline": {
                    "type": "string",
                    "description": "The service airline, e.g. Lufthansa",
                },
            },
            "required": ["loc_origin", "loc_destination", "datetime", "airline"],
        },
    },
    {
        "name": "file_complaint",
        "description": "File a complaint as a customer",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the user, e.g. John Doe",
                },
                "email": {
                    "type": "string",
                    "description": "The email address of the user, e.g. john@doe.com",
                },
                "text": {
                    "type": "string",
                    "description": "Description of issue",
                },
            },
            "required": ["name", "email", "text"],
        },
    },
]

print(function_descriptions_multiple)


def ask_and_reply(prompt):
    """Give LLM a given prompt and get an answer."""

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        # add function calling
        functions=function_descriptions_multiple,
        function_call="auto",  # specify the function call
    )

    output = completion.choices[0].message
    return output


# Scenario 1: Check flight details

user_prompt = "When's the next flight from Amsterdam to New York?"
print(ask_and_reply(user_prompt))

# Get info for the next prompt

origin = json.loads(output.function_call.arguments).get("loc_origin")
destination = json.loads(output.function_call.arguments).get("loc_destination")
chosen_function = eval(output.function_call.name)
flight = chosen_function(origin, destination)

print(origin)
print(destination)
print(flight)

flight_datetime = json.loads(flight).get("datetime")
flight_airline = json.loads(flight).get("airline")

print(flight_datetime)
print(flight_airline)

# Scenario 2: Book a new flight

user_prompt = f"I want to book a flight from {origin} to {destination} on {flight_datetime} with {flight_airline}"
print(ask_and_reply(user_prompt))

# Scenario 3: File a complaint

user_prompt = "This is John Doe. I want to file a complaint about my missed flight. It was an unpleasant surprise. Email me a copy of the complaint to john@doe.com."
print(ask_and_reply(user_prompt))

# --------------------------------------------------------------
# Make It Conversational With Langchain
# --------------------------------------------------------------

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Start a conversation with multiple requests

user_prompt = """
This is Jane Harris. I am an unhappy customer that wants you to do several things.
First, I neeed to know when's the next flight from Amsterdam to New York.
Please proceed to book that flight for me.
Also, I want to file a complaint about my missed flight. It was an unpleasant surprise. 
Email me a copy of the complaint to jane@harris.com.
Please give me a confirmation after all of these are done.
"""

# Returns the function of the first request (get_flight_info)

first_response = llm.predict_messages(
    [HumanMessage(content=user_prompt)], functions=function_descriptions_multiple
)

print(first_response)

# Returns the function of the second request (book_flight)
# It takes all the arguments from the prompt but not the returned information

second_response = llm.predict_messages(
    [
        HumanMessage(content=user_prompt),
        AIMessage(content=str(first_response.additional_kwargs)),
        AIMessage(
            role="function",
            additional_kwargs={
                "name": first_response.additional_kwargs["function_call"]["name"]
            },
            content=f"Completed function {first_response.additional_kwargs['function_call']['name']}",
        ),
    ],
    functions=function_descriptions_multiple,
)

print(second_response)

# Returns the function of the third request (file_complaint)

third_response = llm.predict_messages(
    [
        HumanMessage(content=user_prompt),
        AIMessage(content=str(first_response.additional_kwargs)),
        AIMessage(content=str(second_response.additional_kwargs)),
        AIMessage(
            role="function",
            additional_kwargs={
                "name": second_response.additional_kwargs["function_call"]["name"]
            },
            content=f"Completed function {second_response.additional_kwargs['function_call']['name']}",
        ),
    ],
    functions=function_descriptions_multiple,
)

print(third_response)

# Conversational reply at the end of requests

fourth_response = llm.predict_messages(
    [
        HumanMessage(content=user_prompt),
        AIMessage(content=str(first_response.additional_kwargs)),
        AIMessage(content=str(second_response.additional_kwargs)),
        AIMessage(content=str(third_response.additional_kwargs)),
        AIMessage(
            role="function",
            additional_kwargs={
                "name": third_response.additional_kwargs["function_call"]["name"]
            },
            content=f"Completed function {third_response.additional_kwargs['function_call']['name']}",
        ),
    ],
    functions=function_descriptions_multiple,
)

print(fourth_response)
