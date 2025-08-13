from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    type: str
    score: Optional[str] = None
    text: Optional[str] = None


class Feedback(BaseModel):
    """
    The Feedback object represents all data contained as a feedback response from a user.

    Attributes:
        component: the name of the component that the feedback response is saved to
        model: the model name / version
        user_response: the user response, with a type, score and text
        created_on: datetime of response (in UTC)
        prompt_id: id of the prompt object
        user_id: an optional user id
        tags: optional tags
        metadata: optional metadata, such as model prompts & predictions
    """

    component: str
    model: str
    user_response: Response
    created_on: datetime = Field(default_factory=datetime.utcnow)
    prompt_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: list = []
    metadata: dict = {}
