import streamlit as st
from langchain.llms import OpenAI
from langchain import PromptTemplate
from components.Sidebar import sidebar
from shared import constants

st.title('🦜🔗 Langchain - Blog Outline Generator App')

api_key = sidebar()

def blog_outline(topic):
  # Instantiate LLM model
  llm = OpenAI(
    model_name=constants.OPENROUTER_DEFAULT_INSTRUCT_MODEL,
    openai_api_key=api_key,
    openai_api_base=constants.OPENROUTER_API_BASE,
    headers={"HTTP-Referer": constants.OPENROUTER_REFERER}
  )
  # Prompt
  template = 'As an experienced data scientist and technical writer, generate an outline for a blog about {topic}.'
  prompt = PromptTemplate(input_variables = ['topic'], template = template)
  prompt_query = prompt.format(topic=topic)
  # Run LLM model
  response = llm(prompt_query)
  # Print results
  return st.info(response)

with st.form('myform'):
  topic_text = st.text_input('Enter prompt:', '')
  submitted = st.form_submit_button('Submit')
  if submitted:
    blog_outline(topic_text)
