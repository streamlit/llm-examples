import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers



def getLlamaResponse(input_text, no_words, category):
    llm = CTransformers(model = 'model/path', 
                        model_type = 'model_type', # using llama from share link
                        config={'max_new_tokens': 256,
                                'temperature': 0.01})

    
    template = """Write a  {category} on {input_text} in less than {no_words} word"""

    prompt = PromptTemplate(input_variables = ["input_text", "no_words", "category"],
                            template = template)
    

    respone = llm(prompt.format(category=category,input_text=input_text,no_words=no_words))
    print(respone)
    return respone



st.set_page_config(page_title = "Content-Creater",
                    layout='centered',
                    initial_sidebar_state = "collapsed")



input_text = st.text_input("Write your creative words")

col1,col2 = st.columns([5,5])

with col1:
    no_words = st.text_input('Number of words')
with col2:
    category = st.selectbox("category",
                              ('Essays', 'Poem', 'Joke', 'Blog'),
                              index=0)
    
submit = st.button("Start")

if submit:
    st.write(getLlamaResponse(input_text, no_words, category))