from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ExerciseFilter, ExerciseDetailView, ExerciseListView

urlpatterns = [
    path("exercises/", ExerciseListView.as_view(), name="exercise-list"),
    path("exercises/<int:pk>/", ExerciseDetailView.as_view(), name="exercise-detail"),
]
