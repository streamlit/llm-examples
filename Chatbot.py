import streamlit as st
import openai
import os
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# Initialize OpenAI client instance
def init_openai():
    openai_api_key = st.session_state.get("openai_api_key")
    if openai_api_key:
        openai.api_key = openai_api_key
        return openai
    return None

# Function to generate speech from text
def generate_speech(text, client):
    response = client.Audio.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    audio_content = response["audio"]
    st.audio(audio_content, format="audio/mp3")

# Function to transcribe speech to text
def transcribe_speech(file_buffer, client):
    response = client.Audio.transcriptions.create(
        file=file_buffer,
        model="whisper-1"
    )
    return response["text"]

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
    if openai_api_key:
        st.session_state["openai_api_key"] = openai_api_key

    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display message history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

openai_client = init_openai()

if prompt := st.chat_input():
    if not openai_client:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = openai_client.ChatCompletion.create(
        model="gpt-4",
        messages=st.session_state["messages"]
    )

    msg = response.choices[0]["message"]["content"]
    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    # Provide options to generate speech or upload voice for transcription
    if st.button("Generate Speech"):
        if openai_client:
            generate_speech(msg, openai_client)

    uploaded_file = st.file_uploader("Upload Audio for Transcription", type=["mp3", "wav"])
    if uploaded_file is not None:
        file_buffer = BytesIO(uploaded_file.read())
        if openai_client:
            transcribed_text = transcribe_speech(file_buffer, openai_client)
            st.write("Transcribed text: ", transcribed_text)
