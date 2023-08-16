import openai
import streamlit as st

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from sqlalchemy import create_engine

from langchain import OpenAI
import os 
os.environ['OPENAI_API_KEY'] = "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"
engine = create_engine("postgresql://admin:MyUsmc17WODNVrSLDR3pvwW8YxyYGc@ap-south-1.2a29422e-bfef-4efd-8334-9f94f0a7e904.aws.ybdb.io:5433/yugabyte") 
db = SQLDatabase(engine=engine)
llm = OpenAI(temperature=0)
print("hi")
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
print("hello")


print("hello2")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    Yugabyte_database_url = st.text_input("Yugabyte Database URL", key="chatbot_db_url")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not Yugabyte_database_url:
        st.info("Please add your Yugabyte database URL to continue.")
        st.stop()
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    
    

    openai.api_key = openai_api_key
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.session_state.messages.append(msg.content)
    res = db_chain.run(prompt)
    

