import openai
import streamlit as st


def _submit_feedback(user_response, emoji=None):
    st.toast(f"Feedback submitted: {user_response}", icon=emoji)
    return user_response.update({"some metadata": 123})


def chatbot_thumbs_app(streamlit_feedback, debug=False):
    st.title("💬 Chatbot")

    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            key="chatbot_api_key",
            type="password",
            value=st.secrets.get("OPENAI_API_KEY"),
        )

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    messages = st.session_state.messages

    for n, msg in enumerate(messages):
        st.chat_message(msg["role"]).write(msg["content"])

        if msg["role"] == "assistant" and n > 1:
            feedback_key = f"feedback_{int(n/2)}"

            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="Please provide extra information",
                on_submit=_submit_feedback,
                key=feedback_key,
            )

    if prompt := st.chat_input():
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if debug:
            st.session_state["response"] = "dummy response"
        else:
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
            else:
                openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            st.session_state["response"] = response.choices[0].message.content
        with st.chat_message("assistant"):
            messages.append(
                {"role": "assistant", "content": st.session_state["response"]}
            )
            st.write(st.session_state["response"])
            st.rerun()


def single_prediction_faces_app(streamlit_feedback, debug=False):
    st.title("LLM User Feedback with Trubrics")

    if "response" not in st.session_state:
        st.session_state["response"] = ""
    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            key="chatbot_api_key",
            type="password",
            value=st.secrets.get("OPENAI_API_KEY"),
        )

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        openai.api_key = openai_api_key

    prompt = st.text_area(
        label="Prompt",
        label_visibility="collapsed",
        placeholder="What would you like to know?",
    )
    button = st.button(f"Ask text-davinci-002")

    if button:
        if debug:
            st.session_state["response"] = "dummy response: " + prompt.strip()
        else:
            st.session_state["response"] = openai.Completion.create(
                model="text-davinci-002", prompt=prompt, temperature=0.5, max_tokens=200
            )
            st.session_state["response"] = (
                st.session_state["response"].choices[0].text.replace("\n", "")
            )
        st.session_state.feedback_key += 1  # overwrite feedback component

    if st.session_state["response"]:
        st.markdown(f"#### :violet[{st.session_state['response']}]")

        streamlit_feedback(
            feedback_type="faces",
            optional_text_label="Please provide extra information",
            align="flex-start",
            on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
        )


def basic_app(streamlit_feedback, debug):
    st.title("Component demo")

    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    st.button("Random button")

    if st.button("Refresh feedback component"):
        st.session_state.feedback_key += 1  # overwrite feedback component

    multiline = st.toggle("Multiline", value=False)

    if multiline:
        feedback = streamlit_feedback(
            feedback_type="faces",
            # on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
            optional_text_label="Please provide some more information",
            max_text_length=500,
            args=["✅"],
        )
    else:
        feedback = streamlit_feedback(
            feedback_type="faces",
            # on_submit=_submit_feedback,
            key=f"feedback_{st.session_state.feedback_key}",
            optional_text_label="Please provide some more information",
            args=["✅"],
        )

    if feedback:
        st.write(":orange[Component output:]")
        st.write(feedback)


def bare_bones_app(streamlit_feedback, debug):
    feedback = streamlit_feedback(feedback_type="faces", on_submit=_submit_feedback)

    if feedback:
        st.write(":orange[Component output:]")
        st.write(feedback)


def streaming_chatbot(streamlit_feedback, debug):

    st.title("💬 Streaming Chatbot")

    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "feedback_key" not in st.session_state:
        st.session_state.feedback_key = 0

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "Please provide extra information",
        "on_submit": _submit_feedback,
    }

    for n, msg in enumerate(st.session_state.messages):
        st.chat_message(msg["role"]).write(msg["content"])

        if msg["role"] == "assistant" and n > 1:
            feedback_key = f"feedback_{int(n/2)}"

            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            disable_with_score = (
                st.session_state[feedback_key].get("score")
                if st.session_state[feedback_key]
                else None
            )
            streamlit_feedback(
                **feedback_kwargs,
                key=feedback_key,
                disable_with_score=disable_with_score,
            )

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        streamlit_feedback(
            **feedback_kwargs, key=f"feedback_{int(len(st.session_state.messages)/2)}"
        )
