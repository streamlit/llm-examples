from django.urls import path
from .views import *
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Lulu API",
      default_version='v1',
      description="Interactive documentation of all Lulu API endpoints",
      contact=openapi.Contact(email="lucas@happy-kids.lu"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('historical-sessions', historicalSessionsView.as_view()),
    path('lulu-trainning', LuluTrainningView.as_view()),
    path('chat_Session', chat_SessionView.as_view()),
    path('chat_memories', chat_memoriesView.as_view()),
    path('chat_dim_onboarding_questions', chat_dim_onboarding_questionsView.as_view()),
    path('chat_dim_onboarding_options_answers', chat_dim_onboarding_options_answersView.as_view()),
    path('chat_facts_onboarding_answers', chat_facts_onboarding_answersView.as_view()),
    path('dim_question_type', dim_question_type_view.as_view()),
    path('diary_facts', diary_factsView.as_view()),
    path('dim_am_i_boring_questions', dim_am_i_boring_questionsView.as_view()),
    path('dim_am_i_boring_options_answers', dim_am_i_boring_options_answersView.as_view()),
    path('facts_am_i_boring_answers', facts_am_i_boring_answersView.as_view()),
    path('fact-memos', facts_memosView.as_view()),
    path('chat-facts-feedback', chat_facts_feedbackView.as_view()),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
