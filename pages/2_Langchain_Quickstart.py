import streamlit as st
from langchain.chat_models import ChatOpenAI
from components.Sidebar import sidebar
from shared import constants
from langchain.schema import (
    HumanMessage,
)

st.title("🦜🔗 Langchain Quickstart App")

api_key, selected_model = sidebar(constants.OPENROUTER_DEFAULT_CHAT_MODEL)

def generate_response(input_text):
    chat = ChatOpenAI(
        temperature=0.7,
        model=selected_model,
        openai_api_key=api_key,
        openai_api_base=constants.OPENROUTER_API_BASE,
        headers={"HTTP-Referer": constants.OPENROUTER_REFERRER},
    )
    resp = chat([HumanMessage(content=input_text)])
    st.write(resp.content)

with st.form("my_form"):
    text = st.text_area(
        "Enter text:", "What are 3 key advice for learning how to code?"
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        generate_response(text)
