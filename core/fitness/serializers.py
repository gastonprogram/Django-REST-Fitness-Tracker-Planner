from rest_framework import serializers
from .models import Exercise

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