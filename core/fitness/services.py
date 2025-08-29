"""
StatsService - Servicio simple para cálculos de métricas de fitness.
"""

from datetime import datetime, timedelta
from django.db.models import Sum, Max, Count, F
from django.utils import timezone
from .models import Workout, WorkoutExercise, WorkoutSet, Exercise
from decimal import Decimal


class StatsService:
    """Servicio simple para estadísticas de fitness"""
    
    def __init__(self, user):
        self.user = user
    
    def calculate_volume(self, date_from=None, date_to=None, exercise=None):
        """Calcula volumen total (reps × weight)"""
        # Query base
        sets = WorkoutSet.objects.filter(
            workout_exercise__workout__user=self.user
        )
        
        # Filtros
        if date_from:
            sets = sets.filter(workout_exercise__workout__date__gte=date_from)
        if date_to:
            sets = sets.filter(workout_exercise__workout__date__lte=date_to)
        if exercise:
            sets = sets.filter(workout_exercise__exercise=exercise)
        
        # Calcular volumen
        total_volume = Decimal('0')
        daily_volumes = []
        workout_count = 0
        
        for workout_set in sets.select_related('workout_exercise__workout'):
            if workout_set.weight and workout_set.reps:
                volume = workout_set.weight * workout_set.reps
                total_volume += volume
        
        # Contar workouts únicos
        unique_workouts = sets.values('workout_exercise__workout').distinct().count()
        
        # Volumen promedio diario
        if date_from and date_to:
            days = (date_to - date_from).days + 1
            avg_daily_volume = total_volume / days if days > 0 else Decimal('0')
        else:
            avg_daily_volume = Decimal('0')
        
        return {
            'total_volume': total_volume,
            'average_daily_volume': avg_daily_volume,
            'workout_count': unique_workouts,
            'daily_volumes': []  # Simplificado por ahora
        }
    
    def calculate_top_sets(self, date_from=None, date_to=None, exercise=None, limit=10):
        """Obtiene los mejores sets por volumen"""
        sets = WorkoutSet.objects.filter(
            workout_exercise__workout__user=self.user,
            weight__isnull=False,
            reps__isnull=False
        ).select_related(
            'workout_exercise__exercise',
            'workout_exercise__workout'
        )
        
        # Filtros
        if date_from:
            sets = sets.filter(workout_exercise__workout__date__gte=date_from)
        if date_to:
            sets = sets.filter(workout_exercise__workout__date__lte=date_to)
        if exercise:
            sets = sets.filter(workout_exercise__exercise=exercise)
        
        # Ordenar por volumen y tomar los top
        top_sets = []
        for workout_set in sets.order_by('-weight', '-reps')[:limit]:
            volume = workout_set.weight * workout_set.reps if workout_set.weight and workout_set.reps else 0
            estimated_1rm = self._calculate_1rm(workout_set.weight, workout_set.reps)
            
            top_sets.append({
                'date': workout_set.workout_exercise.workout.date,
                'exercise_name': workout_set.workout_exercise.exercise.name,
                'exercise_id': workout_set.workout_exercise.exercise.id,
                'weight': workout_set.weight,
                'reps': workout_set.reps,
                'volume': volume,
                'workout_id': workout_set.workout_exercise.workout.id,
                'estimated_1rm': estimated_1rm
            })
        
        return top_sets
    
    def calculate_estimated_1rm(self, exercise, date_from=None, date_to=None):
        """Calcula 1RM estimado para un ejercicio"""
        sets = WorkoutSet.objects.filter(
            workout_exercise__workout__user=self.user,
            workout_exercise__exercise=exercise,
            weight__isnull=False,
            reps__isnull=False
        ).select_related('workout_exercise__workout')
        
        # Filtros
        if date_from:
            sets = sets.filter(workout_exercise__workout__date__gte=date_from)
        if date_to:
            sets = sets.filter(workout_exercise__workout__date__lte=date_to)
        
        if not sets.exists():
            return {
                'current_estimated_1rm': None,
                'max_estimated_1rm': None,
                'improvement': None,
                'improvement_percentage': None,
                'data_points': []
            }
        
        # Calcular 1RM para cada set
        max_1rm = Decimal('0')
        data_points = []
        
        for workout_set in sets:
            estimated_1rm = self._calculate_1rm(workout_set.weight, workout_set.reps)
            if estimated_1rm > max_1rm:
                max_1rm = estimated_1rm
            
            data_points.append({
                'date': workout_set.workout_exercise.workout.date,
                'estimated_1rm': estimated_1rm,
                'weight': workout_set.weight,
                'reps': workout_set.reps,
                'workout_id': workout_set.workout_exercise.workout.id
            })
        
        return {
            'current_estimated_1rm': max_1rm,
            'max_estimated_1rm': max_1rm,
            'improvement': None,
            'improvement_percentage': None,
            'data_points': data_points
        }
    
    def calculate_consistency(self, days=30):
        """Calcula consistencia de entrenamiento"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        workouts = Workout.objects.filter(
            user=self.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_workouts = workouts.count()
        unique_days = workouts.values('date').distinct().count()
        
        consistency_percentage = (unique_days / days) * 100 if days > 0 else 0
        avg_workouts_per_week = (total_workouts / days) * 7 if days > 0 else 0
        
        return {
            'total_workouts': total_workouts,
            'active_days': unique_days,
            'consistency_percentage': round(consistency_percentage, 2),
            'average_workouts_per_week': round(avg_workouts_per_week, 2),
            'longest_streak_days': 0,  # Simplificado
            'current_streak_days': 0   # Simplificado
        }
    
    def _calculate_1rm(self, weight, reps):
        """Fórmula de Epley: 1RM = weight × (1 + reps/30)"""
        if not weight or not reps or reps <= 0:
            return Decimal('0')
        return weight * (1 + Decimal(str(reps)) / 30)
