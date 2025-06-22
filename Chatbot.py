from openai import OpenAI
import anthropic
from dotenv import load_dotenv
import streamlit as st
import asyncio
from streamlit_product_card import product_card
from utils import (
    updateFile, 
    solicitaCargaBaseConhecimento, 
    listaDocumentos, 
    verificaDocumento, 
    getEstruturas, 
    getRecursos, 
    get_structure_prompt, 
    get_recurso_narrativo, 
    digitaPrompt,
    getPersonagens,
    getFatos,
    get_prompt_fato,
    carrega_fatos,
    get_prompt_personagem,
    get_instrucoes,
    getComoComecar,
    getComoComecarTexto,
    getComoOrganizar,
    getComoOrganizarTexto,
    getComoEnsinar,
    getComoEnsinarTexto,
    getFormasContar,
    getFormasContarTexto,
    getEngajamentoCuriosidade,
    getEngajamentoCuriosidadeTexto,
    getTomVoz,
    getTomVozTexto,
    getClarezaAutoridade,
    getClarezaAutoridadeTexto,
    getPosicionamentoConexao,
    getPosicionamentoConexaoTexto,
    getRecursosExtras,
    getRecursosExtrasTexto,
    getPromptRecursoIniciante,
    getPromptUsoHistoria,
    getPromptPersonagemIniciante,
    getPromptFatoIniciante,
    getPromptTextoIniciante,
    getPromptFinalTextoIniciante,
    getPromptTextoIntermediario,
    getPromptFatoIntermediario,
    getPromptPersonagemIntermediario,
    getEstruturasAvancadas,
    getRecursosAvancados,
    getPromptTextoAvancado,
    getPromptFatoAvancado,
    getPromptPersonagemAvancado    
)
from streamlit_quill import st_quill
import json
import time
import re
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
from typing import Dict, List, Union
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

load_dotenv()

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = None
    
if 'anthropic_api_key' not in st.session_state:
    st.session_state.anthropic_api_key = None

if 'deepseek_api_key' not in st.session_state:
    st.session_state.deepseek_api_key = None    

if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = None  

if 'openai_model' not in st.session_state:
    st.session_state.openai_model = None

if 'anthropic_model' not in st.session_state:
    st.session_state.anthropic_model = None  
    
if 'deepseek_model' not in st.session_state:
    st.session_state.deepseek_model = None      
    
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None 
    
if 'recurso' not in st.session_state:    
    st.session_state.recurso = None  

if 'como_comecar' not in st.session_state:    
    st.session_state.como_comecar = None  

if 'como_organizar' not in st.session_state:    
    st.session_state.como_organizar = None  
    
if 'como_ensinar' not in st.session_state:    
    st.session_state.como_ensinar = None         

if 'formas_contar' not in st.session_state:    
    st.session_state.formas_contar = None         

if 'engajamento_curiosidade' not in st.session_state:    
    st.session_state.engajamento_curiosidade = None   

if 'tom_voz' not in st.session_state:    
    st.session_state.tom_voz = None   

if 'clareza_autoridade' not in st.session_state:    
    st.session_state.clareza_autoridade = None   

if 'posicionamento_conexao' not in st.session_state:    
    st.session_state.posicionamento_conexao = None   

if 'recursos_extras' not in st.session_state:    
    st.session_state.recursos_extras = None     
    
if 'tipo_estoria' not in st.session_state:    
    st.session_state.tipo_estoria = None  
    
if 'recurso_estoria' not in st.session_state:    
    st.session_state.recurso_estoria = None
    
if 'uso_estoria' not in st.session_state:    
    st.session_state.uso_estoria = None
    
if 'estrutura' not in st.session_state:    
    st.session_state.estrutura = None  
    
if 'conteudo_digitado' not in st.session_state:   
    st.session_state.conteudo_digitado = None  

if 'proposta_selecionada' not in st.session_state:   
    st.session_state.proposta_selecionada = None   
    
if 'modo_narracao' not in st.session_state:       
    st.session_state.modo_narracao = None
    
if 'narrativa' not in st.session_state:
   st.session_state.narrativa = None 
   
if 'autor' not in st.session_state:
    st.session_state.autor = "rodrigo.almeida@gmail.com"        

if 'personagem' not in st.session_state:
    st.session_state.personagem = None
    
if 'fato' not in st.session_state:
    st.session_state.fato = None    
    
if 'provedor' not in st.session_state:
    st.session_state.provedor = None

if 'idioma' not in st.session_state:
    st.session_state.idioma = None

if 'modelOpenAI' not in st.session_state:
    st.session_state.modelOpenAI = None    

if 'modelAnthropic' not in st.session_state:
    st.session_state.modelAnthropic = None 
    
if 'modelDeepseek' not in st.session_state:
    st.session_state.modelDeepseek = None 

if 'modelGemini' not in st.session_state:
    st.session_state.modelGemini = None     
                
if 'num_propostas' not in st.session_state:
    st.session_state.num_propostas = 3    
            
if 'narrativas' not in st.session_state:
    st.session_state['narrativas'] = []
    
if 't1' not in st.session_state:
    st.session_state.t1 = False
    
if 't2' not in st.session_state:
    st.session_state.t2 = False
    
if 't3' not in st.session_state:
    st.session_state.t3 = False
    
if 't4' not in st.session_state:
    st.session_state.t4 = False

if 't5' not in st.session_state:
    st.session_state.t5 = False
    
if 't6' not in st.session_state:
    st.session_state.t6 = False                   
    
if 't7' not in st.session_state:
    st.session_state.t7 = False    

if 't8' not in st.session_state:
    st.session_state.t8 = False

if 't9' not in st.session_state:
    st.session_state.t9 = False


if 'e1' not in st.session_state:
    st.session_state.e1 = False
    
if 'e2' not in st.session_state:
    st.session_state.e2 = False
    
if 'e3' not in st.session_state:
    st.session_state.e3 = False
    
if 'e4' not in st.session_state:
    st.session_state.e4 = False

if 'e5' not in st.session_state:
    st.session_state.e5 = False
    
if 'e6' not in st.session_state:
    st.session_state.e6 = False                   
    
if 'e7' not in st.session_state:
    st.session_state.e7 = False    

if 'e8' not in st.session_state:
    st.session_state.e8 = False

if 'e9' not in st.session_state:
    st.session_state.e9 = False

if 'e10' not in st.session_state:
    st.session_state.e10 = False
    
if 'e11' not in st.session_state:
    st.session_state.e11 = False
    
if 'e12' not in st.session_state:
    st.session_state.e12 = False    
    
    
if 'r1' not in st.session_state:
    st.session_state.r1 = False
    
if 'r2' not in st.session_state:
    st.session_state.r2 = False
    
if 'r3' not in st.session_state:
    st.session_state.r3 = False
    
if 'r4' not in st.session_state:
    st.session_state.r4 = False

if 'r5' not in st.session_state:
    st.session_state.r5 = False
    
if 'r6' not in st.session_state:
    st.session_state.r6 = False                   
    
if 'r7' not in st.session_state:
    st.session_state.r7 = False    

if 'r8' not in st.session_state:
    st.session_state.r8 = False

if 'r9' not in st.session_state:
    st.session_state.r9 = False

if 'r10' not in st.session_state:
    st.session_state.r10 = False
    
if 'r11' not in st.session_state:
    st.session_state.r11 = False
    
if 'r12' not in st.session_state:
    st.session_state.r12 = False           

if 'r13' not in st.session_state:
    st.session_state.r13 = False           

OPENAI_MODELS_1 = ("gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14",
                   "gpt-4o-2024-08-06", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06",
                   "gpt-4o-realtime-preview-2024-12-17", "gpt-4o-realtime-preview-2024-10-01",
                   "gpt-4o-mini-2024-07-18", "gpt-4o-mini-realtime-preview-2024-12-17",
                   "o1-2024-12-17", "o1-preview-2024-09-12", "o3-2025-04-16", "o4-mini-2025-04-16",
                   "o3-mini-2025-01-31", "o1-mini-2024-09-12" , "--- PREMIUM MODELS ---", "o1-pro-2025-03-19", "gpt-4.5-preview-2025-02-27")


GEMINI_MODELS = ("gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro")

OPENAI_MODELS = ("gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14",
                   "gpt-4o-2024-08-06", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06",
                   "gpt-4o-realtime-preview-2024-12-17", "gpt-4o-realtime-preview-2024-10-01",
                   "gpt-4o-mini-2024-07-18", "gpt-4o-mini-realtime-preview-2024-12-17",
                   "o1-2024-12-17", "o1-preview-2024-09-12", "o4-mini-2025-04-16",
                   "o3-mini-2025-01-31", "o1-mini-2024-09-12" , "--- PREMIUM MODELS ---", "gpt-4.5-preview-2025-02-27")


# ANTHROPIC_MODELS = ("claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022")
ANTHROPIC_MODELS = ("claude-3-5-haiku-20241022")

DEEPSEEK_MODELS = ("deepseek-chat")

st.set_page_config(page_title='👾 VFN 1.0', layout='wide',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }                   
    #    initial_sidebar_state=st.session_state.get('sidebar_state', 'collapsed'),
)


def toggle_recurso_avancado():
    if st.session_state.r1:
        st.session_state.r2 = False
        st.session_state.r3 = False    
    if st.session_state.r2:
        st.session_state.r1 = False
        st.session_state.r3 = False    
    if st.session_state.r3:
        st.session_state.r2 = False
        st.session_state.r1 = False 
    
    if st.session_state.r4:
        st.session_state.r5 = False
        st.session_state.r6 = False    
    if st.session_state.r5:
        st.session_state.r4 = False
        st.session_state.r6 = False    
    if st.session_state.r6:
        st.session_state.r4 = False
        st.session_state.r5 = False   
        
    if st.session_state.r7:
        st.session_state.r8 = False        
    if st.session_state.r8:
        st.session_state.r7 = False

    if st.session_state.r9:
        st.session_state.r10 = False
        st.session_state.r11 = False    
    if st.session_state.r10:
        st.session_state.r9 = False
        st.session_state.r11 = False    
    if st.session_state.r11:
        st.session_state.r9 = False
        st.session_state.r10 = False   
        
    if st.session_state.r12:
        st.session_state.r13 = False        
    if st.session_state.r13:
        st.session_state.r12 = False              
        
                

def toggle_estrutura_avancada():
    if st.session_state.e1:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e2:
        st.session_state.e1 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e3:
        st.session_state.e1 = False
        st.session_state.e2 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e4:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e1 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e5:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e1 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e6:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e1 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e7:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e1 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e8:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e1 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e9:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e1 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e10:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e1 = False
        st.session_state.e11 = False
        st.session_state.e12 = False
    if st.session_state.e11:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e1 = False
        st.session_state.e12 = False
    if st.session_state.e12:
        st.session_state.e2 = False
        st.session_state.e3 = False
        st.session_state.e4 = False
        st.session_state.e5 = False
        st.session_state.e6 = False
        st.session_state.e7 = False
        st.session_state.e8 = False
        st.session_state.e9 = False
        st.session_state.e10 = False
        st.session_state.e11 = False
        st.session_state.e1 = False
        

def toggle_change_manager():
    # When toggle 1 is False, set toggle 2 to False
    if st.session_state.t1:
        st.session_state.t2 = False
        st.session_state.t3 = False    

    if st.session_state.t2:
        st.session_state.t1 = False
        st.session_state.t3 = False  
        
    if st.session_state.t3:
        st.session_state.t2 = False
        st.session_state.t1 = False    
        
    if st.session_state.t4:
        st.session_state.t5 = False
        st.session_state.t6 = False    
        st.session_state.t7 = False   
        st.session_state.t8 = False   
        st.session_state.t9 = False  
        
    if st.session_state.t5:
        st.session_state.t4 = False
        st.session_state.t6 = False    
        st.session_state.t7 = False   
        st.session_state.t8 = False   
        st.session_state.t9 = False  
        
    if st.session_state.t6:
        st.session_state.t5 = False
        st.session_state.t4 = False    
        st.session_state.t7 = False   
        st.session_state.t8 = False   
        st.session_state.t9 = False                            


    if st.session_state.t7:
        st.session_state.t5 = False
        st.session_state.t6 = False    
        st.session_state.t4 = False   
        st.session_state.t8 = False   
        st.session_state.t9 = False 
        
    if st.session_state.t8:
        st.session_state.t5 = False
        st.session_state.t6 = False    
        st.session_state.t7 = False   
        st.session_state.t4 = False   
        st.session_state.t9 = False    
        
    if st.session_state.t9:
        st.session_state.t5 = False
        st.session_state.t6 = False    
        st.session_state.t7 = False   
        st.session_state.t8 = False   
        st.session_state.t4 = False         
             
with st.sidebar:
    st.session_state.openai_api_key = st.text_input("OpenAI API Key", key="chat_openai_api_key", type="password")
    "[OpenAI Models Overview](https://platform.openai.com/docs/models)"
    st.session_state.anthropic_api_key = st.text_input("Anthropic API Key", key="chat_anthropic_api_key", type="password")    
    "[Anthropic Models Overview](https://docs.anthropic.com/en/docs/about-claude/models/overview)"
    st.session_state.deepseek_api_key = st.text_input("DeepSeek API Key", key="chat_deepseek_api_key", type="password")    
    "[DeepSeek Models Overview](https://api-docs.deepseek.com/quick_start/pricing)"    
    st.session_state.gemini_api_key = st.text_input("Gemini API Key", key="chat_gemini_api_key", type="password")    
    "[Gemini Models Overview](https://ai.google.dev/gemini-api/docs/models)"     
    

# Classe com parametros necessários para construção das propostas narrativas
@dataclass
class SupportDependencies:  
    narrativa: str
    personagem: str
    fatos: str
    tipo_estoria: str
    uso_estoria: str
    estrutura: str
    recurso: str
    count: int
    idioma: str

class SupportResult(BaseModel):
    titulo: str = Field(description='Um titulo que resume a proposta.')    
    proposta: str = Field(description='Ideia que deverá evoluir com base no tipo de estoria, recurso e uso da estoria sugerido pelo usuário, escrita no idioma selecionado pelo usuario.')
    # impacto: str = Field(description='Como a ideia impacta a jornada do personagem')
    # abordagem_estrutural: str = Field(description="De que forma a ideia está relacionada à abordagem estrutural proposta? (Ex.: A alternância emocional é alcançada através das indecisões do personagem .....)")
    # recurso_narrativo: str = Field(description="De que forma o recurso narrativo foi abordado? (ex.: incluí a Alegoria ao sugerir que o amor fosse representado através da relação entre o algodão e a desfiadeira....)")
    # lugar_comum: str = Field(description='Como a proposta sugerida evita que o escritor caia no lugar comum em relação a seu conteúdo?')


class Extraction(BaseModel):
    Support_Result: List[SupportResult] = Field(description="List of Support Results")    

@st.fragment() 
def getTitulosPropostas():
    result = []
    for i in range(len(st.session_state['narrativas'])):
        if st.session_state['narrativas'][i]["titulo"] is not None:
            result.append(st.session_state['narrativas'][i]["titulo"])        
    return result    

@st.fragment() 
def getNarrativaSelecionada():
    result = None
    for i in range(len(st.session_state['narrativas'])):
        if st.session_state['narrativas'][i]["titulo"] == st.session_state.proposta_selecionada:
            result = st.session_state['narrativas'][i]
            break              
    return result    
    

@st.fragment() 
def trecho5():
    with st.chat_message("assistant"):   
        st.write(digitaPrompt("🛺 Selecione o Título da Proposta que você gostaria de ver a estória completa:")) 


def callback_toggle(param):
    if param == 1:
        st.write("on_organizar")
        st.toggle()

        


@st.fragment() 
def escolheNarrativa():
    texto = "🧚🏼‍♀️"  
    trecho5()
    titulos = getTitulosPropostas()
    cols_titulos_propostas = st.columns(len(titulos))  
    for j, option_titulos_propostas in enumerate(titulos):                        
        if cols_titulos_propostas[j].button(option_titulos_propostas):
            st.session_state.proposta_selecionada = option_titulos_propostas                           
    if st.session_state.proposta_selecionada is not None:
        texto =  f"""🧚🏼‍♀️ Proposta Selecionada: {st.session_state.proposta_selecionada}"""
        st.info(texto)        
        nova_historia_texto = getNarrativaSelecionada()
        # st.write(nova_historia_texto)
        
        # prompt_instrucoes = get_instrucoes(nova_historia=nova_historia_texto,
        #                                    personagem = st.session_state.personagem,
        #                                    idioma=st.session_state.idioma)  
        
        
        uso_estoria = getPromptUsoHistoria(st.session_state.uso_estoria)
        fatos = carrega_fatos(st.session_state.narrativa, st.session_state.personagem, st.session_state.autor) 
        prompt_instrucoes = getPromptFinalTextoIniciante(nova_historia=nova_historia_texto,
                                            titulo=st.session_state.proposta_selecionada,             
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)       
        
        result_narrativa = None
        
        if (st.session_state.provedor == "ANTHROPIC"):
            support_agent_anthropic_narrativa = Agent(  
                st.session_state.modelAnthropic, 
                system_prompt=(  
                    "Você é um ajudante na jornada de um escritor em melhorar a escrita de seu conteúdo."            
                ),
                retries=2,
            )             
            with st.spinner(f"[ANTHROPIC {st.session_state.anthropic_model}] Gerando Narrativa....", show_time=True):    
                result_narrativa = support_agent_anthropic_narrativa.run_sync(prompt_instrucoes)
                while result_narrativa is None:        
                    time.sleep(1) 
                            
        if (st.session_state.provedor == "OPENAI"):
            support_agent_openai_narrativa = Agent(   
                st.session_state.modelOpenAI,
                system_prompt=(  
                    "Você é um ajudante na jornada de um escritor em melhorar a escrita de seu conteúdo."
                ),
                retries=2,
            )               
            with st.spinner(f"[OPENAI {st.session_state.openai_model}] Gerando Narrativa....", show_time=True):    
                result_narrativa =  support_agent_openai_narrativa.run_sync(prompt_instrucoes)
                while result_narrativa is None:        
                    time.sleep(1)            
                     
        if (st.session_state.provedor == "GEMINI"):
            support_agent_gemini_narrativa = Agent(  
                st.session_state.modelGemini, 
                system_prompt=(  
                    "Você é um ajudante na jornada de um escritor em melhorar a escrita de seu conteúdo."
                ),
                retries=2,
            )                
            with st.spinner(f"[GEMINI {st.session_state.gemini_model}] Gerando Narrativa....", show_time=True):    
                result_narrativa = support_agent_gemini_narrativa.run_sync(prompt_instrucoes)
                while result_narrativa is None:        
                    time.sleep(1)    

        if (st.session_state.provedor == "DEEPSEEK"):
            support_agent_deepseek_narrativa = Agent(  
                st.session_state.modelDeepseek, 
                system_prompt=(  
                    "Você é um ajudante na jornada de um escritor em melhorar a escrita de seu conteúdo."            
                ),
                retries=2,
            )                                 
            with st.spinner(f"[DEEPSEEK {st.session_state.deepseek_model}] Gerando Narrativa....", show_time=True):    
                result_narrativa = support_agent_deepseek_narrativa.run_sync(prompt_instrucoes)
                while result_narrativa is None:        
                    time.sleep(1)                              

        st.write(result_narrativa.output)                     


async def chat():  
    st.image("./logo/ComfyUI_00309_2.png", use_container_width=True )
    st.title("💬 Validador de Fluxo Narrativo - VFN 1.0")
    st.header("Cadastrar Narrativa Base 🧠")
    with st.expander("Expanda para Cadastrar Narrativa Base"):
        title = st.text_input("Título (evite caracteres especiais no título):", "")
        # Remove aspas
        title = title.replace('"', '')        
        st.session_state.conteudo_digitado = st_quill()   
        if st.button("Carregar", type="primary"):
            updateFile(title, st.session_state.autor, st.session_state.conteudo_digitado)
            solicitaCargaBaseConhecimento(title, st.session_state.autor,"NOVA_NARRATIVA","PT", "story_teller")   
            with st.spinner("Carregando Base de Conhecimento....", show_time=True):    
                while not verificaDocumento(title, st.session_state.autor):        
                    time.sleep(1)
                st.success("File successfully uploaded!")

    st.header("Parametrize a Contação de Estória 🎯")
    container = st.container(border=True)
    with container:
        options = listaDocumentos(st.session_state.autor)
        # cols = st.columns(len(options))
        st.session_state.narrativa = st.selectbox("Selecione uma Narrativa:", options=options, index=0, 
                                            help=f"Narrativas Carregadas pelo Autor", key="narrativa_box")    

        if st.session_state.narrativa is not None:
            col1, col2 = st.columns([1,1])  
            with col1:
                options_personagem = getPersonagens(st.session_state.autor, st.session_state.narrativa)
                st.session_state.personagem = st.selectbox("Selecione um Personagem:", options=options_personagem, index=0, 
                                            help=f"Personagens presentes na narrativa {st.session_state.narrativa}", key="personagem_box")    
            with col2:    
                options_fatos = getFatos(st.session_state.autor, st.session_state.narrativa)
                st.session_state.fato = st.selectbox("Selecione um Fato:", options=options_fatos, index=0, 
                                            help=f"Fatos presentes na narrativa {st.session_state.narrativa}")        

            st.markdown(":green-badge[:material/star: Selecione uma Modalidade:]")
            tab1, tab2, tab3 = st.tabs(["👶🏼 Iniciante", "🧒🏽 Intermediário", "👨🏾‍🦳 Avançado"])
            with tab1:
                st.header("Modo Iniciante 👶🏼")
                containerIniciante = st.container(border=True)            
                with containerIniciante:                
                    st.subheader("Qual estória devemos contar?")
                    col1_select, col2_select, col3_select = st.columns([1,1,1]) 
                    with col1_select:
                        clicked_select1 = product_card(
                            product_name=f"Uma estória com foco no Personagem",
                            description=f"Conte a estória de {st.session_state.personagem}",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00070_.png",
                            key="select_card1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_select1:
                            st.session_state.tipo_estoria = "Personagem"   
                                                                                
                    with col2_select:                        
                        clicked_select2 = product_card(
                            product_name="Uma estória baseada no Texto Completo",
                            description=f"Utilize todo o conteúdo de \"{st.session_state.narrativa}\" para criar uma nova estória." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00108_.png",
                            key="select_card2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select2:
                            st.session_state.tipo_estoria = "Texto" 
                            
                    with col3_select:   
                        clicked_select3 = product_card(
                            product_name=f"Uma estória com foco em um Fato",
                            description=f"Conte a estória com foco no fato  \"{st.session_state.fato}\"",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00115_.png",
                            key="select_card3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select3:
                            st.session_state.tipo_estoria = "Fato"                                                                         

                    st.subheader("Como devemos contar a estória?")     
                    
                    col1_how, col2_how, col3_how = st.columns([1,1,1]) 
                    with col1_how:
                        clicked_basic = product_card(
                            product_name=f"Impacto Logo no Início",
                            description=f"Comece a estória com tudo! Essa estrutura é perfeita para redes sociais, vídeos curtos ou textos que precisam fisgar o leitor em segundos.",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_01059_.png",
                            key="basic_card1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_basic:
                            st.session_state.recurso_estoria = "IMPACTO_INICIO"     
                                                    
                    with col2_how:                        
                        clicked_basic2 = product_card(
                            product_name="Minha Verdade",
                            description=f"Não é só um desabafo: é um posicionamento com narrativa. Funciona muito bem para influenciadores e especialistas." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_01121_.png",
                            key="basic_card2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_basic2:
                            st.session_state.recurso_estoria = "MINHA_VERDADE" 
                            
                    with col3_how:   
                        clicked_basic3 = product_card(
                            product_name=f"Bastidores ou Segredos",
                            description=f"Revele algo inesperado, pouco falado ou mal compreendido sobre seu tema. Essa estrutura desperta curiosidade e posiciona você como alguém que traz conteúdo original.",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_01128_.png",
                            key="basic_card3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_basic3:
                            st.session_state.recurso_estoria = "BASTIDORES_SEGREDOS"                                   

                    col4_how, col5_how, col6_how = st.columns([1,1,1]) 
                    with col4_how:
                        clicked_basic = product_card(
                            product_name=f"Ordem Cronológica",
                            description=f"Essa estrutura é ideal para mostrar uma sequência de eventos, como a trajetória de uma marca, a evolução de uma ideia, ou o passo a passo de uma jornada.",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00359_.png",
                            key="basic_card4",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_basic:
                            st.session_state.recurso_estoria = "ORDEM_CRONOLOGICA"                                
                    with col5_how:                        
                        clicked_basic2 = product_card(
                            product_name="Queda e Superação",
                            description=f"O personagem (ou você) enfrenta um desafio, passa por uma crise, mas encontra uma saída e termina em um lugar melhor. Boa para estórias inspiradoras e lições de vida." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00326_.png",
                            key="basic_card5",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_basic2:
                            st.session_state.recurso_estoria = "QUEDA_SUPERACAO" 
                            
                    with col6_how:   
                        clicked_basic3 = product_card(
                            product_name=f"Aprendi do Jeito Difícil",
                            description=f"Conte sobre um erro que cometeu e como ele te ensinou algo valioso. Isso aproxima você do público e passa autoridade de forma autêntica.",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00367_.png",
                            key="basic_card6",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_basic3:
                            st.session_state.recurso_estoria = "APRENDI_DIFICIL"                                   
                    
                    st.subheader("Como você deseja usar sua estória?")  
                    col1_uso, col2_uso, col3_uso = st.columns([1,1,1]) 
                    with col1_uso:
                        clicked_uso_estoria1 = product_card(
                            product_name=f"Rede Social",
                            description=f"A estória em formato de vídeo curto para ser divulgada em Plataformas Sociais",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00271_.png",
                            key="uso_estoria1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_uso_estoria1:
                            st.session_state.uso_estoria = "REDE_SOCIAL"
                                                        
                    with col2_uso:                        
                        clicked_uso_estoria2 = product_card(
                            product_name="PodCast",
                            description=f"A estória em formato de áudio para ser aproveitada em um PodCast ou Similar." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00302_.png",
                            key="uso_estoria2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_estoria2:
                            st.session_state.uso_estoria = "PODCAST" 
                            
                    with col3_uso:   
                        clicked_uso_estoria3 = product_card(
                            product_name=f"Conteúdo de Artefato",
                            description=f"A estória em formato de Texto para ser incluído em livros, panfletos, WebSites, etc..",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00327_.png",
                            key="uso_estoria3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_estoria3:
                            st.session_state.uso_estoria = "CONTEUDO"                 

            with tab2:
                st.header("Modo Intermediário 🧒🏽")
                containerEstrutura = st.container(border=True)            
                with containerEstrutura:
                    st.subheader("Qual estória devemos contar?")
                    col1_select_intermed, col2_select_intermed, col3_select_intermed = st.columns([1,1,1]) 
                    with col1_select_intermed:
                        clicked_select_intermed1 = product_card(
                            product_name=f"Uma estória com foco no Personagem",
                            description=f"Conte a estória de {st.session_state.personagem}",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00070_.png",
                            key="select_intermed_card1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_select_intermed1:
                            st.session_state.tipo_estoria = "Personagem"   
                                                                                
                    with col2_select_intermed:                        
                        clicked_select_intermed2 = product_card(
                            product_name="Uma estória baseada no Texto Completo",
                            description=f"Utilize todo o conteúdo de \"{st.session_state.narrativa}\" para criar uma nova estória." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00108_.png",
                            key="select_intermed_card2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select_intermed2:
                            st.session_state.tipo_estoria = "Texto" 
                            
                    with col3_select_intermed:   
                        clicked_select_intermed3 = product_card(
                            product_name=f"Uma estória com foco em um Fato",
                            description=f"Conte a estória com foco no fato  \"{st.session_state.fato}\"",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00115_.png",
                            key="select_intermed_card3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select_intermed3:
                            st.session_state.tipo_estoria = "Fato"                                                                         
                    
                    col1_est, col2_est = st.columns([1,1])
                    with col1_est:
                        st.subheader("Modelos de Estrutura de Conteúdo")
                        st.markdown(":green-badge[:material/star: O \"Formato\" da sua estória - **Habilite somente um grupo desse bloco**.]")
                    with col2_est:
                        with st.expander(f"**📖 O que é isso?**"):                    
                            st.markdown('''
                                        A estrutura é a **base da sua estória ou conteúdo**.  
                                        Pense como o “formato” que organiza o que você vai contar.                                            
                                        Selecione um dos seguintes Grupos de Estruturas para formatar sua estória. 
                                        ''')                                                                        
                    
                    st.markdown(":gray-badge[:material/Start: **Grupo 1: Foque no Começo da Estória**]")
                    col0_comecar, col1_comecar, col2_comecar = st.columns([1,4,4])    
                    with col0_comecar:
                        on_comecar = st.toggle("Habilitar", key="t1", help=f"Clique para Habilitar o Grupo 1.", on_change=toggle_change_manager)     
                    with col1_comecar:
                        st.session_state.como_comecar = st.selectbox("**Como você quer começar?**", options=getComoComecar(), index=0, 
                                                    help=f"Selecione o melhor jeito de começar sua estória.", key="como_comecar_box")                        
                    with col2_comecar:
                        if st.session_state.como_comecar is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.como_comecar}?**"):
                                st.markdown(getComoComecarTexto(st.session_state.como_comecar))                     
                        
                    st.markdown(":gray-badge[:material/Start: **Grupo 2: Foque na Organização da estória**]")
                    col0_organizar, col1_organizar, col2_organizar = st.columns([1,4,4])    
                    with col0_organizar:
                        on_organizar = st.toggle("Habilitar", key="t2", help=f"Clique para Habilitar o Grupo 2.", on_change=toggle_change_manager)                        
                    with col1_organizar:
                        st.session_state.como_organizar = st.selectbox("**Como você quer organizar o Texto?**", options=getComoOrganizar(), index=0, 
                                                    help=f"Selecione o melhor jeito de organizar sua estória.", key="como_organizar_box")                        
                    with col2_organizar:
                        if st.session_state.como_organizar is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.como_organizar}?**"):
                                st.markdown(getComoOrganizarTexto(st.session_state.como_organizar))  

                    st.markdown(":gray-badge[:material/Start: **Grupo 3: Foque na Proposta de Valor**]")
                    col0_ensinar, col1_ensinar, col2_ensinar = st.columns([1,4,4])
                    with col0_ensinar:
                        on_ensinar = st.toggle("Habilitar", key="t3", help=f"Clique para Habilitar o Grupo 3.", on_change=toggle_change_manager)                            
                    with col1_ensinar:
                        st.session_state.como_ensinar = st.selectbox("**Como gerar Valor?**", options=getComoEnsinar(), index=0, 
                                                    help=f"Selecione o melhor jeito de gerar Valor para sua estória.", key="como_ensinar_box")                        
                    with col2_ensinar:
                        if st.session_state.como_ensinar is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.como_ensinar}?**"):
                                st.markdown(getComoEnsinarTexto(st.session_state.como_ensinar))

                    col1_rec, col2_rec = st.columns([1,1]) 
                    with col1_rec:
                        st.subheader("Modelos de Recursos de Conteúdo")
                        st.markdown(":green-badge[:material/star: Os \"Temperos\" da sua estória - **Habilite somente um grupo desse bloco**.]")
                    with col2_rec:
                        with st.expander(f"**📖 O que é isso?**"):                    
                            st.markdown('''
                                        Os recursos deixam tudo mais interessante e efetivamente "temperam" sua estória.                                     
                                        ''') 
                    st.markdown(":gray-badge[:material/Start: **Grupo 4: Deixe sua narrativa mais visual, criativa ou envolvente.**]")
                    col0_formas_contar, col1_formas_contar, col2_formas_contar = st.columns([1,4,4])    
                    with col0_formas_contar:
                        on_formas_contar = st.toggle("Habilitar",key="t4", on_change=toggle_change_manager,  help=f"Clique para Habilitar o Grupo 4.")                            
                    with col1_formas_contar:
                        st.session_state.formas_contar = st.selectbox("**Formas de Contar**", options=getFormasContar(), index=0, 
                                                    help=f"Selecione o melhor jeito de contar sua estória.", key="como_contar_box")                        
                    with col2_formas_contar:
                        if st.session_state.formas_contar is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.formas_contar}?**"):
                                st.markdown(getFormasContarTexto(st.session_state.formas_contar))                                                

                    st.markdown(":gray-badge[:material/Start: **Grupo 5: Prenda a atenção e provoque o leitor.**]")
                    col0_eng_cur, col1_eng_cur, col2_eng_cur = st.columns([1,4,4])    
                    with col0_eng_cur:
                        on_engajamento_curiosidade = st.toggle("Habilitar",key="t5", on_change=toggle_change_manager, help=f"Clique para Habilitar o Grupo 5.")                            
                    with col1_eng_cur:
                        st.session_state.engajamento_curiosidade = st.selectbox("**Engajamento e Curiosidade**", options=getEngajamentoCuriosidade(), index=0, 
                                                    help=f"Selecione o melhor jeito de gerar Engajamento e Curiosidade.", key="como_engajar_curiosidade_box")                        
                    with col2_eng_cur:
                        if st.session_state.engajamento_curiosidade is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.engajamento_curiosidade}?**"):
                                st.markdown(getEngajamentoCuriosidadeTexto(st.session_state.engajamento_curiosidade))    
                                
                    st.markdown(":gray-badge[:material/Start: **Grupo 6: Use sua personalidade como diferencial.**]")
                    col0_tom_voz, col1_tom_voz, col2_tom_voz = st.columns([1,4,4])    
                    with col0_tom_voz:
                        on_tom_voz = st.toggle("Habilitar",key="t6", on_change=toggle_change_manager, help=f"Clique para Habilitar o Grupo 6.")                            
                    with col1_tom_voz:
                        st.session_state.tom_voz = st.selectbox("**Tom e Voz**", options=getTomVoz(), index=0, 
                                                    help=f"Selecione o melhor jeito de dar o tom para sua estória.", key="como_tom_voz_box")                        
                    with col2_tom_voz:
                        if st.session_state.tom_voz is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.tom_voz}?**"):
                                st.markdown(getTomVozTexto(st.session_state.tom_voz))     

                    st.markdown(":gray-badge[:material/Start: **Grupo 7: Passe segurança, ensine melhor, informe com base.**]")
                    col0_clareza, col1_clareza, col2_clareza = st.columns([1,4,4])    
                    with col0_clareza:
                        on_clareza = st.toggle("Habilitar",key="t7", on_change=toggle_change_manager, help=f"Clique para Habilitar o Grupo 7.")                            
                    with col1_clareza:
                        st.session_state.clareza_autoridade = st.selectbox("**Clareza e Autoridade**", options=getClarezaAutoridade(), index=0, 
                                                    help=f"Selecione o melhor jeito de demonstrar clareza e autoridade.", key="como_clareza_autoridade_box")                        
                    with col2_clareza:
                        if st.session_state.clareza_autoridade is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.clareza_autoridade}?**"):
                                st.markdown(getClarezaAutoridadeTexto(st.session_state.clareza_autoridade))    
                                 
                    
                    st.markdown(":gray-badge[:material/Start: **Grupo 8: Mostre quem você é e com quem você fala.**]")            
                    col0_conexao, col1_conexao, col2_conexao = st.columns([1,4,4])    
                    with col0_conexao:
                        on_conexao = st.toggle("Habilitar",key="t8", on_change=toggle_change_manager, help=f"Clique para Habilitar o Grupo 8.")                            
                    with col1_conexao:
                        st.session_state.posicionamento_conexao = st.selectbox("**Posicionamento e Conexão**", options=getPosicionamentoConexao(), index=0, 
                                                    help=f"Selecione o melhor jeito de demonstrar Conexão com o Leitor.", key="como_conexao_box")                        
                    with col2_conexao:
                        if st.session_state.posicionamento_conexao is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.posicionamento_conexao}?**"):
                                st.markdown(getPosicionamentoConexaoTexto(st.session_state.posicionamento_conexao))                                                                                                                                                                    

                    st.markdown(":gray-badge[:material/Start: **Grupo 9: Recursos Extras.**]")
                    col0_recursos, col1_recursos, col2_recursos = st.columns([1,4,4])    
                    with col0_recursos:
                        on_recursos = st.toggle("Habilitar",key="t9", on_change=toggle_change_manager, help=f"Clique para Habilitar o Grupo 9.")                            
                    with col1_recursos:
                        st.session_state.recursos_extras = st.selectbox("**Recursos Extras**", options=getRecursosExtras(), index=0, 
                                                    help=f"Adicione elementos interessantes à narrativa.", key="como_recursos_box")                        
                    with col2_recursos:
                        if st.session_state.recursos_extras is not None:
                            with st.expander(f"**📖 O que significa {st.session_state.recursos_extras}?**"):
                                st.markdown(getRecursosExtrasTexto(st.session_state.recursos_extras))  

                    st.subheader("Como você deseja usar sua estória?")  
                    col1_uso_intermed, col2_uso_intermed, col3_uso_intermed = st.columns([1,1,1]) 
                    with col1_uso_intermed:
                        clicked_uso_intermed_estoria1 = product_card(
                            product_name=f"Rede Social",
                            description=f"A estória em formato de vídeo curto para ser divulgada em Plataformas Sociais",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00271_.png",
                            key="uso_intermed_estoria1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_uso_intermed_estoria1:
                            st.session_state.uso_estoria = "REDE_SOCIAL"
                                                        
                    with col2_uso_intermed:                        
                        clicked_uso_intermed_estoria2 = product_card(
                            product_name="PodCast",
                            description=f"A estória em formato de áudio para ser aproveitada em um PodCast ou Similar." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00302_.png",
                            key="uso_intermed_estoria2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_intermed_estoria2:
                            st.session_state.uso_estoria = "PODCAST" 
                            
                    with col3_uso_intermed:   
                        clicked_uso_intermed_estoria3 = product_card(
                            product_name=f"Conteúdo de Artefato",
                            description=f"A estória em formato de Texto para ser incluído em livros, panfletos, WebSites, etc..",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00327_.png",
                            key="uso_intermed_estoria3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_intermed_estoria3:
                            st.session_state.uso_estoria = "CONTEUDO"   
                
        
            with tab3:
                st.header("Modo Avançado 👨🏾‍🦳")
                containerAvancado = st.container(border=True)            
                with containerAvancado:    
                    st.subheader("Qual estória devemos contar?")
                    col1_select_avancad, col2_select_avancad, col3_select_avancad = st.columns([1,1,1]) 
                    with col1_select_avancad:
                        clicked_select_avancad1 = product_card(
                            product_name=f"Uma estória com foco no Personagem",
                            description=f"Conte a estória de {st.session_state.personagem}",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00070_.png",
                            key="select_avancad_card1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_select_avancad1:
                            st.session_state.tipo_estoria = "Personagem"   
                                                                                
                    with col2_select_avancad:                        
                        clicked_select_avancad2 = product_card(
                            product_name="Uma estória baseada no Texto Completo",
                            description=f"Utilize todo o conteúdo de \"{st.session_state.narrativa}\" para criar uma nova estória." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00108_.png",
                            key="select_avancad_card2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select_avancad2:
                            st.session_state.tipo_estoria = "Texto" 
                            
                    with col3_select_avancad:   
                        clicked_select_avancad3 = product_card(
                            product_name=f"Uma estória com foco em um Fato",
                            description=f"Conte a estória com foco no fato  \"{st.session_state.fato}\"",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00115_.png",
                            key="select_avancad_card3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_select_avancad3:
                            st.session_state.tipo_estoria = "Fato"                                                                         
                    
                    col1_est, col2_est = st.columns([1,1])
                    with col1_est:
                        st.subheader("Modelos de Estrutura de Conteúdo")
                        st.markdown(":green-badge[:material/star: O \"Formato\" da sua estória - **Habilite somente um grupo desse bloco**.]")
                    with col2_est:
                        with st.expander(f"**📖 O que é isso?**"):                    
                            st.markdown('''
                                        A estrutura é a **base da sua estória ou conteúdo**.  
                                        Pense como o “formato” que organiza o que você vai contar.                                            
                                        Selecione um dos seguintes Grupos de Estruturas para formatar sua estória. 
                                        ''')                    
                                        
                    st.markdown(":gray-badge[:material/Start: **História em Ordem Cronológica**]")
                    col0_linha_tempo, col1_linha_tempo = st.columns([1,4])    
                    with col0_linha_tempo:
                        on_linha_tempo = st.toggle("Habilitar", key="e1", help=f"Clique para Habilitar o uso da Linha do Tempo.", on_change=toggle_estrutura_avancada)     
                    with col1_linha_tempo:
                        st.markdown("Conte a sua história seguindo a ordem dos acontecimentos, do começo ao fim. Essa estrutura é ideal para mostrar uma sequência de eventos, como a trajetória de uma marca, a evolução de uma ideia, ou o passo a passo de uma jornada.")                       

                    st.markdown(":gray-badge[:material/Start: **Montanha-Russa Emocional**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_montanha_russa = st.toggle("Habilitar", key="e2", help=f"Clique para Habilitar o uso da Alternância Emocional.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Aqui, sua narrativa vai alternar entre altos e baixos emocionais. Um momento difícil dá espaço a uma conquista, ou uma tensão é quebrada com humor. Ideal para engajar o público e criar conexão emocional.")                       

                    st.markdown(":gray-badge[:material/Start: **Impacto Logo no Início**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_impacto_inicio = st.toggle("Habilitar", key="e3", help=f"Clique para Habilitar o uso de Lead Forte.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Você começa com tudo: uma revelação surpreendente, uma pergunta intrigante ou algo que prende a atenção de cara. Essa estrutura é perfeita para redes sociais, vídeos curtos ou textos que precisam fisgar o leitor em segundos.")                       

                    st.markdown(":gray-badge[:material/Start: **Queda e Superação**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_queda_superacao = st.toggle("Habilitar", key="e4", help=f"Clique para Habilitar o uso do Homem no Buraco.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("A história começa bem, mas algo dá errado. O personagem (ou você) enfrenta um desafio, passa por uma crise, mas encontra uma saída e termina em um lugar melhor. Boa para histórias inspiradoras e lições de vida.")                       

                    st.markdown(":gray-badge[:material/Start: **Descoberta de um Valor Escondido**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_valor_escondido = st.toggle("Habilitar", key="e5", help=f"Clique para Habilitar o uso dos Trapos à Riqueza.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Tudo começa com algo que parece ruim, inútil ou sem valor. Mas ao longo da história, esse \"problema\" se revela uma grande força. Excelente para transformar percepções e mostrar crescimento.")                       

                    st.markdown(":gray-badge[:material/Start: **Tentativa e Erro**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_tentativa_erro = st.toggle("Habilitar", key="e6", help=f"Clique para Habilitar o uso da Solução Errada.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Você começa com um problema e tenta uma solução que parece funcionar... mas não funciona. Depois de um revés, encontra o caminho certo. Ideal para mostrar aprendizado, evolução e autenticidade.")                       

                    st.markdown(":gray-badge[:material/Start: **Guia Prático**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_guia_pratico = st.toggle("Habilitar", key="e7", help=f"Clique para Habilitar o uso do Passo a Passo.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Mostre como fazer algo, do início ao fim, em etapas claras. Ideal para tutoriais, dicas profissionais, ou mostrar seu processo criativo.")                       

                    st.markdown(":gray-badge[:material/Start: **Transformação Visível**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_transformacao_visivel = st.toggle("Habilitar", key="e8", help=f"Clique para Habilitar o uso de Antes e Depois.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Mostre uma mudança: de uma situação inicial para um resultado final impressionante. Pode ser uma mudança pessoal, profissional, estética ou de mentalidade. Muito usado por coaches, terapeutas, criadores de estilo ou fitness.")                       

                    st.markdown(":gray-badge[:material/Start: **Comece com uma Pergunta**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_comece_pergunta = st.toggle("Habilitar", key="e9", help=f"Clique para Habilitar o uso de Pergunta e Resposta.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Inicie com uma dúvida comum do seu público e responda de forma clara, objetiva ou criativa. Boa para criar conexão direta e gerar engajamento rápido.")                       


                    st.markdown(":gray-badge[:material/Start: **Opinião com Contexto**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_opiniao_contexto = st.toggle("Habilitar", key="e10", help=f"Clique para Habilitar o uso do Minha Verdade.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Compartilhe sua visão sobre um tema com base na sua vivência ou experiência. Não é só um desabafo: é um posicionamento com história. Funciona muito bem para influenciadores e especialistas.")                       

                    st.markdown(":gray-badge[:material/Start: **Aprendi do Jeito Difícil**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_jeito_dificil = st.toggle("Habilitar", key="e11", help=f"Clique para Habilitar o uso do Erro que Virei Mestre.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Conte sobre um erro que cometeu e como ele te ensinou algo valioso. Isso aproxima você do público e passa autoridade de forma autêntica.")                       

                    st.markdown(":gray-badge[:material/Start: **Bastidores ou Segredos**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_bastidores_segredos = st.toggle("Habilitar", key="e12", help=f"Clique para Habilitar o uso do O que Ninguém Te Conta.", on_change=toggle_estrutura_avancada)     
                    with col1:
                        st.markdown("Revele algo inesperado, pouco falado ou mal compreendido sobre seu tema. Essa estrutura desperta curiosidade e posiciona você como alguém que traz conteúdo original.")                       
                    col1_rec, col2_rec = st.columns([1,1]) 
                    with col1_rec:
                        st.subheader("Modelos de Recursos de Conteúdo")
                        st.markdown(":green-badge[:material/star: Os \"Temperos\" da sua estória.]")
                    with col2_rec:
                        with st.expander(f"**📖 O que é isso?**"):                    
                            st.markdown('''
                                        Os recursos deixam tudo mais interessante e efetivamente "temperam" sua estória.  Use algumas para dar uma maior variabilidade para a sua história.                                   
                                        ''') 
                    st.markdown(":gray-badge[:material/Start: **Formas de Contar: Recursos ajudam a deixar o conteúdo mais criativo ou visual - Habilite somente um grupo desse bloco.**]")
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_historia_rapida = st.toggle("Habilitar", key="r1", help=f"Clique para Habilitar o uso da História Rápida.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Use uma história curta ou inventada (real ou não) para explicar algo de forma mais envolvente.")                       

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_comparacao_simples = st.toggle("Habilitar", key="r2", help=f"Clique para Habilitar o uso do Comparação Simples .", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Compare o tema com algo que todo mundo entende. Pode ser uma metáfora, um símbolo ou até dar “vida” a um conceito.")                       

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r3", help=f"Clique para Habilitar o uso do Antes e Depois.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Mostre a diferença entre duas situações. Pode ser o que mudou, melhorou ou piorou. Isso dá força à sua mensagem.")                       

                    st.markdown(":gray-badge[:material/Start: **Engajamento e Curiosidade: Recursos que criam expectativa, envolvem ou desafiam o leitor - Habilite somente um grupo desse bloco.**]")

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r4", help=f"Clique para Habilitar o uso do Pergunta ou Curiosidade.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Faça uma pergunta que desperte o interesse ou sugira que você tem uma informação escondida.")                       


                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r5", help=f"Clique para Habilitar o uso de Surpresa ou Reviravolta.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Traga algo inesperado ou mude o rumo do conteúdo no final. Isso segura a atenção.")       
                        
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r6", help=f"Clique para Habilitar o uso de Gancho Final.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Termine com algo que deixa o leitor querendo mais: uma pergunta, promessa ou continuação.")                                                    


                    st.markdown(":gray-badge[:material/Start: **Tom e Voz: Escolhas que afetam o estilo, humor ou forma de falar - Habilite somente um grupo desse bloco.**]")
                    
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r7", help=f"Clique para Habilitar o uso de Tom Pessoal.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Use sua voz. Fale como você. Pode ser contando em primeira pessoa, explicando diretamente ao leitor ou fazendo piada com a própria narrativa.")                      

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r8", help=f"Clique para Habilitar o uso de Alívio Cômico.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Use humor para deixar tudo mais leve. Pode ser uma piada, uma quebra engraçada ou algo inesperado.")                      


                    st.markdown(":gray-badge[:material/Start: **Clareza e Autoridade: Recursos para reforçar credibilidade, instruir ou informar melhor - Habilite somente um grupo desse bloco.**]")

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r9", help=f"Clique para Habilitar o uso de Contexto Rápido.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Explique o básico de forma simples: o que está acontecendo? Onde? Com quem? Por quê?")   
                        
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r10", help=f"Clique para Habilitar o uso de Prova com Dados .", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Traga um número ou dado interessante que sustente seu ponto ou surpreenda.")   
                        
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r11", help=f"Clique para Habilitar o uso de Dica Prática.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Liste passos fáceis ou ofereça uma solução rápida. Ideal para conteúdos úteis e objetivos.")  
                        
                    st.markdown(":gray-badge[:material/Start: **Posicionamento: Recursos que ajudam o criador a tomar uma posição clara no conteúdo - Habilite somente um grupo desse bloco.**]")                                                                                        

                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r12", help=f"Clique para Habilitar o uso de Discordância Construtiva.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Mostre um ponto de vista diferente do comum, questione ideias ou se posicione contra algo — com respeito e argumentos.")   
                        
                    col0, col1 = st.columns([1,4])    
                    with col0:
                        on_antes_depois = st.toggle("Habilitar", key="r13", help=f"Clique para Habilitar o uso de Conexão com o Leitor.", on_change=toggle_recurso_avancado)     
                    with col1:
                        st.markdown("Mostre como o conteúdo tem a ver com quem está lendo e incentive a pessoa a comentar, pensar ou agir.")  

                    st.subheader("Como você deseja usar sua estória?")  
                    col1_uso_avanc, col2_uso_avanc, col3_uso_avanc = st.columns([1,1,1]) 
                    with col1_uso_avanc:
                        clicked_uso_avanc_estoria1 = product_card(
                            product_name=f"Rede Social",
                            description=f"A estória em formato de vídeo curto para ser divulgada em Plataformas Sociais",
                            price=f"",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00271_.png",
                            key="uso_avanc_estoria1",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",                        
                        )

                        if clicked_uso_avanc_estoria1:
                            st.session_state.uso_estoria = "REDE_SOCIAL"
                                                        
                    with col2_uso_avanc:                        
                        clicked_uso_avanc_estoria2 = product_card(
                            product_name="PodCast",
                            description=f"A estória em formato de áudio para ser aproveitada em um PodCast ou Similar." ,
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00302_.png",
                            key="uso_avanc_estoria2",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_avanc_estoria2:
                            st.session_state.uso_estoria = "PODCAST" 
                            
                    with col3_uso_avanc:   
                        clicked_uso_avanc_estoria3 = product_card(
                            product_name=f"Conteúdo de Artefato",
                            description=f"A estória em formato de Texto para ser incluído em livros, panfletos, WebSites, etc..",
                            price="",
                            product_image="https://alegoria.nyc3.digitaloceanspaces.com/COMUM/IMAGENS/MarkuryFLUX_00327_.png",
                            key="uso_avanc_estoria3",
                            picture_position="right",
                            image_aspect_ratio="16/9",
                            image_object_fit="cover",
                        )

                        if clicked_uso_avanc_estoria3:
                            st.session_state.uso_estoria = "CONTEUDO"   


        
        col1, col2, col3, col4 = st.columns([1,1,1,1])    
        with col1:
            st.session_state.openai_model = st.selectbox("Modelo OpenAI:",OPENAI_MODELS, key="openai_model_box")
        with col2:  
            st.session_state.anthropic_model = st.selectbox("Modelo Anthropic:",ANTHROPIC_MODELS,key="anthropic_model_box")  
        with col3:              
            st.session_state.deepseek_model = st.selectbox("Modelo DeepSeek:",DEEPSEEK_MODELS,key="deepseek_model_box")  
        with col4:              
            st.session_state.gemini_model = st.selectbox("Modelo Gemini:",GEMINI_MODELS,key="gemini_model_box")
            
        col1, col2, col3 = st.columns([1,1,1])  
        with col1:
            st.session_state.idioma = st.selectbox("Selecione o Idioma:",("PORTUGUES", "INGLES", "ESPANHOL", "ITALIANO", "FRANCES"),key="idiomas_box")
        with col2:
            st.session_state.provedor = st.selectbox("Selecione um Provedor de Modelos de IA:",("OPENAI", "ANTHROPIC", "DEEPSEEK", "GEMINI"),key="provedores_box")    
        with col3:
            st.session_state.modo_narracao = st.selectbox("Selecione um Modo de Narração:",("Iniciante", "Intermediário", "Avançado"),key="modo_narracao_box")    

        containerSumario = st.container(border=True)
        
        with containerSumario:
            st.subheader("Sumário")
            if (st.session_state.modo_narracao == "Iniciante"): 
                st.write(f"Proposta Narrativa: {st.session_state.narrativa}")
                st.write(f"Tipo de Historia: {st.session_state.tipo_estoria}")
                st.write(f"Recurso de Historia: {st.session_state.recurso_estoria}")
                st.write(f"Uso de Historia: {st.session_state.uso_estoria}")
                st.write(f"Idioma: {st.session_state.idioma}")
                st.write(f"Modo de Narração:  {st.session_state.modo_narracao}")
            if (st.session_state.modo_narracao == "Intermediário"):    
                st.write(f"Proposta Narrativa: {st.session_state.narrativa}")
                st.write(f"Tipo de Historia: {st.session_state.tipo_estoria}")
                if st.session_state.t1:
                    st.write(f"Estrutura: {st.session_state.como_comecar}")
                if st.session_state.t2:
                    st.write(f"Estrutura: {st.session_state.como_organizar}")
                if st.session_state.t3:        
                    st.write(f"Estrutura: {st.session_state.como_ensinar}")
                if st.session_state.t4: 
                    st.write(f"Recurso: {st.session_state.formas_contar}")
                if st.session_state.t5:
                    st.write(f"Recurso: {st.session_state.engajamento_curiosidade}")    
                if st.session_state.t6:
                    st.write(f"Recurso: {st.session_state.tom_voz}")
                if st.session_state.t7:
                    st.write(f"Recurso: {st.session_state.clareza_autoridade}")
                if st.session_state.t8:
                    st.write(f"Recurso: {st.session_state.posicionamento_conexao}")
                if st.session_state.t9:   
                    st.write(f"Recurso: {st.session_state.recursos_extras}")    
                st.write(f"Uso de Historia: {st.session_state.uso_estoria}")
                st.write(f"Idioma: {st.session_state.idioma}")
                st.write(f"Modo de Narração:  {st.session_state.modo_narracao}")  
            if (st.session_state.modo_narracao == "Avançado"):
                st.write(f"Proposta Narrativa: {st.session_state.narrativa}")
                st.write(f"Tipo de Historia: {st.session_state.tipo_estoria}")
                st.write(f"######## ESTRUTURAS #######")
                if st.session_state.e1:
                    st.write(f"Estrutura: História em Ordem Cronológica")
                if st.session_state.e2:
                    st.write(f"Estrutura: Montanha-Russa Emocional")
                if st.session_state.e3:        
                    st.write(f"Estrutura: Impacto Logo no Início")
                if st.session_state.e4: 
                    st.write(f"Estrutura: Queda e Superação")
                if st.session_state.e5:
                    st.write(f"Estrutura: Descoberta de um Valor Escondido")    
                if st.session_state.e6:
                    st.write(f"Estrutura: Tentativa e Erro")
                if st.session_state.e7:
                    st.write(f"Estrutura: Guia Prático")
                if st.session_state.e8:
                    st.write(f"Estrutura: Transformação Visível")
                if st.session_state.e9:   
                    st.write(f"Estrutura: Comece com uma Pergunta")    
                if st.session_state.e10:   
                    st.write(f"Estrutura: Opinião com Contexto")  
                if st.session_state.e11:   
                    st.write(f"Estrutura: Aprendi do Jeito Difícil")  
                if st.session_state.e12:   
                    st.write(f"Estrutura: Bastidores ou Segredos")                                                                          
                st.write(f"######## RECURSOS #######")     
                if st.session_state.r1:
                    st.write(f"Recurso: História Rápida")
                if st.session_state.r2:
                    st.write(f"Recurso: Comparação Simples")
                if st.session_state.r3:        
                    st.write(f"Recurso: Antes e Depois")
                if st.session_state.r4: 
                    st.write(f"Recurso: Queda e Superação")
                if st.session_state.r5:
                    st.write(f"Recurso: Surpresa ou Reviravolta")    
                if st.session_state.r6:
                    st.write(f"Recurso: Gancho Final")
                if st.session_state.r7:
                    st.write(f"Recurso: Tom Pessoal")
                if st.session_state.r8:
                    st.write(f"Recurso: Alívio Cômico")
                if st.session_state.r9:   
                    st.write(f"Recurso: Contexto Rápido")    
                if st.session_state.r10:   
                    st.write(f"Recurso: Prova com Dados")  
                if st.session_state.r11:   
                    st.write(f"Recurso: Dica Prática")  
                if st.session_state.r12:   
                    st.write(f"Recurso: Discordância Construtiva")                                                                          
                if st.session_state.r13:   
                    st.write(f"Recurso: Conexão com o Leitor")                                                                          

                st.write(f"Uso de Historia: {st.session_state.uso_estoria}")
                st.write(f"Idioma: {st.session_state.idioma}")
                st.write(f"Modo de Narração:  {st.session_state.modo_narracao}")
                         
            

    if st.button("Gerar Algumas Propostas de Estórias", type="primary"):
        if st.session_state.openai_api_key is None or st.session_state.anthropic_api_key is None or st.session_state.gemini_api_key is None or st.session_state.deepseek_api_key is None:
            st.write(digitaPrompt("Please add API key to continue."))
            st.stop()        
        results = []
     
        prompt = ""
        
        
        if st.session_state.modo_narracao == "Avançado":
            fatos = carrega_fatos(st.session_state.narrativa, st.session_state.personagem, st.session_state.autor)    
            recurso_iniciante = getPromptRecursoIniciante(st.session_state.recurso_estoria) 
            uso_estoria = getPromptUsoHistoria(st.session_state.uso_estoria)  
            estruturas = getEstruturasAvancadas(st.session_state.e1, 
                                                st.session_state.e2, 
                                                st.session_state.e3, 
                                                st.session_state.e4, 
                                                st.session_state.e5, 
                                                st.session_state.e6, 
                                                st.session_state.e7, 
                                                st.session_state.e8, 
                                                st.session_state.e9, 
                                                st.session_state.e10, 
                                                st.session_state.e11, 
                                                st.session_state.e12)
            
            recursos = getRecursosAvancados(st.session_state.r1, 
                                                st.session_state.r2, 
                                                st.session_state.r3, 
                                                st.session_state.r4, 
                                                st.session_state.r5, 
                                                st.session_state.r6, 
                                                st.session_state.r7, 
                                                st.session_state.r8, 
                                                st.session_state.r9, 
                                                st.session_state.r10, 
                                                st.session_state.r11, 
                                                st.session_state.r12,
                                                st.session_state.r13)            

            deps = SupportDependencies(st.session_state.narrativa, 
                                    st.session_state.personagem, 
                                    fatos,
                                    st.session_state.tipo_estoria, 
                                    uso_estoria,
                                    estruturas,
                                    recursos, 
                                    st.session_state.num_propostas,
                                    st.session_state.idioma)   
                     
            if (st.session_state.tipo_estoria == "Personagem"):
                prompt = getPromptPersonagemAvancado(COUNT=st.session_state.num_propostas, 
                                            PERSONAGEM=st.session_state.personagem, 
                                            RECURSO=recursos,
                                            ESTRUTURA=estruturas, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
            
            
            if (st.session_state.tipo_estoria == "Fato"):
                prompt = getPromptFatoAvancado(COUNT=st.session_state.num_propostas, 
                                            FATO=st.session_state.fato, 
                                            RECURSO=recursos,
                                            ESTRUTURA=estruturas, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
                
            if (st.session_state.tipo_estoria == "Texto"):
                prompt = getPromptTextoAvancado(COUNT=st.session_state.num_propostas, 
                                            RECURSO=recursos,
                                            ESTRUTURA=estruturas, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
                
        if st.session_state.modo_narracao == "Iniciante":
            estrutura = ""            
            fatos = carrega_fatos(st.session_state.narrativa, st.session_state.personagem, st.session_state.autor)    
            recurso_iniciante = getPromptRecursoIniciante(st.session_state.recurso_estoria) 
            uso_estoria = getPromptUsoHistoria(st.session_state.uso_estoria)  
            deps = SupportDependencies(st.session_state.narrativa, 
                                    st.session_state.personagem, 
                                    fatos,
                                    st.session_state.tipo_estoria, 
                                    uso_estoria,
                                    estrutura,
                                    recurso_iniciante, 
                                    st.session_state.num_propostas,
                                    st.session_state.idioma)
            
            
            
            if (st.session_state.tipo_estoria == "Personagem"):
                prompt = getPromptPersonagemIniciante(COUNT=st.session_state.num_propostas, 
                                            PERSONAGEM=st.session_state.personagem, 
                                            RECURSO_INICIANTE=recurso_iniciante, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
            
            
            if (st.session_state.tipo_estoria == "Fato"):
                prompt = getPromptFatoIniciante(COUNT=st.session_state.num_propostas, 
                                            FATO=st.session_state.fato, 
                                            RECURSO_INICIANTE=recurso_iniciante, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
                
            if (st.session_state.tipo_estoria == "Texto"):
                prompt = getPromptTextoIniciante(COUNT=st.session_state.num_propostas, 
                                            RECURSO_INICIANTE=recurso_iniciante, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)  
                                          
        if st.session_state.modo_narracao == "Intermediário":
            fatos = carrega_fatos(st.session_state.narrativa, st.session_state.personagem, st.session_state.autor) 
            uso_estoria = getPromptUsoHistoria(st.session_state.uso_estoria)
            # ESTRUTURAS
            estrutura = ""
            if st.session_state.t1:
                estrutura = getComoComecarTexto(st.session_state.como_comecar)
            if st.session_state.t2:
                estrutura = getComoOrganizarTexto(st.session_state.como_organizar)
            if st.session_state.t3:        
                estrutura = getComoEnsinarTexto(st.session_state.como_ensinar)
            # RECURSOS
            recurso = ""
            if st.session_state.t4: 
                recurso = getFormasContarTexto(st.session_state.formas_contar)
            if st.session_state.t5:
                recurso = getEngajamentoCuriosidadeTexto(st.session_state.engajamento_curiosidade)    
            if st.session_state.t6:
                recurso = getTomVozTexto(st.session_state.tom_voz)
            if st.session_state.t7:
                recurso = getClarezaAutoridadeTexto(st.session_state.clareza_autoridade)
            if st.session_state.t8:
                recurso = getPosicionamentoConexaoTexto(st.session_state.posicionamento_conexao)
            if st.session_state.t9:   
                recurso = getRecursosExtrasTexto(st.session_state.recursos_extras) 
            
            deps = SupportDependencies(st.session_state.narrativa, 
                                    st.session_state.personagem, 
                                    fatos,
                                    st.session_state.tipo_estoria, 
                                    uso_estoria,
                                    estrutura,
                                    recurso, 
                                    st.session_state.num_propostas,
                                    st.session_state.idioma)
            
            prompt = ""
            
            if (st.session_state.tipo_estoria == "Personagem"):
                prompt = getPromptPersonagemIntermediario(COUNT=st.session_state.num_propostas, 
                                            PERSONAGEM=st.session_state.personagem, 
                                            RECURSO=recurso,
                                            ESTRUTURA=estrutura, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
            
            
            if (st.session_state.tipo_estoria == "Fato"):
                prompt = getPromptFatoIntermediario(COUNT=st.session_state.num_propostas, 
                                            FATO=st.session_state.fato, 
                                            RECURSO=recurso,
                                            ESTRUTURA=estrutura, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
                
            if (st.session_state.tipo_estoria == "Texto"):
                prompt = getPromptTextoIntermediario(COUNT=st.session_state.num_propostas, 
                                            RECURSO=recurso,
                                            ESTRUTURA=estrutura, 
                                            USO_HISTORIA=uso_estoria, 
                                            FACTS=fatos, 
                                            IDIOMA=st.session_state.idioma)
        
        result = None
        
        if (st.session_state.provedor == "GEMINI"):
            st.write(digitaPrompt(f"🙅🏽‍♀️ Ok! A partir de agora vamos apresentar as propostas {st.session_state.narrativa}. Narrativas geradas com o Provedor {st.session_state.provedor} usando o modelo {st.session_state.gemini_model}" ))   
            st.session_state.modelGemini = GeminiModel(st.session_state.gemini_model, provider=GoogleGLAProvider(api_key=st.session_state.gemini_api_key))
            support_agent_gemini = Agent(  
                st.session_state.modelGemini, 
                deps_type=SupportDependencies,
                result_type=Extraction,  
                system_prompt=(  
                "Voce é um agente de suporte responsável por criar narrativas."            
                ),
                retries=2,
            )              
            with st.spinner(f"[GEMINI {st.session_state.gemini_model}] Gerando Propostas....", show_time=True):    
                result = await support_agent_gemini.run(prompt)
                while result is None:        
                    time.sleep(1)        

        if (st.session_state.provedor == "OPENAI"):
            st.write(digitaPrompt(f"🙅🏽‍♀️ Ok! A partir de agora vamos apresentar as propostas {st.session_state.narrativa}. Narrativas geradas com o Provedor {st.session_state.provedor} usando o modelo {st.session_state.openai_model}" ))   
            st.session_state.modelOpenAI = OpenAIModel(st.session_state.openai_model, provider=OpenAIProvider(api_key=st.session_state.openai_api_key))
            support_agent_openai = Agent(   
                st.session_state.modelOpenAI,
                deps_type=SupportDependencies,
                result_type=Extraction,  
                system_prompt=(  
                "Voce é um agente de suporte responsável por criar narrativas."            
                ),
                retries=2,
            )            
            with st.spinner(f"[OPENAI {st.session_state.openai_model}] Gerando Propostas....", show_time=True):    
                result = await support_agent_openai.run(prompt)
                while result is None:        
                    time.sleep(1)        
                    
        if (st.session_state.provedor == "ANTHROPIC"):
            st.write(digitaPrompt(f"🙅🏽‍♀️ Ok! A partir de agora vamos apresentar as propostas {st.session_state.narrativa}. Narrativas geradas com o Provedor {st.session_state.provedor} usando o modelo {st.session_state.anthropic_model}" ))   
            st.session_state.modelAnthropic  = AnthropicModel(st.session_state.anthropic_model, provider=AnthropicProvider(api_key=st.session_state.anthropic_api_key))
            support_agent_anthropic = Agent(  
                st.session_state.modelAnthropic, 
                deps_type=SupportDependencies,
                output_type=Extraction,  
                system_prompt=(  
                "Voce é um agente de suporte responsável por criar narrativas. "            
                ),
                retries=2,
            )              
            with st.spinner(f"[ANTHROPIC {st.session_state.anthropic_model}] Gerando Propostas....", show_time=True):    
                result = await support_agent_anthropic.run(prompt)
                while result is None:        
                    time.sleep(1)                         
        
        if (st.session_state.provedor == "DEEPSEEK"):
            st.write(digitaPrompt(f"🙅🏽‍♀️ Ok! A partir de agora vamos apresentar as propostas {st.session_state.narrativa}. Narrativas geradas com o Provedor {st.session_state.provedor} usando o modelo {st.session_state.deepseek_model}" ))   
            st.session_state.modelDeepseek = OpenAIModel(st.session_state.deepseek_model, provider=DeepSeekProvider(api_key=st.session_state.deepseek_api_key ),)
            support_agent_deepseek = Agent(  
                st.session_state.modelDeepseek, 
                deps_type=SupportDependencies,
                result_type=Extraction,  
                system_prompt=(  
                "Voce é um agente de suporte responsável por criar narrativas."            
                ),
                retries=2,
            )            
            with st.spinner(f"[DEEPSEEK {st.session_state.deepseek_model}] Gerando Propostas....", show_time=True):    
                result = await support_agent_deepseek.run(prompt)
                while result is None:        
                    time.sleep(1) 
                            
        with open("content223.txt", "w", encoding="utf-8") as f:
            f.write(str(result.output)) 
        with open("content223.txt", "r", encoding="utf-8") as file:
            # Read the contents of the file
            content = file.read()   
            content = content.strip() 
            # Regular expression to match each SupportResult block
            pattern = r"SupportResult\((.*?)\)"

            # Find all matches
            matches = re.findall(pattern, content, re.DOTALL)

            # Process each match into a dictionary
            
            for match in matches:
                fields = re.findall(r"(\w+)=\'(.*?)\'", match, re.DOTALL)
                result_dict = {key: value for key, value in fields}
                results.append(result_dict)
        st.session_state['narrativas'] = results
        st.write(st.session_state['narrativas']) 
        escolheNarrativa()



if __name__ == "__main__":
    asyncio.run(chat())