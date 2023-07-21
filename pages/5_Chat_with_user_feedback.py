import streamlit as st
import openai
from trubrics.integrations.streamlit import FeedbackCollector


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="langchain_search_api_key_openai", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/pages/2_Chat_with_search.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("🔎 Trubrics - Chat with user feedback")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]
if "response" not in st.session_state:
    st.session_state["response"] = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Tell me a joke about sharks"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        openai.api_key = openai_api_key

    response = openai.Completion.create(model="text-davinci-002", prompt=prompt, temperature=0.5, max_tokens=200)
    st.session_state["response"] = response.choices[0].text.replace("\n", "")
    with st.chat_message("assistant"):
        st.session_state.messages.append({"role": "assistant", "content": st.session_state["response"]})
        st.write(st.session_state["response"])

if st.session_state["response"]:
    collector = FeedbackCollector(component_name="default", email=None, password=None)

    feedback = collector.st_feedback(
        feedback_type="thumbs",
        model="text-davinci-002",
        open_feedback_label="[Optional] Provide additional feedback",
        metadata={"response": st.session_state["response"], "prompt": prompt},
        save_to_trubrics=False,
    )
    if feedback:
        st.success("Feedback saved! You can analyse your feedback with https://trubrics.streamlit.app/.")
