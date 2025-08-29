from django.urls import path
from .views import (
    ExerciseDetailView, ExerciseListView,
    WorkoutListView, WorkoutDetailView
)

urlpatterns = [
    
    # exercises endpoints
    path("exercises/", ExerciseListView.as_view(), name="exercise-list"),
    path("exercises/<int:pk>/", ExerciseDetailView.as_view(), name="exercise-detail"),
    
    
    # workouts endpoints
    path("workouts/", WorkoutListView.as_view(), name="workout-list"),
    path("workouts/<int:pk>/", WorkoutDetailView.as_view(), name="workout-detail"),
    
]
