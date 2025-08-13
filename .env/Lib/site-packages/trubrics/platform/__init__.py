from typing import Optional

from loguru import logger

from trubrics.platform.auth import expire_after_n_seconds, get_trubrics_auth_token
from trubrics.platform.config import TrubricsConfig, TrubricsDefaults
from trubrics.platform.feedback import Feedback, Response
from trubrics.platform.firestore import (
    get_trubrics_firestore_api_url,
    list_components_in_organisation,
    list_projects_in_organisation,
    save_document_to_collection,
)
from trubrics.platform.prompts import ModelConfig, Prompt


class Trubrics:
    def __init__(
        self,
        email: str,
        password: str,
        project: str,
        firebase_api_key: Optional[str] = None,
        firebase_project_id: Optional[str] = None,
    ):
        if firebase_api_key or firebase_project_id:
            if firebase_api_key and firebase_project_id:
                defaults = TrubricsDefaults(firebase_api_key=firebase_api_key, firebase_project_id=firebase_project_id)
            else:
                raise ValueError("Both API key and firebase_project_id are required to change project.")
        else:
            defaults = TrubricsDefaults()

        auth = get_trubrics_auth_token(defaults.firebase_api_key, email, password, rerun=expire_after_n_seconds())
        if "error" in auth:
            raise Exception(f"Error while authenticating '{email}' with Trubrics: {auth['error']}")
        else:
            firestore_api_url = get_trubrics_firestore_api_url(auth, defaults.firebase_project_id)

        projects = list_projects_in_organisation(firestore_api_url, auth)
        if project not in projects:
            raise KeyError(f"Project '{project}' not found. Please select one of {projects}.")

        self.config = TrubricsConfig(
            email=email,
            password=password,  # type: ignore
            project=project,
            username=auth["displayName"],
            firebase_api_key=defaults.firebase_api_key,
            firestore_api_url=firestore_api_url,
        )

    def log_prompt(
        self,
        config_model: dict,
        prompt: str,
        generation: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: list = [],
        metadata: dict = {},
    ) -> Optional[Prompt]:
        """
        Log user prompts to Trubrics.

        Parameters:
            config_model: model configuration with fields "model", "prompt_template", "temperature"
            prompt: user prompt to the model
            generation: model generation
            user_id: user id
            session_id: session id, for example for a chatbot conversation
            tags: feedback tags
            metadata: any feedback metadata
        """
        config_model = ModelConfig(**config_model)
        prompt = Prompt(
            config_model=config_model,
            prompt=prompt,
            generation=generation,
            user_id=user_id,
            session_id=session_id,
            tags=tags,
            metadata=metadata,
        )
        auth = get_trubrics_auth_token(
            self.config.firebase_api_key,
            self.config.email,
            self.config.password.get_secret_value(),
            rerun=expire_after_n_seconds(),
        )
        res = save_document_to_collection(
            auth,
            firestore_api_url=self.config.firestore_api_url,
            project=self.config.project,
            collection="prompts",
            document=prompt,
        )
        if "error" in res:
            logger.error(res["error"])
            return None
        else:
            logger.info("User prompt saved to Trubrics.")
            prompt.id = res["name"].split("/")[-1]
            return prompt

    def log_feedback(
        self,
        component: str,
        model: str,
        user_response: dict,
        prompt_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: list = [],
        metadata: dict = {},
    ) -> Optional[Feedback]:
        """
        Log user feedback to Trubrics.

        Parameters:
            component: feedback component name created in Trubrics
            model: model name
            user_response: a user response dict that must contain these fields {"type": "", "score": "", "text": None}
            prompt_id: an optional prompt_id for tracing feedback on a specific prompt / model generation
            user_id: a user_id
            tags: feedback tags
            metadata: any feedback metadata
        """
        user_response = Response(**user_response)
        feedback = Feedback(
            component=component,
            model=model,
            user_response=user_response,
            prompt_id=prompt_id,
            user_id=user_id,
            tags=tags,
            metadata=metadata,
        )
        auth = get_trubrics_auth_token(
            self.config.firebase_api_key,
            self.config.email,
            self.config.password.get_secret_value(),
            rerun=expire_after_n_seconds(),
        )
        components = list_components_in_organisation(
            firestore_api_url=self.config.firestore_api_url, auth=auth, project=self.config.project
        )
        if feedback.component not in components:
            raise ValueError(f"Component '{feedback.component}' not found. Please select one of: {components}.")
        res = save_document_to_collection(
            auth,
            firestore_api_url=self.config.firestore_api_url,
            project=self.config.project,
            collection=f"feedback/{feedback.component}/responses",
            document=feedback,
        )
        if "error" in res:
            logger.error(res["error"])
            return None
        else:
            logger.info("User feedback saved to Trubrics.")
            return feedback
