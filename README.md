# 🔀 OpenRouter + Streamlit Example App

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/alexanderatallah/openrouter-streamlit?quickstart=1)

Starter examples for building LLM apps with Streamlit and OpenRouter.

## Overview of the App

This app showcases a growing collection of OpenRouter minimum working examples, using multiple AI APIs.

Current examples include:

- Chatbot
- File Q&A
- Langchain Quickstart
- Langchain PromptTemplate
- LangChain Search

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://llm-examples.streamlit.app/)

## Running the code

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run File_Q\&A.py
```

## Getting API keys

Not needed! Your users will click the **Connect OpenRouter** button and auto-supply your app with a custom API key, using an [OAuth PKCE flow]("https://oauth.net/2/pkce/").
