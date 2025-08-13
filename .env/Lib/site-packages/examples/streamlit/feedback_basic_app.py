import streamlit as st

from trubrics.integrations.streamlit import FeedbackCollector

collector = FeedbackCollector(email=st.secrets.TRUBRICS_EMAIL, password=st.secrets.TRUBRICS_PASSWORD, project="default")

user_feedback = collector.st_feedback(
    component="default",
    feedback_type="thumbs",
    open_feedback_label="[Optional] Provide additional feedback",
    model="gpt-3.5-turbo",
    prompt_id=None,  # checkout collector.log_prompt() to log your user prompts
)

if user_feedback:
    st.write("#### Raw feedback saved to Trubrics:")
    st.write(user_feedback)
