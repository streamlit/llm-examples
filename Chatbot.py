import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = "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"

# Initialize session state
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []

if 'openai_response' not in st.session_state:
    st.session_state['openai_response'] = []

def api_calling(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message_text = completions.choices[0].text
    return message_text

def message(text, key, avatar_style="icons", is_user=False):
    # Display messages in the chat interface
    if not is_user:
        st.text(text)
    else:
        st.text("User: " + text)

st.title("ChatGPT ChatBot With Streamlit and OpenAI")

def get_text():
    input_text = st.text_input("Write here", key="input")
    return input_text

user_input = get_text()

if user_input:
    try:
        output = api_calling(user_input)
        output = output.lstrip("\n")

        # Store the output
        st.session_state.openai_response.append(output)
        st.session_state.user_input.append(user_input)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Display the chat history
user_input_history = st.session_state.get('user_input', [])
for i, user_input in enumerate(user_input_history):
    message(user_input, key=str(i), avatar_style="icons", is_user=True)
    message(st.session_state['openai_response'][i], key=str(i) + 'data_by_user', avatar_style="miniavs")

# Display the current user input
if user_input:
    message(user_input, key="current_user_input", avatar_style="icons", is_user=True)

# Display the current AI response
if st.session_state.get('openai_response'):
    message(st.session_state['openai_response'][-1], key="current_ai_response", avatar_style="miniavs")
