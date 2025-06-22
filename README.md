# 🎈 Streamlit + LLM Examples App

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)

Starter examples for building LLM apps with Streamlit.

## Overview of the App

This app showcases a growing collection of LLM minimum working examples.

Current examples include:

- Chatbot
- File Q&A
- Chat with Internet search
- LangChain Quickstart
- LangChain PromptTemplate
- Chat with user feedback

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://llm-examples.streamlit.app/)

### Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:

1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.

### Enter the OpenAI API key in Streamlit Community Cloud

To set the OpenAI API key as an environment variable in Streamlit apps, do the following:

1. At the lower right corner, click on `< Manage app` then click on the vertical "..." followed by clicking on `Settings`.
2. This brings the **App settings**, next click on the `Secrets` tab and paste the API key into the text box as follows:

```sh
OPENAI_API_KEY='xxxxxxxxxx'
```

## Run it locally

```sh
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Chatbot.py
```


O chanceler do governo Lula, Mauro Vieira, afirmou nesta quarta-feira que o interesse nacional está sempre em primeiro lugar nas relações com outros países. Vieira deu essa declaração ao ser perguntado por alguns parlamentares sobre as ameaças do governo do presidente americano, Donald Trump, ao ministro do Supremo Tribunal Federal (STF), Alexandre de Moraes.

— Queria relembrar as palavras que disse, em que fiz referência ao Barão do Rio Branco, dizendo que o Brasil não tem alianças, não tem parcerias incondicionais. O principal é o interesse nacional, que está sempre em primeiro lugar — afirmou, em audiência pública na Comissão de Relações Exteriores e Defesa Nacional da Câmara dos Deputados, Mauro Vieira também foi questionado sobre o anúncio feito pelo secretário de Estado dos EUA, Marco Rubio, de que haverá restrição na concessão de vistos para autoridades estrangeiras. Rubio não citou alvos, mas bolsonaristas acreditam que entre os alvos estão ministros do STF.

— A política de visto é de cada Estrado, cada um toma as decisões de conceder ou não conceder. É uma decisão soberana de cada país — disse ele, sem citar nomes que poderiam ser afetados com a medida.

Na semana passada, Marco Rubio declarou que há possibilidade de Moraes sofrer sanções dos EUA, como ser proibido de entrar no país. O chefe da diplomacia americana causou preocupação ao governo brasileiro, que afirmou a Washington que as relações bilaterais serão negativamente afetadas.