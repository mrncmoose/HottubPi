from .models import Setpoint
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import SetpointSerializer


class SetpointViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Setpoint.objects.all()
    serializer_class = SetpointSerializer
    permission_classes = [permissions.IsAuthenticated]
