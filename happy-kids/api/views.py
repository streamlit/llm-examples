from rest_framework import generics
from .serializers import *
from .models import *

class historicalSessionsView(generics.ListAPIView):
    queryset = historicalSessions.objects.all()
    serializer_class = historicalSessionsSerializer


class LuluTrainningView(generics.ListAPIView):
    queryset = luluTrainning.objects.all()
    serializer_class = LuluTrainningSerializer

class UsersMilestonesView(generics.ListAPIView):
    queryset = UsersMilestones.objects.all()
    serializer_class = UsersMilestonesSerializer

class chat_dim_onboarding_questionsView(generics.ListAPIView):
    queryset = chat_dim_onboarding_questions.objects.all()
    serializer_class = chat_dim_onboarding_questionsSerializer

class chat_dim_onboarding_options_answersView(generics.ListAPIView):
    queryset = chat_dim_onboarding_options_answers.objects.all()
    serializer_class = chat_dim_onboarding_options_answersSerializer

class chat_facts_onboarding_answersView(generics.ListAPIView):
    queryset =chat_facts_onboarding_answers.objects.all()
    serializer_class = chat_facts_onboarding_answersSerializer

class dim_question_type_view(generics.ListAPIView):
    queryset = dim_question_type.objects.all()
    serializer_class = dim_question_typeSerializer
