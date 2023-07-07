import openai
import streamlit as st
from streamlit_chat import message
from components.Sidebar import sidebar
import json
from shared import constants

api_key, selected_model = sidebar(constants.OPENROUTER_DEFAULT_CHAT_MODEL)

st.title("💬 Streamlit GPT")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

with st.form("chat_input", clear_on_submit=True):
    a, b = st.columns([4, 1])
    user_input = a.text_input(
        label="Your message:",
        placeholder="What would you like to say?",
        label_visibility="collapsed",
    )
    b.form_submit_button("Send", use_container_width=True)

for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=i)

if user_input and not api_key:
    st.info("Please click Connect OpenRouter to continue.")

if user_input and api_key:
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)
    openai.api_key = api_key
    openai.api_base = constants.OPENROUTER_API_BASE
    response = openai.ChatCompletion.create(
        model=selected_model,
        messages=st.session_state.messages,
        headers={"HTTP-Referer": constants.OPENROUTER_REFERRER},
    )
    # response is sometimes type str
    # TODO replace this hack with a real fix
    if type(response) == str:
        response = json.loads(response)
    msg = response["choices"][0]["message"]
    st.session_state.messages.append(msg)
    message(msg["content"])
