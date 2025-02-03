from django.contrib import admin

from .models import historicalSessions, UsersMilestones, luluTrainning

admin.site.register(historicalSessions)
admin.site.register(UsersMilestones)
admin.site.register(luluTrainning)