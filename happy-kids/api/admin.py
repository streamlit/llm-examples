from django.contrib import admin

from .models import historicalSessions, UsersMilestones, luluTrainning, chat_dim_onboarding_questions

admin.site.register(historicalSessions)
admin.site.register(UsersMilestones)
admin.site.register(luluTrainning)
admin.site.register(chat_dim_onboarding_questions)