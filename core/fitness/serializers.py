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


# Stats Serializers

class VolumeDataPointSerializer(serializers.Serializer):
    """Serializer para un punto de datos de volumen"""
    date = serializers.DateField()
    volume = serializers.DecimalField(max_digits=10, decimal_places=2)
    exercise_name = serializers.CharField(required=False, allow_null=True)
    exercise_id = serializers.IntegerField(required=False, allow_null=True)


class VolumeStatsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de estadísticas de volumen"""
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    exercise = serializers.CharField(required=False, allow_null=True)
    exercise_id = serializers.IntegerField(required=False, allow_null=True)
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_daily_volume = serializers.DecimalField(max_digits=10, decimal_places=2)
    workout_count = serializers.IntegerField()
    daily_volumes = VolumeDataPointSerializer(many=True)


class TopSetSerializer(serializers.Serializer):
    """Serializer para un set récord"""
    date = serializers.DateField()
    exercise_name = serializers.CharField()
    exercise_id = serializers.IntegerField()
    weight = serializers.DecimalField(max_digits=8, decimal_places=2)
    reps = serializers.IntegerField()
    volume = serializers.DecimalField(max_digits=10, decimal_places=2)
    workout_id = serializers.IntegerField()
    estimated_1rm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)


class TopSetsStatsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de sets récord"""
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField()
    exercise = serializers.CharField(required=False, allow_null=True)
    exercise_id = serializers.IntegerField(required=False, allow_null=True)
    limit = serializers.IntegerField()
    top_sets = TopSetSerializer(many=True)


class OneRMDataPointSerializer(serializers.Serializer):
    """Serializer para un punto de datos de 1RM estimado"""
    date = serializers.DateField()
    estimated_1rm = serializers.DecimalField(max_digits=8, decimal_places=2)
    weight = serializers.DecimalField(max_digits=8, decimal_places=2)
    reps = serializers.IntegerField()
    workout_id = serializers.IntegerField()


class OneRMStatsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de estadísticas de 1RM"""
    exercise = serializers.CharField()
    exercise_id = serializers.IntegerField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    current_estimated_1rm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    max_estimated_1rm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    improvement = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    improvement_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    data_points = OneRMDataPointSerializer(many=True)


class ConsistencyStatsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de estadísticas de consistencia"""
    time_window_days = serializers.IntegerField()
    total_workouts = serializers.IntegerField()
    active_days = serializers.IntegerField()
    consistency_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    average_workouts_per_week = serializers.DecimalField(max_digits=4, decimal_places=2)
    longest_streak_days = serializers.IntegerField()
    current_streak_days = serializers.IntegerField()


# Request Serializers for validation

class VolumeStatsRequestSerializer(serializers.Serializer):
    """Serializer para validar parámetros de request de volumen"""
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    exercise_id = serializers.IntegerField(required=False, min_value=1)

    def validate(self, data):
        """Validaciones custom"""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to")
        
        # Limitar rango máximo a 2 años
        if date_from and date_to:
            delta = date_to - date_from
            if delta.days > 730:
                raise serializers.ValidationError("Date range cannot exceed 2 years")
        
        return data


class TopSetsStatsRequestSerializer(serializers.Serializer):
    """Serializer para validar parámetros de request de top sets"""
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    exercise_id = serializers.IntegerField(required=False, min_value=1)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)

    def validate(self, data):
        """Validaciones custom"""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to")
        
        return data


class OneRMStatsRequestSerializer(serializers.Serializer):
    """Serializer para validar parámetros de request de 1RM"""
    exercise_id = serializers.IntegerField(required=True, min_value=1)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, data):
        """Validaciones custom"""
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to")
        
        # Limitar rango máximo a 1 año para 1RM
        if date_from and date_to:
            delta = date_to - date_from
            if delta.days > 365:
                raise serializers.ValidationError("Date range cannot exceed 1 year for 1RM stats")
        
        return data


class ConsistencyStatsRequestSerializer(serializers.Serializer):
    """Serializer para validar parámetros de request de consistencia"""
    days = serializers.IntegerField(required=False, min_value=1, max_value=365, default=30)