from django.urls import path
from .views import *

urlpatterns = [
    path('historical-sessions', historicalSessionsView.as_view()),
    path('lulu-trainning', LuluTrainningView.as_view()),
    path('user-milestones', UsersMilestonesView.as_view()),
]
