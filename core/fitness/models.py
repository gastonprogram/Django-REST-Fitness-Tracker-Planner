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