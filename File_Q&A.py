import streamlit as st
import openai
import json
from components.Sidebar import sidebar

api_key = sidebar()

st.title("📝 File Q&A with OpenRouter")
uploaded_file = st.file_uploader("Upload an article", type="txt")
with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    question = a.text_input(
        "Ask something about the article",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )
    b.form_submit_button("Ask", use_container_width=True)

if uploaded_file and question and not api_key:
    st.info("Please add your OpenRouter API key to continue.")

if uploaded_file and question and api_key:
    article = uploaded_file.read().decode()
    openai.api_base = "https://openrouter.ai/api/v1"
    # openai.api_base = "http://localhost:3000/api/v1"
    openai.api_key = api_key
    context_prompt = f"""Here's an article:\n\n<article>
    {article}\n\n</article>\n\n"""
    context_message = {"role": "assistant", "content": context_prompt}
    question_message = {"role": "user", "content": question}
    response = openai.ChatCompletion.create(
        model="openai/gpt-3.5-turbo",
        messages=[context_message, question_message],
        headers={"HTTP-Referer": "https://yourdomain.streamlit.io"},
    )
    # response is sometimes type str
    # TODO replace this hack with a real fix
    if(type(response) == str):
        response = json.loads(response)
    msg = response["choices"][0]["message"]
    st.write("### Answer")
    st.write(msg["content"])
