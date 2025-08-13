import uuid

import openai
import streamlit as st
from trubrics_utils import trubrics_config

from trubrics.integrations.streamlit import FeedbackCollector

st.title("💬 [Trubrics] LLM Chat with user feedback")


with st.sidebar:
    email, password = trubrics_config()
    st.divider()
    stream = st.toggle("Stream LLM response", value=True)

if not email or not password:
    st.info(
        "To chat with an LLM and save your feedback to Trubrics, add your email and password in the sidebar."
        " Don't have an account yet? Create one for free [here](https://trubrics.streamlit.app/)!"
    )
    st.stop()


@st.cache_data
def init_trubrics(email, password):
    try:
        collector = FeedbackCollector(email=email, password=password, project="default")
        return collector
    except Exception:
        st.error(f"Error authenticating '{email}' with [Trubrics](https://trubrics.streamlit.app/). Please try again.")
        st.stop()


collector = init_trubrics(email, password)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "prompt_ids" not in st.session_state:
    st.session_state["prompt_ids"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

model = st.secrets.get("OPENAI_API_MODEL") or "gpt-3.5-turbo"
tags = [f"llm_chatbot{'_stream' if stream else ''}.py"]

openai_api_key = st.secrets.get("OPENAI_API_KEY")

messages = st.session_state.messages

for n, msg in enumerate(messages):
    st.chat_message(msg["role"]).write(msg["content"])

    if msg["role"] == "assistant" and n > 1:
        feedback_key = f"feedback_{int(n / 2)}"

        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = None
        feedback = collector.st_feedback(
            component="default",
            feedback_type="thumbs",
            open_feedback_label="[Optional] Provide additional feedback",
            model=model,
            tags=tags,
            key=feedback_key,
            prompt_id=st.session_state.prompt_ids[int(n / 2) - 1],
            user_id=email,
        )
        if feedback:
            with st.sidebar:
                st.write(":orange[Here's the raw feedback you sent to [Trubrics](https://trubrics.streamlit.app/):]")
                st.write(feedback)

if prompt := st.chat_input("Ask your question"):
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        openai.api_key = openai_api_key

    with st.chat_message("assistant"):
        if stream:
            message_placeholder = st.empty()
            generation = ""
            for response in openai.ChatCompletion.create(model=model, messages=messages, stream=True):
                generation += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(generation + "▌")
            message_placeholder.markdown(generation)
        else:
            response = openai.ChatCompletion.create(model=model, messages=messages)
            generation = response.choices[0].message.content
            st.write(generation)

        logged_prompt = collector.log_prompt(
            config_model={"model": model},
            prompt=prompt,
            generation=generation,
            session_id=st.session_state.session_id,
            tags=tags,
            user_id=email,
        )
        st.session_state.prompt_ids.append(logged_prompt.id)
        messages.append({"role": "assistant", "content": generation})
        st.experimental_rerun()  # force rerun of app, to load last feedback component
