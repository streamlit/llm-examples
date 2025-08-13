from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    model: str
    prompt_template: str = "{prompt}"
    temperature: Optional[float] = None


class Prompt(BaseModel):
    """
    The Prompt object represents all data contained as a prompt / model request from a user.

    Attributes:
        id: prompt id
        config_model: model configuration. See ModelConfig data model.
        prompt: a user prompt
        generation: a model generation
        created_on: the UTC created time of the prompt log
        user_id: a user id
        session_id: a session id, for example for chat generations
        tags: prompt tags
        metadata: prompt metadata
    """

    id: Optional[str] = None
    config_model: ModelConfig
    prompt: str
    generation: str
    created_on: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list = []
    metadata: dict = {}
