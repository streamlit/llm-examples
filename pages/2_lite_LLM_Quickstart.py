import streamlit as st
import threading
import os
from litellm import completion
from dotenv import load_dotenv

# load .env, so litellm reads from .env
load_dotenv()

# Function to get model outputs
def get_model_output(prompt, model_name):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    response = completion(messages=messages, model=model_name)
    
    return response['choices'][0]['message']['content']

# Function to get model outputs
def get_model_output_thread(prompt, model_name, outputs, idx):
    output = get_model_output(prompt, model_name)
    outputs[idx] = output

# Streamlit app

st.title("liteLLM API Playground - use 50+ LLM Models")
st.markdown("[Powered by liteLLM - one package for Anthropic, Cohere, OpenAI, Replicate](https://github.com/BerriAI/litellm/)")

# Sidebar for user input
with st.sidebar:
    st.header("User Settings")
    anthropic_api_key = st.text_input("Enter your Anthropic API key:", type="password")
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")
    set_keys_button = st.button("Set API Keys")

if set_keys_button:
    if anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    st.success("API keys have been set.")

# User Input section
with st.sidebar:
    st.header("User Input")
    prompt = st.text_area("Enter your prompt here:")
    submit_button = st.button("Submit")

# Main content area to display model outputs
st.header("Model Outputs")

# List of models to test
model_names = ["claude-instant-1.2", "claude-2", "gpt-3.5-turbo", "gpt-4", ]  # Add your model names here

cols = st.columns(len(model_names))  # Create columns
outputs = [""] * len(model_names)  # Initialize outputs list with empty strings

threads = []

if submit_button and prompt:
    for idx, model_name in enumerate(model_names):
        thread = threading.Thread(target=get_model_output_thread, args=(prompt, model_name, outputs, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Display text areas and fill with outputs if available
for idx, model_name in enumerate(model_names):
    with cols[idx]:
        st.text_area(label=f"{model_name}", value=outputs[idx], height=300, key=f"output_{model_name}_{idx}")  # Use a unique key

