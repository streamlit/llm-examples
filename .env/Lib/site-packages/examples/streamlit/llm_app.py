import openai
import streamlit as st
from trubrics_utils import trubrics_config, trubrics_successful_feedback

from trubrics.integrations.streamlit import FeedbackCollector

if "response" not in st.session_state:
    st.session_state.response = ""
if "feedback_key" not in st.session_state:
    st.session_state.feedback_key = 0
if "logged_prompt" not in st.session_state:
    st.session_state.logged_prompt = ""

st.title("LLM User Feedback with Trubrics")

with st.sidebar:
    email, password = trubrics_config()

if email and password:
    try:
        collector = FeedbackCollector(email=email, password=password, project="default")
    except Exception:
        st.error(f"Error authenticating '{email}' with [Trubrics](https://trubrics.streamlit.app/). Please try again.")
        st.stop()
else:
    st.info(
        "To ask a question to an LLM and save your feedback to Trubrics, add your email and password in the sidebar."
        " Don't have an account yet? Create one for free [here](https://trubrics.streamlit.app/)!"
    )
    st.stop()

models = ("gpt-3.5-turbo",)
model = st.selectbox(
    "Choose your GPT-3.5 LLM",
    models,
    help="Consult https://platform.openai.com/docs/models/gpt-3-5 for model info.",
)

openai.api_key = st.secrets.get("OPENAI_API_KEY")
if openai.api_key is None:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

prompt = st.text_area(label="Prompt", label_visibility="collapsed", placeholder="What would you like to know?")
button = st.button(f"Ask {model}")

if button:
    response = openai.ChatCompletion.create(model=model, messages=[{"role": "user", "content": prompt}])
    response_text = response.choices[0].message["content"]
    st.session_state.logged_prompt = collector.log_prompt(
        config_model={"model": model}, prompt=prompt, generation=response_text, tags=["llm_app.py"], user_id=email
    )
    st.session_state.response = response_text
    st.session_state.feedback_key += 1

if st.session_state.response:
    st.markdown(f"#### :violet[{st.session_state.response}]")

    feedback = collector.st_feedback(
        component="default",
        feedback_type="thumbs",
        open_feedback_label="[Optional] Provide additional feedback",
        prompt_id=st.session_state.logged_prompt.id,
        model=model,
        align="flex-start",
        tags=["llm_app.py"],
        key=f"feedback_{st.session_state.feedback_key}",  # overwrite with new key
        user_id=email,
    )

    if feedback:
        trubrics_successful_feedback(feedback)
