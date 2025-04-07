from django.contrib import admin

from .models import *

admin.site.register(historicalSessions)
admin.site.register(UsersMilestones)
admin.site.register(luluTrainning)
admin.site.register(chat_dim_onboarding_questions)
admin.site.register(chat_dim_onboarding_options_answers)
admin.site.register(dim_question_type)
admin.site.register(chat_facts_onboarding_answers)
admin.site.register(diary_facts)

admin.site.register(chat_memories)
admin.site.register(chat_facts_feedback)
admin.site.register(facts_memos)

admin.site.register(dim_am_i_boring_questions)
admin.site.register(dim_am_i_boring_options_answers)
admin.site.register(facts_am_i_boring_answers)