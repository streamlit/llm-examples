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