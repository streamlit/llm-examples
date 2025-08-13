from typing import Optional

import streamlit as st
from streamlit_feedback import streamlit_feedback

from trubrics import Trubrics
from trubrics.platform.feedback import Feedback, Response


class FeedbackCollector(Trubrics):
    def __init__(
        self,
        project: Optional[str],
        email: Optional[str],
        password: Optional[str],
        firebase_api_key: Optional[str] = None,
        firebase_project_id: Optional[str] = None,
    ):
        """
        Args:
            project: a Trubrics project name
            email: a Trubrics account email
            password: a Trubrics account password
        """

        if email and password and project:
            super().__init__(
                email=email,
                password=password,
                project=project,
                firebase_api_key=firebase_api_key,
                firebase_project_id=firebase_project_id,
            )

    def st_feedback(
        self,
        component: str,
        feedback_type: str,
        model: str,
        textbox_type: str = "text-input",
        prompt_id: Optional[str] = None,
        tags: list = [],
        metadata: dict = {},
        user_id: Optional[str] = None,
        key: Optional[str] = None,
        open_feedback_label: Optional[str] = None,
        save_to_trubrics: bool = True,
        align: str = "flex-end",
        disable_with_score: Optional[str] = None,
        success_fail_message: bool = True,
    ) -> Optional[dict]:
        """
        Collect ML model user feedback with UI components from a Streamlit app.

        Args:
            component: component name. Create a new component directly in Trubrics.
            feedback_type: type of feedback to be collected

                - textbox: open textbox feedback
                - thumbs: 👍 / 👎 UI buttons
                - faces: 😞 / 🙁 / 😐 / 🙂 / 😀 UI buttons
            textbox_type: if textbox selected as feedback_type, the type of textbox to use ["text-input", "text-area"]
            model: the model used - can be a model version, a link to the saved model artifact in cloud storage, etc
            prompt_id: id of the prompt object
            tags: a list of tags for the feedback
            metadata: any data to save with the feedback
            user_id: an optional reference to a user, for example a username if there is a login, a cookie ID, etc
            key: a key for the streamlit components (necessary if calling this method multiple times)
            open_feedback_label: label of optional text_input for "faces" or "thumbs" feedback_type
            save_to_trubrics: whether to save the feedback to Trubrics, or just to return the feedback object
            disable_with_score: an optional score to disable the component. Must be a "thumbs" emoji or a "faces" emoji.
                Can be used to pass state from one component to another.
            align: where to align the feedback component ["flex-end", "center", "flex-start"]
            success_fail_message: whether to display an st.toast message on feedback submission.
        """
        if key is None:
            key = feedback_type
        if feedback_type == "textbox":
            text = self.st_textbox_ui(type=textbox_type, key=key, label=open_feedback_label)
            if text:
                user_response = {"type": feedback_type, "score": None, "text": text}
                if save_to_trubrics:
                    feedback = self.log_feedback(
                        component=component,
                        user_response=user_response,
                        model=model,
                        prompt_id=prompt_id,
                        metadata=metadata,
                        tags=tags,
                        user_id=user_id,
                    )
                    if feedback is None:
                        error_msg = "Error in pushing feedback issue to Trubrics."
                        if success_fail_message:
                            st.error(error_msg)
                    else:
                        if success_fail_message:
                            st.success("Feedback saved to Trubrics.")
                        return self._pydantic_to_dict(feedback)
                else:
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
                    return self._pydantic_to_dict(feedback)
        elif feedback_type in ("thumbs", "faces"):

            def _log_feedback_trubrics(user_response, **kwargs):
                feedback = self.log_feedback(user_response=user_response, **kwargs)
                if success_fail_message:
                    if feedback:
                        st.toast("Feedback saved to [Trubrics](https://trubrics.streamlit.app/).", icon="✅")
                        return self._pydantic_to_dict(feedback)
                    else:
                        st.toast("Error in saving feedback to [Trubrics](https://trubrics.streamlit.app/).", icon="❌")

            user_response = streamlit_feedback(
                feedback_type=feedback_type,
                optional_text_label=open_feedback_label,
                disable_with_score=disable_with_score,
                on_submit=_log_feedback_trubrics if save_to_trubrics else None,
                kwargs={
                    "component": component,
                    "model": model,
                    "prompt_id": prompt_id,
                    "metadata": metadata,
                    "tags": tags,
                    "user_id": user_id,
                },
                align=align,
                key=key,
            )
            if save_to_trubrics is False and user_response:
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
                return self._pydantic_to_dict(feedback)
            return user_response
        else:
            raise ValueError("feedback_type must be one of ['textbox', 'faces', 'thumbs'].")
        return None

    @staticmethod
    def _pydantic_to_dict(feedback: Feedback) -> dict:
        """Support for pydantic v1 and v2."""
        try:
            return feedback.model_dump()
        except AttributeError:
            return feedback.dict()

    @staticmethod
    def st_textbox_ui(
        type: str = "text-input", key: Optional[str] = None, label: Optional[str] = None
    ) -> Optional[str]:
        """
        Trubrics 'textbox' UI component.

        Args:
            type: type of textbox to use (should be one of ['text-area', 'text-input'])
            key: a key for the streamlit components (necessary if calling this method multiple times with the same type)
            label: the textbox's streamlit label
        """
        if key is None:
            key = "textbox"

        if f"{key}_save_button" not in st.session_state:
            st.session_state[f"{key}_save_button"] = False

        if f"previous_{key}_state" not in st.session_state:
            st.session_state[f"previous_{key}_state"] = ""

        def clear_session_state():
            st.session_state[f"previous_{key}_state"] = st.session_state[f"{key}_title"]
            st.session_state[f"{key}_title"] = ""

        if type not in ("text-input", "text-area"):
            raise ValueError("textbox_type must be one of ['text-area', 'text-input'].")
        else:
            if type == "text-input":
                title = st.text_input(
                    label=label or "Provide some feedback",
                    key=f"{key}_title",
                )
            elif type == "text-area":
                title = st.text_area(label=label or "Provide some feedback", key=f"{key}_title")

        if title:
            st.button("Save feedback", on_click=clear_session_state, key=f"{key}_save_button")
        if st.session_state[f"{key}_save_button"]:
            return st.session_state[f"previous_{key}_state"]
        else:
            return None
