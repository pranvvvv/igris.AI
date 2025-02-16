import cohere 
from rich import print 
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


COHERE_API_KEY= "Bj8It0LYh5awv9dlmcxOygnnBRzCzLM7kPqfY0cv"

if not COHERE_API_KEY:
    raise Exception("COHERE_API_KEY not found in environment variables")

co = cohere.Client(api_key=COHERE_API_KEY)

funcs = [
    "exit", "general", "realtime", "open", "close", "play", 
    "generate image", "system", "content", "google search", 
    "youtube search", "wikipedia search", "weather", "news",
    "reminder", "timer", "alarm", "schedule", "calendar",
]

# Define the list of commands
commands = [
    "generate image", "system", "content", "google search", 
    "youtube search", "wikipedia search", "weather", "news",
    "reminder", "timer", "alarm", "schedule", "calendar",
]

messages = []

preamble = preamble = """
You are a highly accurate Decision-Making Model designed to classify user queries. Your task is to determine if a query is 'general', 'real-time', or a request for an action (such as opening an app, playing music, or performing a system task).

*** Do not answer the query, only classify it correctly. ***

→ Respond with 'general(query)' if the query can be answered by an LLM model (e.g., a conversational AI chatbot) without requiring real-time data.
→ Respond with 'realtime(query)' if the query requires real-time data (e.g., weather updates, live news, stock prices).
→ Respond with 'open(application name or website name)' if the query is requesting to open an application or website (e.g., 'open Facebook', 'open YouTube').
→ Respond with 'close(application name)' if the query is asking to close an application (e.g., 'close Notepad', 'close Facebook').
→ Respond with 'play(song name)' if the query is requesting to play a specific song (e.g., 'play Shape of You').
→ Respond with 'generate image(image prompt)' if the query is asking to generate an image using a given prompt.
→ Respond with 'system(task name)' if the query is requesting a system task (e.g., mute/unmute, adjust volume, restart the system).
→ Respond with 'content(topic)' if the query is asking to create or edit content (e.g., writing a document, email, or code).
→ Respond with 'google search(topic)' if the query is requesting a Google search.
→ Respond with 'youtube search(topic)' if the query is requesting a YouTube search.
→ If the query involves multiple actions (e.g., 'open Facebook and close WhatsApp'), respond with each action separately.
→ If the user is saying goodbye or ending the conversation (e.g., 'bye Jarvis'), respond with 'exit'.
→ If the query does not fit any category, respond with 'general(query)'.

"""


ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi. "},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi. "},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me. "},
    {"role": "Chatbot", "message": "general chat with me. "}
]

# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):
    # Add the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt} "})

    stream = co.chat_stream(
        model='command-r-plus', # Specify the Cohere model to use.
        message=prompt,
        # Pass the user's query.
        temperature=0.7,
        # Set the creativity level of the model.
        chat_history=ChatHistory,
        # Provide the predefined chat history for context.
        prompt_truncation='OFF', # Ensure the prompt is not truncated.
        connectors=[],
        # No additional connectors are used.
        preamble=preamble # Pass the detailed instruction preamble.
    )
    # Initialize an empty string to store the generated response.
    response = ""
    # Iterate over events in the stream and capture text generation events.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text
    # Append generated text to the response string.

    response = response.replace("\n", " ")
    response = response.split(",")

    response = [i.strip() for i in response]

    temp = []

    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    
    response = temp

    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse # Return the clarified response.
    else:
        return response # Return the filtered response.

# Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>> "))) # Print the categorized response.
