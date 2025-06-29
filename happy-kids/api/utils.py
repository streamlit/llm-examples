import json
import os
from google.cloud import storage
from django.utils import timezone
from datetime import timedelta
from .models import *
import openai
import numpy as np

def get_short_term_memory(user_id):
    """Recupera a memória de curto prazo do banco de dados"""
    time_threshold = timezone.now() - timedelta(minutes=30)
    
    conversations = (
        chat_memories.objects
        .filter(user_id=user_id, date_time__gte=time_threshold)
        .order_by('date_time') 
    )
    
    memory = []
    for conv in conversations:
        
        if conv.user_message:
            memory.append({"role": "user", "content": conv.user_message})
        
        if conv.chat_message:
            memory.append({"role": "assistant", "content": conv.chat_message})

    return memory

## Sentiment Analysis

def classify_sentiment(text):
    system_prompt = (
        "You are an expert assistant in human emotion and sentiment analysis.\n"
        "Your task is to read any provided text and classify the predominant emotion expressed, choosing only one category from the following list.\n"
        "Consider the context, nuance, and tone. If the text does not clearly express any of these emotions, respond with \"Neutral\".\n\n"
        "Possible sentiment categories:\n"
        "- Anger\n"
        "- Fear\n"
        "- Sadness\n"
        "- Joy\n"
        "- Disgust\n"
        "- Surprise\n"
        "- Neutral\n\n"
        "Respond only with the category, no explanation."
    )
    user_prompt = f'Text: "{text}"\nCategory:'
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return None


### RAG

def get_embedding(text):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_relevant_memories(user_id, question, top_k=3):
    question_emb = get_embedding(question)

    history = chat_memories.objects.filter(user_id=user_id).exclude(embedding=None)
    scored = []
    for h in history:
        sim = cosine_similarity(question_emb, h.embedding)
        scored.append((sim, h))
    scored.sort(reverse=True, key=lambda x: x[0])
    top_memories = [x[1] for x in scored[:top_k]]
    return top_memories

### Speech-to-text

from google.cloud import speech_v1p1beta1 as speech
from pydub.utils import mediainfo
import mimetypes

def recognize_speech(audio_path):
    # Detecta o mime/type pelo nome
    mime_type, _ = mimetypes.guess_type(audio_path)
    info = mediainfo(audio_path)

    # Detecta sample_rate
    sample_rate = int(info['sample_rate'])

    # Detecta encoding (Google espera estes valores específicos)
    # .wav => LINEAR16
    # .webm ou .ogg com codec OPUS => WEBM_OPUS ou OGG_OPUS
    # .flac => FLAC
    if mime_type:
        if 'wav' in mime_type:
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif 'webm' in mime_type:
            encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
        elif 'ogg' in mime_type:
            encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
        elif 'flac' in mime_type:
            encoding = speech.RecognitionConfig.AudioEncoding.FLAC
        else:
            # fallback genérico (funciona para MP3, mas a precisão pode ser menor)
            encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    else:
        # Se não conseguir identificar, tente pelo codec do mediainfo
        codec = info.get('codec_name', '')
        if codec == 'pcm_s16le':
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif codec == 'opus':
            encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
        elif codec == 'flac':
            encoding = speech.RecognitionConfig.AudioEncoding.FLAC
        else:
            encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED

    client = speech.SpeechClient()
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=sample_rate,
        language_code="en-US",
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)
    text = ""
    for result in response.results:
        text += result.alternatives[0].transcript
    return text

from django.conf import settings

def transcribe_with_whisper(audio_path, language_code="lb"): 
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text

##### tags #####

### Model 1: Primary Topics ###
def primary_topics_model(text):
    system_prompt = (
        """"
        You are an expert assistant in youth mental health and social-emotional support.
        Your task is to read the message below and classify it into exactly one of the following primary topics.
        Carefully analyze the context, emotional tone, and any subtle references.
        Your response must only be the name of the selected primary topic—no explanations, no additional text.
        Primary Topics — Definitions and Examples:
        
        Emotions and Self-awareness
        Messages about naming or describing feelings, understanding oneself, emotional regulation, self-esteem, personal identity, or self-acceptance.
        Examples:
        - “I feel sad and don’t know why.”
        - “I’m learning to control my anger.”
        - “Who am I, really?”
        
        Relationships and Belonging
        Messages about family, friendships, romantic interests, trust, feeling included or excluded, social isolation, peer pressure, bullying, or social comparison.
        Examples:
        - “Sometimes I feel invisible to my friends.”
        - “My parents are always fighting.”
        - “I wish I had someone to talk to at school.”
        
        School and Academic Life
        Messages about school, academic performance, motivation, teacher relationships, grades, homework, studying, exams, or future academic/career aspirations.
        Examples:
        - “I’m stressed about my exams.”
        - “I don’t understand this math problem.”
        - “I want to be a scientist someday.”
        
        Body and Health
        Messages about the body, body image, physical health, illness, puberty, physical changes, sleep, nutrition, exercise, or substance use concerns.
        Examples:
        - “I don’t like the way I look.”
        - “I feel tired all the time.”
        - “I’m worried about my weight.”
        
        Mental Health Signals
        Messages expressing signs of psychological distress, emotional suffering, anxiety, sadness, hopelessness, or warning signs for mental health (but not just general sadness or frustration—look for indicators of deeper mental health needs or risks).
        Examples:
        - “I feel like I can’t go on.”
        - “Nothing makes me happy anymore.”
        - “I just want everything to stop.”
        
        Personal Growth and Values
        Messages about goals, dreams, perseverance, sense of purpose, personal values, gratitude, kindness, empathy, or learning from challenges.
        Examples:
        - “I want to make a difference in the world.”
        - “Being kind to others makes me happy.”
        - “I’ve learned a lot from my mistakes.”
        
        Life Challenges and Adversities
        Messages about facing difficult situations, adversity, grief, trauma, loss, major life changes, family disruption, economic hardship, or injustice.
        Examples:
        - “My parents are getting divorced.”
        - “I’m still not over losing my grandma.”
        - “We’re having trouble paying the bills.”
        
        Fun, Hobbies and Creativity
        Messages about hobbies, sports, music, arts, gaming, favorite stories, humor, playfulness, daydreaming, or creativity.
        Examples:
        - “I love playing soccer with my friends.”
        - “Drawing helps me relax.”
        - “I can’t stop thinking about my favorite book.”
        
        Digital Life
        Messages about online experiences, social media, digital communities, online friendships, gaming, internet addiction, cyberbullying, or digital self-expression.
        Examples:
        - “People are mean to me online.”
        - “I spend too much time on my phone.”
        - “I made a new friend in an online game.”
        
        Existential and Big Questions
        Messages about meaning, purpose of life, spirituality, philosophy, ethics, or deep reflection about existence.
        Examples:
        - “What’s the meaning of life?”
        - “Sometimes I wonder if anything really matters.”
        - “Is there something after we die?”
        
        Instructions:
        - Assign only one primary topic to the message.
        - Base your choice on the main theme of the message, even if other topics are mentioned.
        - Reply with the exact topic name from the list above (case sensitive, no extra words).
        - Do not provide any explanations, context, or additional text.

        """
    )
    user_prompt = f'Text: "{text}"\nCategory:'
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Error during tag model : {e}")
        return None


def life_pillars_model(text):
    system_prompt = (
        """"
        You are an expert assistant in youth mental health and social-emotional support.
       
         Given a youth conversation message, classify it according to the Life Pillars model below:

        1. **Choose ONE Life Pillar** that best fits the core need or theme of the message:
        - Optimism (Vision): hope, positive future, imagination, awe, curiosity about possibilities
        - Gratitude (Empathy): empathy, appreciation, warmth, kindness, reciprocity
        - Belonging (Connection): feeling seen, accepted, included, cared for, close to others
        - Meaning (Transcendence): deeper purpose, spirituality, meaning beyond oneself, awe
        - Purpose (Achievements): agency, growth, achievement, perseverance, personal progress

        Guidelines:
        - Focus on the main need or emotion in the message, not surface content.
        - Sentiment helps define state: positive = Flourishing/Growing, mixed = Ambivalent, negative (medium) = Yearning, negative (high) = Struggling.
        - Return only one of the 5 options

        """
    )
    user_prompt = f'Text: "{text}"\nCategory:'
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Error during tag model : {e}")
        return None


def classify_sentiment_model(text):
    """
    Classifies the sentiment of a conversation using OpenAI GPT API.
    """
    system_prompt = (   
    """
    You are an expert assistant in youth mental health and social-emotional support.

    Given the following youth conversation message, classify the **main emotional tone** (sentiment) using one of these four options:
    - Positive
    - Negative
    - Mixed (if the message contains both positive and negative feelings)
    - Neutral (if the message expresses little or no clear emotion)

    Return only one option of "sentiment": the sentiment label
    
    """
    )
    user_prompt = f'Text: "{text}"\nCategory:'

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Error during tag model : {e}")
        return None

def intensity_level_sentiment_model(text, api_key):
    """
    Classifies the sentiment of a conversation using OpenAI GPT API.
    """
    system_prompt = (   
    """
    You are an expert assistant in youth mental health and social-emotional support.

    Given the following youth conversation message, classify the **Intensity Level** (how strong is the feeling or emotion expressed?) using one of these four options:
    - Low: mild or barely present emotion
    - Medium: noticeable, clear but not overwhelming emotion
    - High: strong, dominant emotion, hard to ignore
    - Very High: extreme, overwhelming, or urgent emotion

    Return only one option of "Intensity Level": the Intensity Level label
        
    """
    )
    user_prompt = f'Text: "{text}"\nCategory:'

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        category = response.choices[0].message.content.strip()
        return category
    except Exception as e:
        print(f"Error during tag model : {e}")
        return None