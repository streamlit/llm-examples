import streamlit as st
from langchain import OpenAI
from components.Sidebar import sidebar

st.title('🦜🔗 Langchain Quickstart App')

api_key = sidebar()

def generate_response(input_text):
  llm = OpenAI(
    temperature=0.7, 
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    headers={"HTTP-Referer": "https://yourdomain.streamlit.io"}
  )
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are 3 key advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    generate_response(text)

