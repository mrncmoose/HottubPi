from django.db import models
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

PUMP_SPEEDS = (
    ('HIGH', 'HIGH'),
    ('LOW', 'LOW'),
    ('OFF', 'OFF')
)

class Setpoint(models.Model):
    temperature = models.FloatField(default=5.0)
    pumpSpeed = models.CharField(
        max_length = 20,
        choices = PUMP_SPEEDS,
        default = 'OFF'
     )
    light = models.BooleanField(default=False)

    def __str__(self) -> str:
        return '{0} C - {1} - light {2}'.format(self.temperature, self.pumpSpeed, self.light)
    