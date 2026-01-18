import streamlit as st
from openai import OpenAI
import os  # <--- 1. 必须导入这个库，才能读取环境变量

with st.sidebar:
    # 尝试先从环境变量拿 Key，如果没拿不到，留空让用户自己填
    env_key = os.getenv("OPENAI_API_KEY", "")
    
    openai_api_key = st.text_input(
        "OpenAI API Key", 
        value=env_key, # 如果环境变量有值，直接填进去
        key="chatbot_api_key", 
        type="password"
    )
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Google Gemini")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # 2. 修正逻辑：这里应该使用 openai_api_key 变量
    # 因为这个变量现在包含了“环境变量”或“用户手动输入”的值
    client = OpenAI(
        api_key=openai_api_key, 
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # 3. 修正模型名称：目前 Google 官方模型通常是 gemini-1.5-flash
    # "gemini-2.5-flash" 可能是不存在的，可能会导致报错。
    # 建议先用 gemini-1.5-flash 跑通，以后再换。
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", 
            messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    except Exception as e:
        st.error(f"Error: {e}")