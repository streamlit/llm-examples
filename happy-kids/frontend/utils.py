import json
import os
from google.cloud import storage
from django.utils import timezone
from datetime import timedelta
from api import models
import openai
import numpy as np

def get_short_term_memory(user_id):
    """Recupera a memória de curto prazo do banco de dados"""
    time_threshold = timezone.now() - timedelta(minutes=30)
    
    conversations = (
        models.chat_memories.objects
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

    history = models.chat_memories.objects.filter(user_id=user_id).exclude(embedding=None)
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

def transcribe_with_whisper(audio_path, language_code="lb"):  # "lb" para luxemburguês
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text

