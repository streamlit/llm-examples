import streamlit as st

from trubrics.integrations.streamlit import FeedbackCollector

if "logged_prompt" not in st.session_state:
    st.session_state.logged_prompt = None
if "feedback_key" not in st.session_state:
    st.session_state.feedback_key = 0

# 1. authenticate with trubrics
collector = FeedbackCollector(email=st.secrets.TRUBRICS_EMAIL, password=st.secrets.TRUBRICS_PASSWORD, project="default")

if st.button("Refresh"):
    st.session_state.feedback_key += 1
    st.session_state.logged_prompt = None
    st.experimental_rerun()

prompt = "Tell me a joke"
generation = "Why did the chicken cross the road? To get to the other side."
st.write(f"#### :orange[Example user prompt: {prompt}]")


if st.button("Generate response"):
    # 2. log a user prompt & model response
    st.session_state.logged_prompt = collector.log_prompt(
        config_model={"model": "gpt-3.5-turbo"},
        prompt=prompt,
        generation=generation,
    )

if st.session_state.logged_prompt:
    st.write(f"#### :blue[Example model generation: {generation}]")
    # 3. log some user feedback
    user_feedback = collector.st_feedback(
        component="default",
        feedback_type="thumbs",
        open_feedback_label="[Optional] Provide additional feedback",
        model=st.session_state.logged_prompt.config_model.model,
        prompt_id=st.session_state.logged_prompt.id,
        key=st.session_state.feedback_key,
        align="flex-start",
    )
