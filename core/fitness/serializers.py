from rest_framework import serializers
from .models import Exercise, Workout, WorkoutExercise, WorkoutSet

class ExerciseSerializer(serializers.ModelSerializer):
    # Definir secondary_muscles como una lista de strings
    secondary_muscles = serializers.ListField(
        child=serializers.ChoiceField(choices=Exercise.SECONDARY_MUSCLE_CHOICES),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Exercise
        fields = "__all__"
        read_only_fields = ('id',)
        
    def validate_secondary_muscles(self, value):
        """Validar que los músculos secundarios sean válidos"""
        if value:
            valid_choices = [choice[0] for choice in Exercise.SECONDARY_MUSCLE_CHOICES]
            for muscle in value:
                if muscle not in valid_choices:
                    raise serializers.ValidationError(f"'{muscle}' is not a valid secondary muscle choice")
        return value
        
    def validate_video_url(self, value):
        """Validar que la URL del video sea de una plataforma válida"""
        if value and not any(platform in value for platform in ['youtube.com', 'vimeo.com', 'youtu.be']):
            raise serializers.ValidationError("Video URL must be from YouTube or Vimeo")
        return value
        
    def validate(self, data):
        """Validación a nivel de objeto"""
        # Si equipment es bodyweight, is_bodyweight debería ser True
        if data.get('equipment') == 'bodyweight':
            data['is_bodyweight'] = True
            
        # Evitar que primary_muscle esté en secondary_muscles
        primary = data.get('primary_muscle')
        secondary = data.get('secondary_muscles', [])
        if primary and primary in secondary:
            raise serializers.ValidationError("Primary muscle cannot be in secondary muscles list")
            
        return data


class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = "__all__"
        read_only_fields = ('id',)
        
    def validate_rpe(self, value):
        """Validar que RPE esté entre 1 y 10"""
        if value is not None and (value < 1 or value > 10):
            raise serializers.ValidationError("RPE must be between 1 and 10")
        return value
        
    def validate_weight_kg(self, value):
        """Validar que el peso sea positivo"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Weight cannot be negative")
        return value


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    sets = WorkoutSetSerializer(many=True, required=False)
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    
    class Meta:
        model = WorkoutExercise
        fields = "__all__"
        read_only_fields = ('id',)
        
    def validate_sets(self, value):
        """Validar que los números de set sean únicos y consecutivos"""
        if value:
            set_numbers = [s.get('set_number') for s in value]
            # Verificar que sean únicos
            if len(set_numbers) != len(set(set_numbers)):
                raise serializers.ValidationError("Set numbers must be unique")
            # Verificar que sean consecutivos desde 1
            expected = list(range(1, len(set_numbers) + 1))
            if sorted(set_numbers) != expected:
                raise serializers.ValidationError("Set numbers must be consecutive starting from 1")
        return value
        
    def validate_target_sets(self, value):
        """Validar que target_sets sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("Target sets must be greater than 0")
        return value
        
    def validate_target_reps(self, value):
        """Validar que target_reps sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("Target reps must be greater than 0")
        return value


class WorkoutSerializer(serializers.ModelSerializer):
    workout_exercises = WorkoutExerciseSerializer(many=True, read_only=True)
    exercise_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workout
        fields = "__all__"
        read_only_fields = ('id', 'user')
        
    def get_exercise_count(self, obj):
        """Retorna el número de ejercicios en el workout"""
        return obj.workout_exercises.count()
        
    def validate_duration_min(self, value):
        """Validar que la duración sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0 minutes")
        return value
        
    def validate_date(self, value):
        """Validar que la fecha no sea futura"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Workout date cannot be in the future")
        return value


# Serializers adicionales para casos específicos
class WorkoutCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear workouts con ejercicios y sets anidados"""
    workout_exercises = WorkoutExerciseSerializer(many=True, required=False)
    
    class Meta:
        model = Workout
        fields = ['date', 'notes', 'duration_min', 'workout_exercises']
        
    def validate_workout_exercises(self, value):
        """Validar que los ejercicios tengan órdenes únicos"""
        if value:
            orders = [ex.get('order') for ex in value]
            if len(orders) != len(set(orders)):
                raise serializers.ValidationError("Exercise orders must be unique")
        return value
        
    def create(self, validated_data):
        """Crear workout con ejercicios y sets anidados"""
        from django.db import transaction
        
        workout_exercises_data = validated_data.pop('workout_exercises', [])
        
        with transaction.atomic():
            # Crear el workout base
            workout = Workout.objects.create(
                user=self.context['request'].user,
                **validated_data
            )
            
            # Crear ejercicios y sets
            for exercise_data in workout_exercises_data:
                sets_data = exercise_data.pop('sets', [])
                
                workout_exercise = WorkoutExercise.objects.create(
                    workout=workout,
                    **exercise_data
                )
                
                # Crear sets para este ejercicio
                for set_data in sets_data:
                    WorkoutSet.objects.create(
                        workout_exercise=workout_exercise,
                        **set_data
                    )
            
            return workout


class WorkoutUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualizar workouts con nested data"""
    workout_exercises = WorkoutExerciseSerializer(many=True, required=False)
    
    class Meta:
        model = Workout
        fields = ['date', 'notes', 'duration_min', 'workout_exercises']
        
    def validate_workout_exercises(self, value):
        """Validar que los ejercicios tengan órdenes únicos"""
        if value:
            orders = [ex.get('order') for ex in value]
            if len(orders) != len(set(orders)):
                raise serializers.ValidationError("Exercise orders must be unique")
        return value
        
    def validate_date(self, value):
        """Validar que la fecha no sea futura"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Workout date cannot be in the future")
        return value
        
    def validate_duration_min(self, value):
        """Validar que la duración sea positiva"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0 minutes")
        return value
        
    def update(self, instance, validated_data):
        """Actualizar workout con manejo inteligente de ejercicios"""
        from django.db import transaction
        
        workout_exercises_data = validated_data.pop('workout_exercises', None)
        
        with transaction.atomic():
            # Actualizar campos básicos del workout
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Manejo inteligente de ejercicios
            if workout_exercises_data is not None:
                self._update_workout_exercises(instance, workout_exercises_data)
            
            return instance
    
    def _update_workout_exercises(self, workout, exercises_data):
        """Actualizar ejercicios de manera inteligente"""
        # Estrategia: reemplazar completamente (más simple y consistente)
        workout.workout_exercises.all().delete()
        
        for exercise_data in exercises_data:
            sets_data = exercise_data.pop('sets', [])
            
            workout_exercise = WorkoutExercise.objects.create(
                workout=workout,
                **exercise_data
            )
            
            for set_data in sets_data:
                WorkoutSet.objects.create(
                    workout_exercise=workout_exercise,
                    **set_data
                )


class WorkoutDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para mostrar workouts completos"""
    workout_exercises = WorkoutExerciseSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Workout
        fields = "__all__"
