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
    WorkoutUpdateSerializer
)

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
