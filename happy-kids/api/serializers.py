from rest_framework import serializers
from .models import *

class historicalSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = historicalSessions
        fields = ('id','sessionDate','username')

class LuluTrainningSerializer(serializers.ModelSerializer):
    class Meta:
        model = luluTrainning
        fields = ('id','version_title','attachments','comments','creation_date')

class UsersMilestonesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersMilestones
        fields = ('id','user','milestone','completed','created_at')

class chat_dim_onboarding_questionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = chat_dim_onboarding_questions
        fields = ('question','order','active','question_type')

class chat_dim_onboarding_options_answersSerializer(serializers.ModelSerializer):
    class Meta:
        model = chat_dim_onboarding_options_answers
        fields = ('question','option')

class chat_facts_onboarding_answersSerializer(serializers.ModelSerializer):
    class Meta:
        model = chat_facts_onboarding_answers
        fields = ('user','question', 'answer','order','datetime')

class dim_question_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = dim_question_type
        field = ('question_type')

class diary_factsSerializer(serializers.ModelSerializer):
    class Meta:
        model = diary_facts
        fields = ('date','title', 'body','user')



class dim_am_i_boring_questionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = dim_am_i_boring_questions
        fields = ('question','order','active','question_type')

class dim_am_i_boring_options_answersSerializer(serializers.ModelSerializer):
    class Meta:
        model = dim_am_i_boring_options_answers
        fields = ('question','option')

class facts_am_i_boring_answersSerializer(serializers.ModelSerializer):
    class Meta:
        model = facts_am_i_boring_answers
        fields = ('user','question', 'answer','order','datetime')

class facts_memosSerializer(serializers.ModelSerializer):
    class Meta:
        model = facts_memos
        fields = ('user','message','datetime')      

class chat_facts_feedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = chat_facts_feedback
        fields = ('user_prompt','bot_message','user','feedback_type','reason','created_at')