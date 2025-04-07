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

class diary_factsView(generics.ListAPIView):
    queryset = diary_facts.objects.all()
    serializer_class = diary_factsSerializer

class dim_am_i_boring_questionsView(generics.ListAPIView):
    queryset = dim_am_i_boring_questions.objects.all()
    serializer_class = dim_am_i_boring_questionsSerializer

class dim_am_i_boring_options_answersView(generics.ListAPIView):
    queryset = dim_am_i_boring_options_answers.objects.all()
    serializer_class = dim_am_i_boring_options_answersSerializer

class facts_am_i_boring_answersView(generics.ListAPIView):
    queryset = facts_am_i_boring_answers.objects.all()
    serializer_class = facts_am_i_boring_answersSerializer

class facts_memosView(generics.ListAPIView):
    queryset = facts_memos.objects.all()
    serializer_class = facts_memosSerializer

class chat_facts_feedbackView(generics.ListAPIView):
    queryset = chat_facts_feedback.objects.all()
    serializer_class = chat_facts_feedbackSerializer