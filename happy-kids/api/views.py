
from rest_framework import generics
from .serializers import *
from .models import *
from .utils import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import utils

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

# API POST Method to classigy the main emotional sentiment
class TextInputSerializer(serializers.Serializer):
    text = serializers.CharField(help_text="Message text to be classified")

class SentimentOutputSerializer(serializers.Serializer):
    sentiment = serializers.CharField(help_text="Predicted sentiment label")

class SentimentClassificationView(APIView):
    """
    Classify the main emotional sentiment of a youth conversation message.
    """
    @swagger_auto_schema(
        request_body=TextInputSerializer,
        responses={200: SentimentOutputSerializer},
        tags=['Classification Model', '5 Pillars']
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        sentiment = classify_sentiment_model(text)
        return Response({"sentiment": sentiment}, status=status.HTTP_200_OK)

class intensityLevelSentimentClassificationView(APIView):
    """
    Classify the sentiment intensity of a conversation.
    """
    @swagger_auto_schema(
        request_body=TextInputSerializer,
        responses={200: SentimentOutputSerializer},
        tags=['Classification Model','5 Pillars']
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        sentiment = intensity_level_sentiment_model(text)
        return Response({"Intensity Level Sentiment": sentiment}, status=status.HTTP_200_OK)

class lifePillarsClassificationView(APIView):
    """
    Given a youth conversation message, classify it according to the Life Pillars model
    """
    @swagger_auto_schema(
        request_body=TextInputSerializer,
        responses={200: SentimentOutputSerializer},
        tags=['Classification Model','5 Pillars']
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        sentiment = life_pillars_model(text)
        return Response({"Life Pillar Option": sentiment}, status=status.HTTP_200_OK)
    
class primaryTopicClassificationView(APIView):
    """
    classify it into exactly one of the following primary topics model
    """
    @swagger_auto_schema(
        request_body=TextInputSerializer,
        responses={200: SentimentOutputSerializer},
        tags=['Classification Model','5 Pillars']
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        primary_topic = primary_topics_model(text)
        return Response({"Primary Topic": primary_topic}, status=status.HTTP_200_OK)


class primaryTopicClassificationView(APIView):
    """
    classify it into exactly one of the following primary topics model
    """
    @swagger_auto_schema(
        request_body=TextInputSerializer,
        responses={200: SentimentOutputSerializer},
        tags=['Classification Model','5 Pillars']
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "Missing text"}, status=status.HTTP_400_BAD_REQUEST)
        primary_topic = primary_topics_model(text)
        return Response({"Primary Topic": primary_topic}, status=status.HTTP_200_OK)
    
class GenerateSuggestionsView(APIView):
    """
    Generate quick, context-aware question suggestions for the Lulu chatbot, based on recent chat history.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate a short question suggestions to continue the conversation based on recent chat context.",
        responses={200: openapi.Response(
            description="List of suggestion strings",
            examples={
                "application/json": {
                    "suggestions": [
                        "What should I do next?",
                        "How can I explain this to my parents?",
                        "Can you help me understand this better?"
                    ]
                }
            }
        )},
        tags=["Lulu Chat"]
    )
    def get(self, request):
        user_id = request.user.id
        suggestions = utils.generate_suggestions_from_memory(user_id)
        return Response({"suggestions": suggestions})