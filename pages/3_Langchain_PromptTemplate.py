import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from components.Sidebar import sidebar
from shared import constants
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)


st.title("🦜🔗 Langchain - Blog Outline Generator App")

api_key, selected_model = sidebar(constants.OPENROUTER_DEFAULT_INSTRUCT_MODEL)

def blog_outline(topic):
    # Instantiate LLM model
    chat = ChatOpenAI(
        model_name=selected_model,
        openai_api_key=api_key,
        openai_api_base=constants.OPENROUTER_API_BASE,
        headers={"HTTP-Referer": constants.OPENROUTER_REFERRER},
    )
    # Prompt
    template="As an experienced data scientist and technical writer, generate an outline for a blog about {topic}."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt])
    prompt = chat_prompt.format_prompt(topic=topic).to_messages()
    st.write(chat(prompt))

with st.form("myform"):
    topic_text = st.text_input("Enter prompt:", "")
    submitted = st.form_submit_button("Submit")
    if submitted:
        blog_outline(topic_text)
