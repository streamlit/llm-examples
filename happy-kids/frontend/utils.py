import redis
import json
import os
from google.cloud import storage

REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Usa "redis" se a variável não estiver definida
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
# Conectar ao Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

def save_short_term_memory(user_id, message):
    """Armazena a memória de curto prazo no Redis (expira em 10 minutos)."""
    key = f"user:{user_id}:memory"
    
    # Recupera mensagens anteriores
    history = redis_client.lrange(key, 0, -1)

    # Adiciona a nova mensagem no histórico
    history.append(json.dumps({"message": message}))
    
    # Mantém apenas as últimas 5 mensagens
    if len(history) > 5:
        history.pop(0)

    # Salva no Redis com tempo de expiração de 10 minutos
    redis_client.delete(key)  # Remove a chave antiga
    redis_client.rpush(key, *history)  # Insere a lista atualizada
    redis_client.expire(key, 600)  # Expira em 10 minutos

    return True

def get_short_term_memory(user_id):
    """Recupera a memória de curto prazo do Redis."""
    key = f"user:{user_id}:memory"
    history = redis_client.lrange(key, 0, -1)

    # Decodifica os JSONs armazenados
    messages = [json.loads(msg)["message"] for msg in history]
    
    return messages
