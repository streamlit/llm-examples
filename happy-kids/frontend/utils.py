import json
import os
from google.cloud import storage
from django.utils import timezone
from datetime import timedelta
from api import models
import openai

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
