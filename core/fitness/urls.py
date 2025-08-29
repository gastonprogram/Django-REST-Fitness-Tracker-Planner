from django.urls import path
from .views import (
    ExerciseDetailView, ExerciseListView,
    WorkoutListView, WorkoutDetailView,
    VolumeStatsView, TopSetsStatsView, OneRMStatsView, ConsistencyStatsView
)

urlpatterns = [
    
    # exercises endpoints
    path("exercises/", ExerciseListView.as_view(), name="exercise-list"),
    path("exercises/<int:pk>/", ExerciseDetailView.as_view(), name="exercise-detail"),
    
    
    # workouts endpoints
    path("workouts/", WorkoutListView.as_view(), name="workout-list"),
    path("workouts/<int:pk>/", WorkoutDetailView.as_view(), name="workout-detail"),
    
    # Stats endpoints
    path("stats/volume/", VolumeStatsView.as_view(), name="stats-volume"),
    path("stats/top-sets/", TopSetsStatsView.as_view(), name="stats-top-sets"),
    path("stats/1rm/", OneRMStatsView.as_view(), name="stats-1rm"),
    path("stats/consistency/", ConsistencyStatsView.as_view(), name="stats-consistency"),
]
