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
def test_basic_chat(openai_create):
    at = AppTest.from_file("Chatbot.py")
    # Todo: Remove the key in app and fix this once we have chat_input support
    at.session_state["chat"] = "Do you know any jokes?"
    at.run()
    assert at.get("alert")[0].proto.body == "Please add your OpenAI API key to continue."
    assert not at.exception

    JOKE = "Why did the chicken cross the road? To get to the other side."
    openai_create.return_value = create_openai_object_sync(JOKE)
    at.text_input(key="chatbot_api_key").set_value("sk-...").run()
    print(at)
    assert at.get("chat_message")[1].markdown[0].value == "Do you know any jokes?"
    assert at.get("chat_message")[2].markdown[0].value == JOKE
    assert not at.exception
