import streamlit as st
from langchain import OpenAI
from components.Sidebar import sidebar
from shared import constants

st.title('🦜🔗 Langchain Quickstart App')

api_key = sidebar()

def generate_response(input_text):
  llm = OpenAI(
    temperature=0.7, 
    openai_api_key=api_key,
    openai_api_base=constants.OPENROUTER_API_BASE,
    headers={"HTTP-Referer": constants.OPENROUTER_REFERER}
  )
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    generate_response(text)

