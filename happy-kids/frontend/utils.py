import json
import os
from google.cloud import storage
from django.utils import timezone
from datetime import timedelta
from api import models

def get_short_term_memory(user_id):
    """Recupera a memória de curto prazo do banco de dados."""
    time_threshold = timezone.now() - timedelta(minutes=30)
    
    conversations = (
        models.chat_memories.objects
        .filter(user_id=user_id, date_time__gte=time_threshold)
        .order_by('-date_time')[:20]
    )
    
    messages = [
        f"User: {conv.user_message}\nChat: {conv.chat_message}"
        for conv in conversations
    ]
    
    return messages


