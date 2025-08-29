from django.conf import settings
from django.db import models

# Create your models here.


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    
    #choices for primary muscle
    PRIMARY_MUSCLE_CHOICES = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("legs", "Legs"),
        ("arms", "Arms"),
        ("shoulders", "Shoulders"),
    ]
    primary_muscle = models.CharField(max_length=100, choices=PRIMARY_MUSCLE_CHOICES)
    
    #choices for secondary muscles
    SECONDARY_MUSCLE_CHOICES = [
        ("chest", "Chest"),
        ("back", "Back"),
        ("legs", "Legs"),
        ("arms", "Arms"),
        ("shoulders", "Shoulders"),
    ]

    secondary_muscles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of secondary muscles worked"
    )

    #choices for equipment
    EQUIPMENT_CHOICES = [
        ("dumbbell", "Dumbbell"),
        ("barbell", "Barbell"),
        ("kettlebell", "Kettlebell"),
        ("bodyweight", "Bodyweight"),
        ("machine", "Machine"),
    ]
    equipment = models.CharField(max_length=100, choices=EQUIPMENT_CHOICES)
    
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    difficulty = models.CharField(max_length=100, choices=DIFFICULTY_CHOICES)
    
    is_bodyweight = models.BooleanField(default=False)
    video_url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Workout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    duration_min = models.PositiveIntegerField(help_text="Duration in minutes")
    

    

class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    target_sets = models.PositiveIntegerField()
    target_reps = models.PositiveIntegerField()
    
    

class WorkoutSet(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveIntegerField()
    reps_completed = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    rest_sec = models.PositiveIntegerField(blank=True, null=True)