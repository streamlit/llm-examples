import os

import streamlit as st
from openai import OpenAI

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE", "https://api.openai.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

with st.sidebar:
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/pages/1_File_Q%26A.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("📝 File Q&A with LLM Gateway")
uploaded_file = st.file_uploader("Upload an article", type=("txt", "md"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    article = uploaded_file.read().decode()
    prompt = f"Here's an article:\n\n<article>\n{article}\n\n</article>\n\n{question}"

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=False,  # Make sure streaming is disabled
    )
    st.write(response.choices[0].message.content)
