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
streamlit run Chatbot.py
```

## Get an OpenRouter API key

You can get your own OpenRouter API key by following the following instructions:

1. Go to https://openrouter.ai/account.
2. Click on the `Create API key` button at the bottom.
3. Next, enter an identifier name and click on the `Create` button.

## Enter the OpenRouter API key in Streamlit Community Cloud

To set the OpenRouter API key as an environment variable in Streamlit apps, do the following:

1. At the lower right corner, click on `< Manage app` then click on the vertical "..." followed by clicking on `Settings`.
2. This brings the **App settings**, next click on the `Secrets` tab and paste the API key into the text box as follows:

```sh
OPENROUTER_API_KEY='xxxxxxxxxx'
```
