"""
Custom throttling classes for fitness API
"""
from rest_framework.throttling import UserRateThrottle


class StatsThrottle(UserRateThrottle):
    """
    Throttle para endpoints de estadísticas
    Limita a 100 requests por hora por usuario
    """
    scope = 'stats'
    rate = '100/hour'


class VolumeStatsThrottle(UserRateThrottle):
    """
    Throttle específico para estadísticas de volumen
    Limita a 30 requests por minuto por usuario
    """
    scope = 'volume_stats'
    rate = '30/min'


class OneRMStatsThrottle(UserRateThrottle):
    """
    Throttle específico para estadísticas de 1RM
    Limita a 20 requests por minuto por usuario
    """
    scope = 'onerm_stats'
    rate = '20/min'
