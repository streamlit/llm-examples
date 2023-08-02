import openai
import streamlit as st
from litellm import completion
import os

with st.sidebar:
    
    model = st.selectbox(
    'Model',
    ('gpt-3.5-turbo', 'gpt-4', 'command-nightly', 'text-davinci-003', 'claude-2', 'claude-instant-v1'))
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    os.environ["OPENAI_API_KEY"] = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    os.environ['COHERE_API_KEY'] = st.text_input("Cohere API Key", key="cohere_api_key", type="password")
    os.environ['ANTHROPIC_API_KEY'] = st.text_input("Anthropic API Key", key="anthropic_api_key", type="password")
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not os.environ["OPENAI_API_KEY"]:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = completion(model=model, messages=st.session_state.messages)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant").write(msg.content)
