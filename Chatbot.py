import os

import streamlit as st
from openai import OpenAI

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE", "https://api.openai.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
with st.sidebar:
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by LLM Gateway")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=st.session_state.messages,
        extra_headers={"X-TFY-METADATA": '{"tfy_log_request":"true"}'},
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
