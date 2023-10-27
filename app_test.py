from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from openai.openai_object import OpenAIObject


# See https://github.com/openai/openai-python/issues/398
def create_openai_object_sync(response: str, role: str = "assistant") -> OpenAIObject:
    obj = OpenAIObject()
    message = OpenAIObject()
    content = OpenAIObject()
    content.content = response
    content.role = role
    message.message = content
    obj.choices = [message]
    return obj


@patch("openai.ChatCompletion.create")
def test_Chatbot(openai_create):
    at = AppTest.from_file("Chatbot.py").run()
    assert not at.exception
    at.chat_input[0].set_value("Do you know any jokes?").run()
    assert at.info[0].value == "Please add your OpenAI API key to continue."

    JOKE = "Why did the chicken cross the road? To get to the other side."
    openai_create.return_value = create_openai_object_sync(JOKE)
    at.text_input(key="chatbot_api_key").set_value("sk-...")
    at.chat_input[0].set_value("Do you know any jokes?").run()
    print(at)
    assert at.chat_message[1].markdown[0].value == "Do you know any jokes?"
    assert at.chat_message[2].markdown[0].value == JOKE
    assert at.chat_message[2].avatar == "assistant"
    assert not at.exception


@patch("langchain.llms.OpenAI.__call__")
def test_Langchain_Quickstart(langchain_llm):
    at = AppTest.from_file("pages/3_Langchain_Quickstart.py").run()
    assert at.info[0].value == "Please add your OpenAI API key to continue."

    RESPONSE = "1. The best way to learn how to code is by practicing..."
    langchain_llm.return_value = RESPONSE
    at.sidebar.text_input[0].set_value("sk-...")
    at.button[0].set_value(True).run()
    print(at)
    assert at.info[0].value == RESPONSE
