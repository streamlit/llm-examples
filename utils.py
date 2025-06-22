import streamlit as st
import os
import boto3
from botocore.client import Config
import pika
import json
import time
import re
from dotenv import load_dotenv
from py2neo import Graph

load_dotenv()

@st.fragment()
def getFatos(autor, documento):
    NEO4J_URI = st.secrets.NEO4J_URI
    NEO4J_USER = st.secrets.NEO4J_USER
    NEO4J_PASSWORD = st.secrets.NEO4J_PASSWORD
    # Connect to the Neo4j database
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    query = f"""
        MATCH (a:AtomicFact)<-[:HAS_ATOMIC_FACT]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
        WHERE d.autor = \"{autor}\" and d.id = \"{documento}\"
        RETURN DISTINCT a.text as fato
    """
    
    results = graph.run(query)
    
    retorno = []
    
    for fatos in results:
        retorno.append(fatos["fato"])

    return retorno

@st.fragment()
def getPersonagens(autor, documento):
    NEO4J_URI = st.secrets.NEO4J_URI
    NEO4J_USER = st.secrets.NEO4J_USER
    NEO4J_PASSWORD = st.secrets.NEO4J_PASSWORD
    # Connect to the Neo4j database
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    query = f"""
        MATCH (k:Character)<-[:Character]-(a:AtomicFact)<-[:HAS_ATOMIC_FACT]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
        WHERE d.autor = \"{autor}\" and d.id = \"{documento}\"
        RETURN DISTINCT k.text as character
    """
    
    results = graph.run(query)
    
    retorno = []
    
    for character in results:
        retorno.append(character["character"])

    return retorno

def verificaDocumento(documento, autor):
    NEO4J_URI = st.secrets.NEO4J_URI
    NEO4J_USER = st.secrets.NEO4J_USER
    NEO4J_PASSWORD = st.secrets.NEO4J_PASSWORD
    # Connect to the Neo4j database
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))    
    query = f"""
            MATCH (d:Document)
            WHERE d.autor = "{autor}" AND d.id = "{documento}"
            RETURN COUNT(d) > 0 AS documentExists
    """
    result = graph.run(query)
    record = result.evaluate()    
    
    return record

# True se tiver que retornar narrativas com mais de um personagem. Por padrão, Falso.    
def listaDocumentos(autor, maisUmPersonagem = False):
    NEO4J_URI = st.secrets.NEO4J_URI
    NEO4J_USER = st.secrets.NEO4J_USER
    NEO4J_PASSWORD = st.secrets.NEO4J_PASSWORD
    # Connect to the Neo4j database
    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))    
    query = ""
    

    if (maisUmPersonagem):
        query = f"""
            MATCH (k:Character)<-[:Character]-(a:AtomicFact)<-[:HAS_ATOMIC_FACT]-(c:Chunk)<-[:HAS_CHUNK]-(d:Document)
            WHERE d.autor = \"{autor}\" and d.contexto = 'NOVA_NARRATIVA'
            WITH d.id AS conteudo, COUNT(DISTINCT k) AS characterCount
            WHERE characterCount > 1
            RETURN conteudo
        """
    else:
        query = f"""
            MATCH (d:Document)
            WHERE d.autor = \"{autor}\" and d.contexto = 'NOVA_NARRATIVA'
            RETURN DISTINCT d.id as conteudo
        """
    
    
    results = graph.run(query)
    
    retorno = []
    
    for x in results:
        retorno.append(x["conteudo"])

    return retorno   


@st.fragment()
def sanitize_string(input_string):
    # Define the regex pattern
    pattern = r'^[a-zA-Z0-9.\-_]{1,255}$'
    
    # Check if the string matches the regex
    if re.match(pattern, input_string):
        return input_string  # String is already valid
    
    # Sanitize the string: remove invalid characters
    sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '', input_string)
    
    # Truncate to 255 characters if necessary
    return sanitized[:255]

@st.fragment()
def updateFile(filename, usuario, content):
    # st.write(content)
    session = boto3.session.Session()
    client = session.client('s3',
                        endpoint_url=st.secrets.BUCKET_ENDPOINT,
                        config=Config(s3={'addressing_style': 'virtual'}), 
                        region_name=st.secrets.BUCKET_REGION_NAME, 
                        aws_access_key_id=st.secrets.BUCKET_ACCESS_ID, 
                        aws_secret_access_key=st.secrets.BUCKET_ACCESS_KEY) 


    userspace = sanitize_string(usuario)
    path = userspace + "/" + filename

    isCreated = False
    r = client.list_objects(Bucket=st.secrets.BUCKET_NAME)
    if  r.get('Contents') is not None:   
        for n in r.get('Contents'):
            if path in n['Key']:
                isCreated = True
                break
    
    # Create a new Space.
    if not isCreated:
        client.put_object(Bucket=st.secrets.BUCKET_NAME, 
                    Key=path, # Object key, referenced whenever you want to access this file later.
                    Body=content, # The object's contents.
                    ACL='private', # Defines Access-control List (ACL) permissions, such as private or public.
                    Metadata={ # Defines metadata tags.
                        'user': usuario                      
                    }
                    )
        
@st.fragment()
def solicitaCargaBaseConhecimento(document_name, AUTOR, CONTEXTO, IDIOMA, PERSONA):
    
    message = {
        "DOCUMENT_NAME": document_name,
        "AUTOR": AUTOR,
        "CONTEXTO": CONTEXTO,
        "IDIOMA": IDIOMA,
        "PERSONA": PERSONA        
    }
    # Convert the message to a JSON string
    message_json = json.dumps(message)

    credentials = pika.PlainCredentials(st.secrets.rabbitmq_user, st.secrets.rabbitmq_user_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(st.secrets.rabbitmq_server, credentials=credentials))
    channel = connection.channel()
    # Declare a queue
    channel.queue_declare(queue=st.secrets.QUEUE_KNOWLEDGE_DB)

    # Publish the JSON message to the queue
    channel.basic_publish(exchange='',
                        routing_key=st.secrets.QUEUE_KNOWLEDGE_DB,
                        body=message_json)
    connection.close()
        
        
def carrega_fatos(documento, personagem, autor) -> str:
    fatos = ""
    NEO4J_URI = st.secrets.NEO4J_URI
    NEO4J_USER = st.secrets.NEO4J_USER
    NEO4J_PASSWORD = st.secrets.NEO4J_PASSWORD

    graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))        

    # Fatos Atomicos mais relevantes para um personagem especifico
    qry_Relevant_Facts_About_Character = f"""
        MATCH (c:Character)
        WHERE c.text = \"{personagem}\"
        WITH c
        MATCH (a:AtomicFact)
        WHERE (a)-[:Character]->(c)
        WITH a
        MATCH (k:Chunk)
        WHERE (k)-[:HAS_ATOMIC_FACT]->(a)
        WITH k,a
        MATCH (d:Document)
        WHERE (d)-[:HAS_CHUNK]->(k) and d.id = \"{documento}\" and d.autor = \"{autor}\"
        RETURN a.text as texto
    """    

    results = graph.run(qry_Relevant_Facts_About_Character)
        # Process and print the results
    for record in results:    
        texto = record["texto"]        
        fatos += f"Fato: {texto}\n"
    
    return fatos


instrucoes = """
Iremos construir um filme juntos! Para isso vamos construir uma história narrativa separada em cenas e com foco em um personagem.

O Personagem foco da história é: {personagem}.  

A história deverá se basear nas seguintes propostas diretivas: {nova_historia}.

O tom da narrativa deve estar alinhado com o estilo geral da proposta, seja ele comico,  esperançoso, trágico, misterioso ou aberto.

IMPORTANTE: O RESULTADO DA HISTÓRIA DEVE SER NUM FORMATO DE CENAS OU ATOS SEPARADOS POR PARÁGRAFOS E DE FORMA A SER POSSIVEL CONSTRUIR UM VIDEO/FILME A PARTIR DA NARRATIVA. LOGO AS CENAS DEVEM SER VISUALMENTE INTERESSANTES.

IMPORTANTE: SOMENTE O TEXTO DEVE SER A SAÍDA! NÃO INCLUIR QUALQUER REFERENCIA AS DECISÕES TOMADAS, SOBRE OS PARAMETROS DE ENTRADA E QUALQUER OUTRA INFORMAÇÃO QUE NÃO SEJA ESTRITAMENTE SOBRE A HISTÓRIA!!!

NÃO INCLUIR O TITULO NA NARRATIVA FINAL.

IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_FINAL_TEXTO_INICIANTE = """

Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

O titulo da nova historia é: {titulo}

A narrativa deve ser baseada na seguinte proposta:
{nova_historia}

################################

AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}


OS FATOS QUE SUBSIDIAM A NARRATIVA SAO OS SEGUINTES:

{FACTS}

IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""



PROMPT_PERSONAGEM = """

VOCE É UM CONTADOR DE ESTÓRIAS, ESPECIALISTA EM SUGERIR IDEIAS DE COMO UM TEXTO PODE SE TRANSFORMAR EM UMA BOA ESTORIA.

PRECISO QUE ME DÊ {COUNT} IDÉIAS DE COMO AVANÇAR COM A ESCRITA DO MEU LIVRO/CONTO. 

O FOCO DA SUGESTAO DEVE SER NO PERSONAGEM: {PERSONAGEM}.


PARA CADA UMA DAS {COUNT} IDEIAS, CONSIDERE:

################################
CONSIDERE A SEGUINTE ABORDAGEM ESTRUTURAL PARA CONDUZIR A PROPOSTA DE IDEIAS/SUGESTÕES PARA EVOLUIR A NARRATIVA:

{STRUCTURE}

################################
CONSIDERE O SEGUINTE RECURSO NARRATIVO PARA CONDUZIR A PROPOSTA DE IDEIAS/SUGESTÕES DA NARRATIVA:
{RECURSO}

################################
A NARRATIVA RESUMIDA ESTÁ A SEGUIR

{NARRATIVE}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA SUA SUGESTÃO:

{FACTS}

O tom das sugestões deve estar alinhado com o estilo geral da história, seja ele esperançoso, trágico, misterioso ou aberto.


Ao final, apresente ao usuário as seguintes informações por tópicos:


IMPORTANTE: MANTER REFERENCIA A NARRATIVA E A PERSONAGEM NA PROPOSTA GERADA!!

- Titulo: Um titulo que resume a ideia proposta.
- Proposta: Ideia que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo sugerido pelo usuário. 
- Personagem: Como a ideia impacta a jornada do personagem?
- De que forma a ideia está relacionada à abordagem estrutural proposta? (Ex.: A alternância emocional é alcançada através das indecisões do personagem .....)
- De que forma o recurso narrativo foi abordado? (ex.: incluí a Alegoria ao sugerir que o amor fosse representado através da relação entre o algodão e a desfiadeira....)
- Como a proposta sugerida evita que o escritor caia no lugar comum em relação a seu conteúdo? 

IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""

PROMPT_FATO = """

VOCE É UM CONTADOR DE ESTÓRIAS, ESPECIALISTA EM SUGERIR IDEIAS DE COMO UM TEXTO PODE SE TRANSFORMAR EM UMA BOA ESTORIA.

PRECISO QUE ME DÊ {COUNT} IDÉIAS DE COMO AVANÇAR COM A ESCRITA DO MEU LIVRO/CONTO. 

O FOCO DA SUGESTAO DEVE SER NO FATO: {FATO}.

PARA CADA UMA DAS {COUNT} IDEIAS, CONSIDERE:

################################
CONSIDERE A SEGUINTE ABORDAGEM ESTRUTURAL PARA CONDUZIR A PROPOSTA DE IDEIAS/SUGESTÕES PARA EVOLUIR A NARRATIVA:

{STRUCTURE}

################################
CONSIDERE O SEGUINTE RECURSO NARRATIVO PARA CONDUZIR A PROPOSTA DE IDEIAS/SUGESTÕES DA NARRATIVA:
{RECURSO}

################################
A NARRATIVA RESUMIDA ESTÁ A SEGUIR

{NARRATIVE}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA SUA SUGESTÃO:

{FACTS}

O tom das sugestões deve estar alinhado com o estilo geral da história, seja ele esperançoso, trágico, misterioso ou aberto.


Ao final, apresente ao usuário as seguintes informações por tópicos:


IMPORTANTE: MANTER REFERENCIA A NARRATIVA E A PERSONAGEM NA PROPOSTA GERADA!!

- Titulo: Um titulo que resume a ideia proposta.
- Proposta: Ideia que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo sugerido pelo usuário. 
- Personagem: Como a ideia impacta a jornada do personagem?
- De que forma a ideia está relacionada à abordagem estrutural proposta? (Ex.: A alternância emocional é alcançada através das indecisões do personagem .....)
- De que forma o recurso narrativo foi abordado? (ex.: incluí a Alegoria ao sugerir que o amor fosse representado através da relação entre o algodão e a desfiadeira....)
- Como a proposta sugerida evita que o escritor caia no lugar comum em relação a seu conteúdo? 

IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}



"""

PROMPT_TEXTO_AVANCADO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

################################
ESTRUTURA(S) DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_TEXTO_INTERMEDIARIO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 


################################
ESTRUTURA DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_FATO_AVANCADO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no fato: {FATO}

################################
ESTRUTURAS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""

PROMPT_FATO_INTERMEDIARIO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no fato: {FATO}

################################
ESTRUTURA DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_PERSONAGEM_AVANCADO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no personagem: {PERSONAGEM}

################################
ESTRUTURAS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:
{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:
{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""

PROMPT_PERSONAGEM_INTERMEDIARIO = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no personagem: {PERSONAGEM}

################################
ESTRUTURA DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{ESTRUTURA}


################################
RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:
{RECURSO}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:
{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:
{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_PERSONAGEM_INICIANTE = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no personagem: {PERSONAGEM}

################################
ESTRUTURA E RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:


{RECURSO_INICIANTE}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_FATO_INICIANTE = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 

Todas as  Narrativas PROPOSTAS possuem foco no fato: {FATO}

################################
ESTRUTURA E RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:


{RECURSO_INICIANTE}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""


PROMPT_TEXTO_INICIANTE = """
Você é uma inteligência artificial especialista em storytelling. 

Sua missão é criar narrativas envolventes, originais e bem estruturadas com base nos elementos fornecidos. 

Use criatividade, coerência e emoção para transformar ideias em histórias que conectam, inspiram e prendem a atenção do público.

PRECISO QUE ME DÊ {COUNT} PROPOSTAS DE COMO CRIAR NARRATIVAS. 


################################
ESTRUTURA E RECURSOS DAS NARRATIVAS PROPOSTAS DA SEGUINTE FORMA:


{RECURSO_INICIANTE}

################################
AS NARRATIVAS ESTÃO SENDO CRIADAS PELO SEGUINTE MOTIVO/OBJETIVO:

{USO_HISTORIA}

################################
FATOS MAIS RELEVANTES QUE DEVEM SER CONSIDERADOS NA CONSTRUÇÃO DAS NARRATIVAS PROPOSTAS:

{FACTS}

Ao final, apresente ao usuário as seguintes informações por NARRATIVA PROPOSTA:

- Titulo: Um titulo que resume a narrativa proposta.
- Proposta: Proposta que deverá evoluir com base na NARRATIVA, na PERSONAGEM, estrutura e recurso narrativo e motivo/objetivo sugerido pelo usuário. 


IMPORTANTE: O RESULTADO DEVE SER ESCRITO NO IDIOMA: {IDIOMA}

"""

def getPromptPersonagemIniciante(COUNT, PERSONAGEM, RECURSO_INICIANTE, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_PERSONAGEM_INICIANTE.format(
        COUNT=COUNT,
        PERSONAGEM=PERSONAGEM,
        RECURSO_INICIANTE=RECURSO_INICIANTE,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )    
    
def getPromptPersonagemIntermediario(COUNT, PERSONAGEM, RECURSO, ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_PERSONAGEM_INTERMEDIARIO.format(
        COUNT=COUNT,
        PERSONAGEM=PERSONAGEM,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )     

def getPromptPersonagemAvancado(COUNT, PERSONAGEM, RECURSO, ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_PERSONAGEM_AVANCADO.format(
        COUNT=COUNT,
        PERSONAGEM=PERSONAGEM,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )    

def getPromptFatoIniciante(COUNT, FATO, RECURSO_INICIANTE, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_FATO_INICIANTE.format(
        COUNT=COUNT,
        FATO=FATO,
        RECURSO_INICIANTE=RECURSO_INICIANTE,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )  
    
def getPromptFatoIntermediario(COUNT, FATO, RECURSO, ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_FATO_INTERMEDIARIO.format(
        COUNT=COUNT,
        FATO=FATO,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )    
    
def getPromptFatoAvancado(COUNT, FATO, RECURSO, ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_FATO_AVANCADO.format(
        COUNT=COUNT,
        FATO=FATO,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )         

def getPromptTextoIniciante(COUNT, RECURSO_INICIANTE, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_TEXTO_INICIANTE.format(
        COUNT=COUNT,
        RECURSO_INICIANTE=RECURSO_INICIANTE,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )    


def getPromptTextoIntermediario(COUNT, RECURSO,ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_TEXTO_INTERMEDIARIO.format(
        COUNT=COUNT,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )  

def getPromptTextoAvancado(COUNT, RECURSO,ESTRUTURA, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_TEXTO_AVANCADO.format(
        COUNT=COUNT,
        RECURSO=RECURSO,
        ESTRUTURA=ESTRUTURA,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )  

def getPromptFinalTextoIniciante(nova_historia,titulo, USO_HISTORIA, FACTS, IDIOMA):
    return PROMPT_FINAL_TEXTO_INICIANTE.format(
        nova_historia = nova_historia,
        titulo=titulo,
        USO_HISTORIA=USO_HISTORIA,
        FACTS=FACTS,
        IDIOMA=IDIOMA
    )    


# def getPromptTipoHistoria(tipo, personagem, fato):
#     saida = ""
#     if uso == "Personagem":
#         saida = f"Crie uma narrativa envolvente a partir da história de {personagem}."
#     elif uso == "Texto":
#         saida = f"Crie uma narrativa "
#     elif uso == "Fato":
#         saida = f"Crie uma narrativa envolvente a partir do fato \"{fato}\"."
#     return saida    

def getPromptUsoHistoria(uso):
    saida = ""
    if uso == "REDE_SOCIAL":
        saida = "Crie uma narrativa envolvente e concisa, desenvolvida especificamente para o formato de vídeo curto (como Reels, TikTok ou Shorts). A história deve capturar a atenção nos primeiros segundos, desenvolver-se com ritmo ágil e terminar com uma mensagem clara ou emocionalmente marcante. Ideal para gerar conexão e engajamento em plataformas sociais."
    elif uso == "PODCAST":
        saida = "Crie uma narrativa pensada especificamente para o formato de áudio, como podcasts, audioclipes ou narrativas faladas. A história deve ser envolvente desde os primeiros segundos, com ritmo fluido, linguagem acessível e imagens mentais fortes, explorando recursos como entonação, pausa e emoção para manter o ouvinte conectado até o fim."
    elif uso == "CONTEUDO":
        saida = "Crie uma narrativa clara, envolvente e bem estruturada, desenvolvida especialmente para ser utilizada em formato de texto escrito — como em livros, panfletos, websites ou materiais institucionais. A história deve ser adaptada ao suporte escolhido, com atenção ao tom, à organização das ideias e ao impacto da mensagem, garantindo leitura fluida e conexão com o público-alvo."
    return saida


# Prompt para Recursos Iniciantes

def getPromptRecursoIniciante(recurso):
    saida = ""
    if recurso == "IMPACTO_INICIO":
        saida = "Crie uma narrativa que comece de forma impactante e envolvente, com uma cena ou acontecimento que prenda imediatamente a atenção do leitor. Pense em estruturas ideais para redes sociais, vídeos curtos ou qualquer formato que exija impacto nos primeiros segundos. A história deve despertar curiosidade, emoção ou surpresa logo nas primeiras linhas."
    elif recurso == "MINHA_VERDADE":
        saida = "Crie uma narrativa em forma de posicionamento pessoal que vá além de um simples desabafo. A mensagem deve revelar valores, opiniões ou princípios do narrador, estruturada de forma clara e intencional. Ideal para especialistas ou influenciadores que desejam se conectar com seu público com autenticidade, autoridade e propósito."
    elif recurso == "BASTIDORES_SEGREDOS":
        saida = "Construa uma narrativa revelando um aspecto inesperado, pouco discutido ou comumente mal compreendido do seu tema principal. A história deve surpreender, esclarecer ou provocar reflexão, destacando um ponto de vista original e autêntico. Ideal para conteúdos que buscam diferenciar-se por profundidade e frescor intelectual."
    elif recurso == "ORDEM_CRONOLOGICA":
        saida == "Desenvolva uma narrativa que destaque uma sequência de eventos marcantes, como a trajetória de uma marca, a evolução de uma ideia ao longo do tempo ou o passo a passo de uma jornada transformadora. A história deve apresentar progressão clara, com marcos importantes, aprendizados e momentos de virada, permitindo que o leitor acompanhe a construção de algo significativo do início ao fim."
    elif recurso == "QUEDA_SUPERACAO":
        saida == "Crie uma narrativa onde o personagem (ou narrador) enfrenta um desafio significativo, atravessa um período de crise e, através de escolhas ou descobertas, encontra uma solução que o leva a um lugar emocional, pessoal ou profissionalmente melhor. A história deve transmitir superação, aprendizado e inspiração, sendo ideal para compartilhar lições de vida autênticas e transformadoras."
    elif recurso == "APRENDI_DIFICIL":
        saida == "Elabore uma narrativa pessoal centrada em um erro que você cometeu. Descreva o contexto da situação, o impacto desse equívoco e, principalmente, a lição valiosa que ele trouxe. A história deve transmitir vulnerabilidade e autenticidade, ao mesmo tempo em que fortalece sua autoridade e conexão com o público."
    return saida

def get_instrucoes(nova_historia, personagem, idioma):
    return instrucoes.format(
        nova_historia = nova_historia,
        personagem=personagem,
        IDIOMA=idioma
    )       

def digitaPrompt(texto):
    for word in texto.split(" "):
        yield word + " "
        time.sleep(0.02)  

@staticmethod
def get_prompt_fato(count, narrativa, fato, structure, facts, recurso, idioma):
    return PROMPT_FATO.format(
        COUNT=count,
        NARRATIVE=narrativa,
        FATO=fato,
        STRUCTURE=structure,
        FACTS=facts,
        RECURSO=recurso,
        IDIOMA=idioma
    )

@staticmethod
def get_prompt_personagem(count, personagem, narrativa, structure, facts, recurso, idioma):
    return PROMPT_PERSONAGEM.format(
        COUNT=count,
        PERSONAGEM=personagem.upper(),
        NARRATIVE=narrativa.upper(),
        STRUCTURE=structure.upper(),
        FACTS=facts.upper(),
        RECURSO=recurso.upper(),
        IDIOMA=idioma.upper()
    )


como_comecar = ["Impacto logo no início", "Comece com uma Pergunta", "Opinião com Contexto", "O que Quase Ninguém Sabe"]

def getComoComecar():
    return como_comecar


COMO_COMECAR_1 = "Comece com uma revelação surpreendente, uma pergunta forte ou algo que prende atenção nos primeiros segundos. Ideal para redes sociais, vídeos curtos e conteúdos que precisam chamar atenção rápido."
COMO_COMECAR_2 = "Inicie com uma dúvida comum do seu público e responda de forma simples, direta ou criativa. Boa para criar conexão e gerar engajamento."
COMO_COMECAR_3 = "Dê sua visão sobre um tema com base na sua experiência. Vai além do desabafo: é um posicionamento pessoal com história. Funciona muito bem para influenciadores, especialistas e criadores com propósito."
COMO_COMECAR_4 = "Mostre algo que as pessoas raramente contam: um segredo, bastidor ou erro comum. Desperta curiosidade e posiciona você como alguém autêntico."

def getComoComecarTexto(como_comecar_param) -> str:
    saida = ""
    if como_comecar_param == como_comecar[0]:
        saida = COMO_COMECAR_1
    elif como_comecar_param == como_comecar[1]:
        saida = COMO_COMECAR_2        
    elif como_comecar_param == como_comecar[2]:
        saida = COMO_COMECAR_3  
    elif como_comecar_param == como_comecar[3]:
        saida = COMO_COMECAR_4     
    return saida         
         
como_organizar = ["História em Ordem Cronológica", "Emoções em Alta e Baixa", "Queda e Superação", "Tentei, Errei, Acertei", "Guia Prático", "Transformação Visível"]

def getComoOrganizar():
    return como_organizar

COMO_ORGANIZAR_1 = "Conte sua história na sequência em que tudo aconteceu: começo, meio e fim. Ótimo para mostrar uma jornada, trajetória ou processo de crescimento."
COMO_ORGANIZAR_2 = "Alterne momentos de desafio e superação, tensão e humor. Ideal para criar conexão emocional e engajar o público."
COMO_ORGANIZAR_3 = "A história começa bem, depois algo dá errado. Você enfrenta um problema, supera e aprende com isso. Excelente para histórias inspiradoras."
COMO_ORGANIZAR_4 = "Mostre que tentou uma solução que não deu certo, até encontrar o caminho ideal. Ensina com autenticidade e humaniza a narrativa."
COMO_ORGANIZAR_5 = "Explique como fazer algo com etapas claras. Ideal para tutoriais, passo a passo e mostrar seu método."
COMO_ORGANIZAR_6 = "Mostre uma mudança clara entre o “antes” e o “depois”. Pode ser uma mudança pessoal, estética, de mentalidade ou de resultados."


def getComoOrganizarTexto(como_organizar_param) -> str:
    saida = ""
    if como_organizar_param == como_organizar[0]:
        saida = COMO_ORGANIZAR_1
    elif como_organizar_param == como_organizar[1]:
        saida = COMO_ORGANIZAR_2        
    elif como_organizar_param == como_organizar[2]:
        saida = COMO_ORGANIZAR_3  
    elif como_organizar_param == como_organizar[3]:
        saida = COMO_ORGANIZAR_4     
    elif como_organizar_param == como_organizar[4]:
        saida = COMO_ORGANIZAR_5 
    elif como_organizar_param == como_organizar[5]:
        saida = COMO_ORGANIZAR_6                 
    return saida     



como_ensinar = ["Aprendi do Jeito Difícil", "O Problema Era a Solução"]

def getComoEnsinar():
    return como_ensinar

COMO_ENSINAR_1 = "Compartilhe um erro que cometeu e o que ele te ensinou. Mostra vulnerabilidade e autoridade ao mesmo tempo."
COMO_ENSINAR_2 = "Comece com algo que parecia ruim, mas acabou sendo um ponto forte. Mostra crescimento e mudança de visão."

def getComoEnsinarTexto(como_ensinar_param) -> str:
    saida = ""
    if como_ensinar_param == como_ensinar[0]:
        saida = COMO_ENSINAR_1
    elif como_ensinar_param == como_ensinar[1]:
        saida = COMO_ENSINAR_2  
    return saida    


formas_contar = ["História Rápida", "Comparação Simples", "Antes e Depois"]

def getFormasContar():
    return formas_contar

FORMAS_CONTAR_1 = "Conte uma mini-história (real ou fictícia) para ilustrar uma ideia."
FORMAS_CONTAR_2 = "Compare seu tema com algo fácil de entender. Pode usar metáforas, analogias ou dar vida a um conceito."
FORMAS_CONTAR_3 = "Mostre uma transformação ou contraste entre duas situações. Isso dá impacto à sua mensagem."

def getFormasContarTexto(formas_contar_param) -> str:
    saida = ""
    if formas_contar_param == formas_contar[0]:
        saida = FORMAS_CONTAR_1
    elif formas_contar_param == formas_contar[1]:
        saida = FORMAS_CONTAR_2  
    elif formas_contar_param == formas_contar[2]:
        saida = FORMAS_CONTAR_3          
    return saida  


engajamento_curiosidade = ["Pergunta ou Curiosidade", "Surpresa ou Reviravolta", "Gancho Final"]

def getEngajamentoCuriosidade():
    return engajamento_curiosidade

ENGAJAMENTO_CURIOSIDADE_1 = "Abra com uma pergunta ou deixe uma “pulga atrás da orelha”."
ENGAJAMENTO_CURIOSIDADE_2 = "Traga algo inesperado no meio ou fim do conteúdo. Quebre a expectativa."
ENGAJAMENTO_CURIOSIDADE_3 = "Termine com uma pergunta, provocação ou promessa de continuação. Deixe o leitor querendo mais."

def getEngajamentoCuriosidadeTexto(eng_curiosidade_param) -> str:
    saida = ""
    if eng_curiosidade_param == engajamento_curiosidade[0]:
        saida = ENGAJAMENTO_CURIOSIDADE_1
    elif eng_curiosidade_param == engajamento_curiosidade[1]:
        saida = ENGAJAMENTO_CURIOSIDADE_2  
    elif eng_curiosidade_param == engajamento_curiosidade[2]:
        saida = ENGAJAMENTO_CURIOSIDADE_3          
    return saida  
       

tom_voz = ["Tom Pessoal","Alívio Cômico"]

def getTomVoz():
    return tom_voz

TOM_VOZ_1 = "Fale como você fala na vida real. Conte do seu ponto de vista e com sua voz."
TOM_VOZ_2 = "Use humor ou ironia para deixar o conteúdo mais leve e humano."

def getTomVozTexto(tom_voz_param) -> str:
    saida = ""
    if tom_voz_param == tom_voz[0]:
        saida = TOM_VOZ_1
    elif tom_voz_param == tom_voz[1]:
        saida = TOM_VOZ_2         
    return saida  


clareza_autoridade = ["Contexto Rápido", "Prova com Dados", "Dica Prática"]

def getClarezaAutoridade():
    return clareza_autoridade
       
CLAREZA_AUTORIDADE_1 = "Explique o básico para quem está chegando agora. Onde, quando, por quê?"
CLAREZA_AUTORIDADE_2 = "Inclua um número, dado ou fato que sustente o que você está dizendo."
CLAREZA_AUTORIDADE_3 = "Entregue um passo simples, uma dica fácil ou um mini tutorial útil."

def getClarezaAutoridadeTexto(clareza_autoridade_param) -> str:
    saida = ""
    if clareza_autoridade_param == clareza_autoridade[0]:
        saida = CLAREZA_AUTORIDADE_1
    elif clareza_autoridade_param == clareza_autoridade[1]:
        saida = CLAREZA_AUTORIDADE_2
    elif clareza_autoridade_param == clareza_autoridade[2]:
        saida = CLAREZA_AUTORIDADE_3
                 
    return saida         

posicionamento_conexao = ["Discordância Construtiva","Conexão com o Leitor"]

def getPosicionamentoConexao():
    return posicionamento_conexao

POSICIONAMENTO_CONEXAO_1 = "Questione ideias comuns de forma respeitosa. Mostre sua visão."
POSICIONAMENTO_CONEXAO_2 = "Mostre como aquilo afeta quem está lendo. Convide à interação."

def getPosicionamentoConexaoTexto(posicionamento_conexao_param) -> str:
    saida = ""
    if posicionamento_conexao_param == posicionamento_conexao[0]:
        saida = POSICIONAMENTO_CONEXAO_1
    elif posicionamento_conexao_param == posicionamento_conexao[1]:
        saida = POSICIONAMENTO_CONEXAO_2                 
    return saida         


recursos_extras = ["Minha Experiência","Tradução Simples"]

def getRecursosExtras():
    return recursos_extras

RECURSOS_EXTRAS_1 = "Fale de algo que você viveu relacionado ao tema. Traz autenticidade e proximidade."
RECURSOS_EXTRAS_2 = "Explique um conceito difícil com palavras simples, como se falasse com um amigo."

def getRecursosExtrasTexto(param) -> str:
    saida = ""
    if param == recursos_extras[0]:
        saida = RECURSOS_EXTRAS_1
    elif param == recursos_extras[1]:
        saida = RECURSOS_EXTRAS_2                 
    return saida  

       
estruturas = ["LINHA DO TEMPO", "ALTERNÂNCIA EMOCIONAL","LEAD", "O HOMEM NO BURACO", "DOS TRAPOS À RIQUEZA", "SOLUÇÃO ERRADA"]

tamanho_texto = ["Muito Pequeno", "Pequeno", "Medio", "Grande"]


def getTamanhoTexto():
    return tamanho_texto

def getEstruturas():
    return estruturas


def getRecursos():
    return recursos


STRUCTURE_1 = """

LINHA DO TEMPO: A NARRATIVA IRÁ SE DESENROLAR EM TORNO DE UMA LINHA DO TEMPO. A SEQUENCIA NARRATIVA DEVE SER TEMPORAL, CONSIDERANDO QUE OS EVENTOS OCORREM EM UMA ORDEM CRONOLÓGICA. 

"""

STRUCTURE_2 = """

ALTERNÂNCIA EMOCIONAL: A NARRATIVA TORNA-SE UMA JORNADA EMOCIONAL. DESSA FORMA, AO ALTERNAR EMOÇÕES POSITIVAS E NEGATIVAS, O ENREDO AVANÇA: UMA DERROTA DÁ LUGAR A UMA VITÓRIA; UM ALÍVIO CÔMICO QUEBRA UM MOMENTO DE TENSÃO.

"""


STRUCTURE_3 = """

LEAD: A O COMEÇO TORNA-SE A PARTE MAIS IMPORTANTE DA NARRATIVA. LOGO NO COMEÇO CRIAM-SE CURIOSIDADES, INTRIGA-SE OS LEITORES OU AINDA SUGERE-SE O QUE ESTÁ POR VIR. 

"""

STRUCTURE_4 = """

O HOMEM NO BURACO: A NARRATIVA COMEÇA EM UM LUGAR POSITIVO (ZONA DE CONFORTO) PARA LOGO EM SEGUIDA UM PROBLEMA INESPERADO OCORRER (GATILHO). A CRISE SE INSTAURA, CAUSANDO MEDO, AFLIÇÃO, RAIVA OU DESESPERO. MAS LOGO É POSSÍVEL ENCONTRAR UMA SOLUÇÃO OU UM CAMINHO. POR FIM, MOSTRA-SE QUE O MOMENTO DIFÍCIL FOI PASSAGEIRO E QUE O FIM DA NARRATIVA É EM UM LUGAR MELHOR.

"""


STRUCTURE_5 = """

DOS TRAPOS À RIQUEZA: AQUI A NARRATIVA SE INICIA COM UM VALOR OCULTO, ONDE ALGO É VISTO COMO NEGATIVO (uma habilidade, uma emoção, um pensamento, um objeto, etc...), entretanto percebe-se que isso pode ser um erro. O elemento negativo é colocado à prova (ASCENÇÃO) e, para a surpresa do leitor, ele se mostra como algo extremamente valioso.

"""

STRUCTURE_6 = """

SOLUÇÃO ERRADA: A NARRATIVA COMEÇA EM UM LUGAR NEGATIVO, E UMA PRIMEIRA SOLUÇÃO PARECER SER CORRETA. ENTRETANTO, ELA SE MOSTRA FALHA (REVÉS) e a situação é agravada. APÓS ENCONTRAR A RECUPERAÇÃO, A SOLUÇÃO VERDADEIRA É ENCONTRADA. Por fim, aprendemos a tomar melhores decisões. 

"""

STRUCTURE_DEFAULT = """

NÃO É NECESSÁRIO ADOTAR UMA ESTRUTURA PREDEFINIDA. 

"""

RECURSO_DEFAULT = """

NÃO É NECESSÁRIO ADOTAR UM RECURSO

"""


recursos = ["ALEGORIA", "ALIVIO COMICO", "CONTEXTO", "COMPARAÇÃO", "CONTRASTE", "CURIOSIDADE", "DADOS VALIDADORES", "DISCORDÂNCIA",
            "GANCHO", "IDENTIFICAÇÃO", "INTERAÇÃO", "METALINGUAGEM", "MISTÉRIO", "NÚMERO MÁGICO", "PERSONIFICAÇÃO", "PLOT TWIST",
            "PONTO DE VISTA","PRENÚNCIO", "QUEBRA DE PADRÃO", "RELATO", "REVELAÇÃO", "SURPRESA", "TEMPO", "VITÓRIA RÁPIDA", "VIDA PREGRESSA",
            "ANTAGONISMO", "ANEDOTA","ALUSÃO"]

RECURSO_1 = """
ALEGORIA: Representar. Figurar. Simular. Descreva um cenário ou enredo ficcional que claramente remeta à realidade da narrativa. 
"""
RECURSO_2 = """
ALÍVIO CÔMICO: Brincar. Divertir. Fruir. Faça uma observação espirituosa, quebre a quarta parede ou conte uma piada. 
"""
RECURSO_3 = """
CONTEXTO: Situar. Explicar. Conectar. Faça uma contextualização que seja útil, explorando as perguntas: Quem? O quê? Onde? Como? Por quê?
"""
RECURSO_4 = """
COMPARAÇÃO: Comparar. Simbolizar. Imaginar. Encontre a comparação capaz de fazer a explicação avançar com velocidade, seja por metáfora, analogia, e que explore um 
elemento mais simples que já se encontra no imaginário coletivo. 
"""
RECURSO_5 = """
CONTRASTE: Contrastar. Divergir. Diferenciar. O antes e o depois, o que é e o que não é, a mentira e a verdade, isso e aquilo. Encontre elementos que se contrapõem
no intuito de reforçar um argumento. 
"""
RECURSO_6 = """
CURIOSIDADE: Questionar. Instigar. Esconder. Faça uma pergunta engenhosa ou sugeria possuir uma informação que o outro desconheça. Qual a resposta? O que virá a seguir?
"""
RECURSO_7 = """
DADOS VALIDADORES: Comprovar. Concluir. Espantar. Utilize um número que é essencial para reforçar um ponto ou que cause espanto. Preserve a credibilidade apoiando-se 
em fontes confiáveis.
"""
RECURSO_8 = """
DISCORDÂNCIA: Divergir. Contrariar. Opor. Pondere sobre a questão e exponha sua discordância, ajudando a enxergar um outro ponto de vista.
"""
RECURSO_9 = """
GANCHO: Instigar. Entusiasmar. Amarrar. Nos últimos instantes, deixe uma pergunta em aberto ou introduza uma informação inédita à narrativa, prometendo conclusões em uma próxima
criação. 
"""
RECURSO_10 = """
IDENTIFICAÇÃO: Retratar. Conectar. Traduzir. Desperte o interesse ao apontar como o assunto do enredo se conecta de uma forma ou outra com crenças, comportamentos ou com 
a jornada da narrativa.
"""

RECURSO_11 = """
INTERAÇÃO: Motivar. Convocar. Desafiar. Abra espaço para participação ou peça opinião. Especificidade e clareza em relação ao que se espera é importante para 
aumentar a percepção de valor do leitor. 
"""
RECURSO_12 = """
METALINGUAGEM: Referenciar. Analisar. Explicar. Tente ser conciso e claro, sem abrir mão da praticidade. Explore a metalinguagem para fazer sua narrativa autorreferente. 
"""
RECURSO_13 = """
MISTÉRIO: Investigar. Insinuar. Cadenciar. Caminhe no sentido de uma investigação, cadenciando as informações conforme avança. Vez ou outra insinue o que está por vir.
"""
RECURSO_14 = """
NÚMERO MÁGICO: Facilitar. Listar. Adequar. Apresente um numero que pode ser referenciado em vários contextos para que os leitores possam lembrar com facilidade o que foi comunicado.
"""

RECURSO_15 = """
PERSONIFICAÇÃO: Fantasiar. Atribuir. Adjetivar. Dê um adjetivo inventivo ao assunto. Caso julgue pertinente, pode antropomorfizar a narrativa. 
"""

RECURSO_16 = """
PLOT TWIST: Mudar. Transformar. Surpreender. Próximo ao fim, uma reviravolta modifica o enredo. Por algum tempo, conduza a narrativa em uma direção. Então, subverta a 
expectativa trocando o dispositivo temático ou apresentação de uma informação que dá outro sentido a tudo que foi dito antes.
"""
RECURSO_17 = """
PONTO DE VISTA: Distinguir. Narrar. Representar. Use a primeira pessoa (eu) para transmitir pessoalidade e intimismo, a segunda pessoa (você) para transformar o leitor 
em participante ativo do enredo, ou a terceira pessoa (ele/ela) para dar a sensação de distância e neutralidade.
"""

RECURSO_18 = """
PRENÚNCIO: Sugerir. Insinuar. Apontar. Faça uma promessa ou sugestão que indique o que acontece no final, de forma a cativar o interesse do leitor no desfecho da narrativa. 
"""

RECURSO_19 = """
QUEBRA DE PADRÃO: Diferenciar. Subverter. Modificar. Seja um estilo, um discurso, ou um ponto de vista, não hesite em desconstruí-los. 
"""

RECURSO_20 = """
RELATO: Apresentar. Descrever. Divulgar. Relate passagens selecionadas na vida de figuras ilustres ou bons conhecidos capazes de ilustrar com perfeição o ponto da narrativa.
"""

RECURSO_21 = """
REVELAÇÃO: Revelar. Declarar. Exibir. Há uma revelação que é necessária ser feita. Após construir o mistério ou a curiosidade, deixe o leitor satisfeito fechando o ciclo
que foi aberto através de uma revelação. 
"""

RECURSO_22 = """
SURPRESA: Supreender. Impressionar. Cativar. Apresente uma informação inesperada, faça uma conexão improvável ou introduza um novo elemento à narrativa. 
"""


RECURSO_23 = """
Vitória Rápida: Facilitar. Instrumentalizar. Resumir. Ofereça utilidades práticas em forma de resumo, instruções ou orientações em passos que ajude o leitor a 
superar sua provações.
"""
RECURSO_24 = """
Vida Pregressa: Contar. Descrever. Contextualizar. Utilize elementos do passado da jornada como exemplo, pontuando um aprendizado, uma queda ou uma conquista que
reforçe a narrativa.
"""

RECURSO_25 = """
ANTAGONISMO: Expor. Combater. Derrotar. Ideias, crenças, desejos, sentimentos, pessoas, ou uma mistura disso tudo podem ser escalados ao papel de antagonista no enredo
proposto.
"""

RECURSO_26 = """
ANEDOTA: Recortar. Evidenciar. Distinguir. Seja um fato curioso, um acontecimento que faz rir ou repleto de significado, utilize-o. 
"""

RECURSO_27 = """
ALUSÃO: Referenciar. Adaptar. Relacionar. Referencie os clássicos, os modismos, as tendências ou as obras de nicho para cativar o leitor.
"""

RECURSO_28 = """
TEMPO: Retornar. Relembrar. Especular. Volte ao passado remoto em busca de elementos há muito esquecidos ou ao passado recente para despertar a nostalgia.
"""


def get_structure_prompt(estrutura) -> str:
    saida = ""
    if estrutura == estruturas[0]:
        saida = STRUCTURE_1
    elif estrutura == estruturas[1]:
        saida = STRUCTURE_2
    elif estrutura == estruturas[2]:
        saida = STRUCTURE_3
    elif estrutura == estruturas[3]:
        saida = STRUCTURE_4
    elif estrutura == estruturas[4]:
        saida = STRUCTURE_5
    elif estrutura == estruturas[5]:
        saida = STRUCTURE_6
        
    return saida    


def get_recurso_narrativo(recurso) -> str:
    saida = ""
    if recurso == recursos[0]:
        saida = RECURSO_1
    elif recurso == recursos[1]:
        saida = RECURSO_2
    elif recurso == recursos[2]:
        saida = RECURSO_3
    elif recurso == recursos[3]:
        saida = RECURSO_4
    elif recurso == recursos[4]:
        saida = RECURSO_5
    elif recurso == recursos[5]:
        saida = RECURSO_6
    elif recurso == recursos[6]:
        saida = RECURSO_7                        
    elif recurso == recursos[7]:
        saida = RECURSO_8
    elif recurso == recursos[8]:
        saida = RECURSO_9
    elif recurso == recursos[9]:
        saida = RECURSO_10
    elif recurso == recursos[10]:
        saida = RECURSO_11
    elif recurso == recursos[11]:
        saida = RECURSO_12
    elif recurso == recursos[12]:
        saida = RECURSO_13
    elif recurso == recursos[13]:
        saida = RECURSO_14
    elif recurso == recursos[14]:
        saida = RECURSO_15
    elif recurso == recursos[15]:
        saida = RECURSO_16
    elif recurso == recursos[16]:
        saida = RECURSO_17
    elif recurso == recursos[17]:
        saida = RECURSO_18
    elif recurso == recursos[18]:
        saida = RECURSO_19
    elif recurso == recursos[19]:
        saida = RECURSO_20
    elif recurso == recursos[20]:
        saida = RECURSO_21
    elif recurso == recursos[21]:
        saida = RECURSO_22
    elif recurso == recursos[22]:
        saida = RECURSO_23
    elif recurso == recursos[23]:
        saida = RECURSO_24
    elif recurso == recursos[24]:
        saida = RECURSO_25
    elif recurso == recursos[25]:
        saida = RECURSO_26
    elif recurso == recursos[26]:
        saida = RECURSO_27        
    elif recurso == recursos[27]:
        saida = RECURSO_28                                                                                                                                                                    
    return saida    



def getRecursosAvancados(r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13):
    saida = []
    if r1:
        saida.append("Use uma história curta ou inventada (real ou não) para explicar algo de forma mais envolvente.")
    if r2:
        saida.append("Compare o tema com algo que todo mundo entende. Pode ser uma metáfora, um símbolo ou até dar “vida” a um conceito.")
    if r3:
        saida.append("Mostre a diferença entre duas situações. Pode ser o que mudou, melhorou ou piorou. Isso dá força à sua mensagem.")
    if r4:
        saida.append("Faça uma pergunta que desperte o interesse ou sugira que você tem uma informação escondida.")
    if r5:
        saida.append("Traga algo inesperado ou mude o rumo do conteúdo no final. Isso segura a atenção.")
    if r6:
        saida.append("Termine com algo que deixa o leitor querendo mais: uma pergunta, promessa ou continuação.")
    if r7:
        saida.append("Use sua voz. Fale como você. Pode ser contando em primeira pessoa, explicando diretamente ao leitor ou fazendo piada com a própria narrativa.")
    if r8:
        saida.append("Use humor para deixar tudo mais leve. Pode ser uma piada, uma quebra engraçada ou algo inesperado.")
    if r9:
        saida.append("Explique o básico de forma simples: o que está acontecendo? Onde? Com quem? Por quê?")
    if r10:
        saida.append("Traga um número ou dado interessante que sustente seu ponto ou surpreenda.")
    if r11:
        saida.append("Liste passos fáceis ou ofereça uma solução rápida. Ideal para conteúdos úteis e objetivos.")
    if r12:
        saida.append("Mostre um ponto de vista diferente do comum, questione ideias ou se posicione contra algo — com respeito e argumentos.")
    if r13:
        saida.append("Mostre como o conteúdo tem a ver com quem está lendo e incentive a pessoa a comentar, pensar ou agir.")
    return saida


def getEstruturasAvancadas(e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12):
    saida = []
    if e1:
        saida.append("Conte a sua história seguindo a ordem dos acontecimentos, do começo ao fim. Essa estrutura é ideal para mostrar uma sequência de eventos, como a trajetória de uma marca, a evolução de uma ideia, ou o passo a passo de uma jornada. \n")
    if e2:        
        saida.append("Aqui, sua narrativa vai alternar entre altos e baixos emocionais. Um momento difícil dá espaço a uma conquista, ou uma tensão é quebrada com humor. Ideal para engajar o público e criar conexão emocional. \n")
    if e3:
        saida.append("Você começa com tudo: uma revelação surpreendente, uma pergunta intrigante ou algo que prende a atenção de cara. Essa estrutura é perfeita para redes sociais, vídeos curtos ou textos que precisam fisgar o leitor em segundos. \n")
    if e4:
        saida.append("A história começa bem, mas algo dá errado. O personagem (ou você) enfrenta um desafio, passa por uma crise, mas encontra uma saída e termina em um lugar melhor. Boa para histórias inspiradoras e lições de vida. \n")
    if e5:        
        saida.append("Tudo começa com algo que parece ruim, inútil ou sem valor. Mas ao longo da história, esse \"problema\" se revela uma grande força. Excelente para transformar percepções e mostrar crescimento. \n")
    if e6:        
        saida.append("Você começa com um problema e tenta uma solução que parece funcionar... mas não funciona. Depois de um revés, encontra o caminho certo. Ideal para mostrar aprendizado, evolução e autenticidade. \n")
    if e7:        
        saida.append("Mostre como fazer algo, do início ao fim, em etapas claras. Ideal para tutoriais, dicas profissionais, ou mostrar seu processo criativo. \n")
    if e8:        
        saida.append("Mostre uma mudança: de uma situação inicial para um resultado final impressionante. Pode ser uma mudança pessoal, profissional, estética ou de mentalidade. Muito usado por coaches, terapeutas, criadores de estilo ou fitness. \n")
    if e9:        
        saida.append("Inicie com uma dúvida comum do seu público e responda de forma clara, objetiva ou criativa. Boa para criar conexão direta e gerar engajamento rápido. \n")
    if e10:        
        saida.append("Compartilhe sua visão sobre um tema com base na sua vivência ou experiência. Não é só um desabafo: é um posicionamento com história. Funciona muito bem para influenciadores e especialistas. \n")                            
    if e11:
        saida.append("Conte sobre um erro que cometeu e como ele te ensinou algo valioso. Isso aproxima você do público e passa autoridade de forma autêntica. \n")
    if e12:        
        saida.append("Revele algo inesperado, pouco falado ou mal compreendido sobre seu tema. Essa estrutura desperta curiosidade e posiciona você como alguém que traz conteúdo original. \n")
        
    return saida    
        