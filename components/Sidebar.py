import streamlit as st
import webbrowser


def sidebar():
    with st.sidebar:
        params = st.experimental_get_query_params()
        api_key = params.get("api_key", [""])[0] or st.session_state.get("api_key")
        if not api_key:
            if st.button("Connect OpenRouter"):
                webbrowser.open(
                    "https://openrouter.ai/account?callback_url=http://localhost:8501",
                    new=0,
                )
            # link = "[Connect OpenRouter](https://openrouter.ai/account?callback_url=http://localhost:8501)"
            # st.markdown(link, unsafe_allow_html=True)
            # api_key = st.text_input("Or enter a key manually:")
        else:
            st.session_state["api_key"] = api_key
            st.text("Connected to OpenRouter")
            if st.button("Log out"):
                del st.session_state["api_key"]
                st.experimental_rerun()
            st.experimental_set_query_params()
        "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
    return api_key
