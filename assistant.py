import os
from openai import OpenAI, AssistantEventHandler

# Fetch the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

# Create an Assistant
assistant = client.beta.assistants.create(
    name="General AI Assistant",
    instructions="You are an AI assistant that can answer any questions.",
    model="gpt-4-turbo-preview",  # Adjust this as necessary
)

# Define the EventHandler class
class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nAssistant > ", end="", flush=True)
      
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
      
    def on_tool_call_created(self, tool_call):
        print(f"\nAssistant > {tool_call.type}\n", flush=True)
  
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\nOutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

# Main interaction loop
if __name__ == "__main__":
    print("AI Assistant activated. Ask me anything (type 'exit' to stop): ")
    while True:
        user_input = input("You > ")
        if user_input.lower() == 'exit':
            print("Assistant > Exiting. Have a great day!")
            break
        
        # Create a new thread for each interaction
        thread = client.beta.threads.create()
        
        # Add the user's question as a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Use the create_and_stream method to get the assistant's response
        with client.beta.threads.runs.create_and_stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="You are an AI assistant that can answer any questions.",
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

