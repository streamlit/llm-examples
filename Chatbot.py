from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.schema import Document
from langchain_community.llms import Ollama

import streamlit as st

with st.sidebar:
    st.text_input("choose version")

#    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
#    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
#    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
#    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 AIA Chatbot")
st.caption("🚀 AIA 課程查詢機器人")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

llm = Ollama(model="llama3", base_url="http://3ece-140-109-17-42.ngrok-free.app")

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = llm.invoke(st.session_state.messages)
    #msg = response.choices[0].message.content
    msg = response
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
