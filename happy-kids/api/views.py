
from rest_framework import generics
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class historicalSessionsView(generics.ListAPIView):
    queryset = historicalSessions.objects.all()
    serializer_class = historicalSessionsSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class LuluTrainningView(generics.ListAPIView):
    queryset = luluTrainning.objects.all()
    serializer_class = LuluTrainningSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated] 

class chat_SessionView(generics.ListAPIView):
    queryset = chat_Session.objects.all()
    serializer_class = chat_SessionSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class chat_memoriesView(generics.ListAPIView):
    queryset = chat_memories.objects.all()
    serializer_class = chat_memoriesSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class chat_dim_onboarding_questionsView(generics.ListAPIView):
    queryset = chat_dim_onboarding_questions.objects.all()
    serializer_class = chat_dim_onboarding_questionsSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class chat_dim_onboarding_options_answersView(generics.ListAPIView):
    queryset = chat_dim_onboarding_options_answers.objects.all()
    serializer_class = chat_dim_onboarding_options_answersSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class chat_facts_onboarding_answersView(generics.ListAPIView):
    queryset =chat_facts_onboarding_answers.objects.all()
    serializer_class = chat_facts_onboarding_answersSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class dim_question_type_view(generics.ListAPIView):
    queryset = dim_question_type.objects.all()
    serializer_class = dim_question_typeSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class diary_factsView(generics.ListAPIView):
    queryset = diary_facts.objects.all()
    serializer_class = diary_factsSerializer
    filter_backends = [DjangoFilterBackend]

class dim_am_i_boring_questionsView(generics.ListAPIView):
    queryset = dim_am_i_boring_questions.objects.all()
    serializer_class = dim_am_i_boring_questionsSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class dim_am_i_boring_options_answersView(generics.ListAPIView):
    queryset = dim_am_i_boring_options_answers.objects.all()
    serializer_class = dim_am_i_boring_options_answersSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class facts_am_i_boring_answersView(generics.ListAPIView):
    queryset = facts_am_i_boring_answers.objects.all()
    serializer_class = facts_am_i_boring_answersSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class facts_memosView(generics.ListAPIView):
    queryset = facts_memos.objects.all()
    serializer_class = facts_memosSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

class chat_facts_feedbackView(generics.ListAPIView):
    queryset = chat_facts_feedback.objects.all()
    serializer_class = chat_facts_feedbackSerializer
    filter_backends = [DjangoFilterBackend]