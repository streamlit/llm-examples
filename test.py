import os

from openai import OpenAI

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE", "https://api.openai.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")


prompt = f"Here's an article: what is this"

client =OpenAI(api_key=API_KEY, base_url=BASE_URL)
chat = client.chat.completions.create(
    model=LLM_MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    stream=False,  # Make sure streaming is disabled
)
chat.choices[0].message.content
print(chat.choices[0].message.content)
