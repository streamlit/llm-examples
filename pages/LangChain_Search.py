import streamlit as st
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

with st.sidebar:
    serper_api_key = st.text_input('Serper API Key',key='langchain_search_api_key_serper')
    openai_api_key = st.text_input('OpenAI API Key',key='langchain_search_api_key_openai')
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/pages/LangChain_Search.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("🔎 Search with LangChain")
question = st.text_input("What do you want to know?", placeholder="Who won the Women's U.S. Open in 2018?")

if question:
    if not serper_api_key and not openai_api_key:
        st.info("Please add your Serper and OpenAI API keys to continue.")
    elif not serper_api_key:
        st.info("Please add your Serper API key to continue.")
    elif not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif serper_api_key and openai_api_key:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)
#         llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets.openai_api_key)

        search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
#         search = GoogleSerperAPIWrapper(serper_api_key=st.secrets.serper_api_key)

        search_tool = Tool(
            name="Intermediate Answer",
            func=search.run,
            description="useful for when you need to ask with search",
        )
        search_agent = initialize_agent([search_tool], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        response = search_agent.run(question)
        st.write("### Answer")
        st.write(response)
