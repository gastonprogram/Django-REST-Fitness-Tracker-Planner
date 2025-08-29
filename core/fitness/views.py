from django.shortcuts import render
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import F
from .models import Exercise, Workout, WorkoutExercise, WorkoutSet
from .serializers import (
    ExerciseSerializer, WorkoutSerializer, WorkoutCreateSerializer, 
    WorkoutDetailSerializer, WorkoutExerciseSerializer, WorkoutSetSerializer,
    WorkoutUpdateSerializer, VolumeStatsResponseSerializer, VolumeStatsRequestSerializer,
    TopSetsStatsResponseSerializer, TopSetsStatsRequestSerializer,
    OneRMStatsResponseSerializer, OneRMStatsRequestSerializer,
    ConsistencyStatsResponseSerializer, ConsistencyStatsRequestSerializer
)
from .services import StatsService
from .throttles import StatsThrottle, VolumeStatsThrottle, OneRMStatsThrottle

# Create your views here.


class ExerciseFilter(django_filters.FilterSet):
    """Filtro personalizado para ejercicios"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    primary_muscle = django_filters.ChoiceFilter(choices=Exercise.PRIMARY_MUSCLE_CHOICES)
    equipment = django_filters.ChoiceFilter(choices=Exercise.EQUIPMENT_CHOICES)
    difficulty = django_filters.ChoiceFilter(choices=Exercise.DIFFICULTY_CHOICES)
    is_bodyweight = django_filters.BooleanFilter()
    
    class Meta:
        model = Exercise
        fields = ['name', 'primary_muscle', 'equipment', 'difficulty', 'is_bodyweight']


class WorkoutFilter(django_filters.FilterSet):
    """Filtro personalizado para workouts"""
    from_date = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    date = django_filters.DateFilter()
    
    class Meta:
        model = Workout
        fields = ['date']


class ExerciseListView(generics.ListAPIView):
    """
    Lista todos los ejercicios con opciones de filtrado y búsqueda.
    
    Filtros disponibles:
    - primary_muscle: Músculo primario trabajado
    - equipment: Equipo necesario
    - difficulty: Nivel de dificultad
    - is_bodyweight: Si es ejercicio de peso corporal
    
    Búsqueda disponible por:
    - name: Nombre del ejercicio
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.AllowAny]  # cualquiera puede ver ejercicios
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ExerciseFilter
    
    # Búsqueda por nombre
    search_fields = ['name']
    
    # Ordenamiento
    ordering_fields = ['name', 'difficulty', 'primary_muscle']
    ordering = ['name']  # Ordenamiento por defecto


class ExerciseDetailView(generics.RetrieveAPIView):
    """
    Obtiene el detalle de un ejercicio específico por su ID.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.AllowAny]  # cualquiera puede ver ejercicios


class WorkoutListView(generics.ListCreateAPIView):
    """
    Lista y crea workouts del usuario autenticado.
    
    GET: Lista workouts con filtros opcionales:
    - from_date: Fecha desde (YYYY-MM-DD)
    - to_date: Fecha hasta (YYYY-MM-DD)
    
    POST: Crea un nuevo workout
    """
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = WorkoutFilter
    ordering_fields = ['date', 'duration_min']
    ordering = ['-date']  # Más recientes primero
    
    def get_queryset(self):
        """Solo workouts del usuario autenticado"""
        return Workout.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Usar serializer específico para creación"""
        if self.request.method == 'POST':
            return WorkoutCreateSerializer
        return WorkoutSerializer


class WorkoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un workout específico.
    
    GET: Detalle completo del workout con ejercicios y sets
    PATCH: Actualiza campos específicos del workout
    DELETE: Elimina el workout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo workouts del usuario autenticado"""
        return Workout.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Usar serializer específico para cada método"""
        if self.request.method == 'GET':
            return WorkoutDetailSerializer
        elif self.request.method in ['PATCH', 'PUT']:
            return WorkoutUpdateSerializer  
        return WorkoutSerializer


# Stats Views
class VolumeStatsView(APIView):
    """Estadísticas de volumen"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [VolumeStatsThrottle]

    def get(self, request):
        # Parámetros simples
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        exercise_id = request.query_params.get('exercise_id')

        # Parsear fechas
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_from format'}, status=400)
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_to format'}, status=400)

        # Ejercicio si se especifica
        exercise = None
        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return Response({'error': 'Exercise not found'}, status=404)

        # Obtener stats
        stats_service = StatsService(request.user)
        data = stats_service.calculate_volume(date_from, date_to, exercise)

        return Response({
            'date_from': date_from,
            'date_to': date_to,
            'exercise': exercise.name if exercise else None,
            'exercise_id': exercise.id if exercise else None,
            **data
        })


class TopSetsStatsView(APIView):
    """Top sets (récords personales)"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [StatsThrottle]

    def get(self, request):
        # Parámetros
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        exercise_id = request.query_params.get('exercise_id')
        limit = int(request.query_params.get('limit', 10))

        # Parsear fechas
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_from format'}, status=400)
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_to format'}, status=400)

        # Ejercicio si se especifica
        exercise = None
        if exercise_id:
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return Response({'error': 'Exercise not found'}, status=404)

        # Obtener stats
        stats_service = StatsService(request.user)
        top_sets = stats_service.calculate_top_sets(date_from, date_to, exercise, limit)

        return Response({
            'date_from': date_from,
            'date_to': date_to,
            'exercise': exercise.name if exercise else None,
            'exercise_id': exercise.id if exercise else None,
            'limit': limit,
            'top_sets': top_sets
        })


class OneRMStatsView(APIView):
    """Estadísticas de 1RM estimado"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [OneRMStatsThrottle]

    def get(self, request):
        # exercise_id es requerido
        exercise_id = request.query_params.get('exercise_id')
        if not exercise_id:
            return Response({'error': 'exercise_id is required'}, status=400)

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Parsear fechas
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_from format'}, status=400)
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date_to format'}, status=400)

        # Validar ejercicio
        try:
            exercise = Exercise.objects.get(id=exercise_id)
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercise not found'}, status=404)

        # Obtener stats
        stats_service = StatsService(request.user)
        data = stats_service.calculate_estimated_1rm(exercise, date_from, date_to)

        return Response({
            'exercise': exercise.name,
            'exercise_id': exercise.id,
            'date_from': date_from,
            'date_to': date_to,
            **data
        })


class ConsistencyStatsView(APIView):
    """Estadísticas de consistencia"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [StatsThrottle]

    def get(self, request):
        days = int(request.query_params.get('days', 30))

        # Obtener stats
        stats_service = StatsService(request.user)
        data = stats_service.calculate_consistency(days)

        return Response({
            'time_window_days': days,
            **data
        })