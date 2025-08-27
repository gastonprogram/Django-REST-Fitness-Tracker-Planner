from django.shortcuts import render
from rest_framework import generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Exercise
from .serializers import ExerciseSerializer

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