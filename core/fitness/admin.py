from django.contrib import admin
from .models import Exercise

# Register your models here.

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_muscle', 'equipment', 'difficulty', 'is_bodyweight')
    list_filter = ('primary_muscle', 'equipment', 'difficulty', 'is_bodyweight')
    search_fields = ('name', 'primary_muscle', 'secondary_muscles')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'primary_muscle', 'secondary_muscles')
        }),
        ('Exercise Details', {
            'fields': ('equipment', 'difficulty', 'is_bodyweight', 'video_url')
        }),
    )
