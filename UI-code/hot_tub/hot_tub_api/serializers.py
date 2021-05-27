from .models import Setpoint

from rest_framework import serializers

class SetpointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Setpoint
        fields = ['temperature', 'pumpSpeed', 'light']
