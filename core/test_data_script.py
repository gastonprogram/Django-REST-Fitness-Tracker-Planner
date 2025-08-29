#!/usr/bin/env python
"""
Script para inyectar datos de prueba en el sistema de workouts.
Ejecutar desde el directorio core/ con: python test_data_script.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from fitness.models import Exercise, Workout, WorkoutExercise, WorkoutSet

User = get_user_model()


def create_test_user():
    """Crear usuario de prueba si no existe"""
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Usuario creado: {username} / {password}")
    else:
        print(f"✅ Usuario ya existe: {username}")
    
    return user


def create_test_workouts(user):
    """Crear workouts de prueba con ejercicios y sets"""
    
    # Verificar que tenemos ejercicios disponibles
    exercises = Exercise.objects.all()[:10]  # Tomar los primeros 10
    if not exercises:
        print("❌ Error: No hay ejercicios disponibles. Ejecuta: python manage.py loaddata exercises.json")
        return
    
    print(f"📋 Usando ejercicios: {[ex.name for ex in exercises[:5]]}...")
    
    # Workout 1: Entrenamiento básico
    workout1 = Workout.objects.create(
        user=user,
        date=date.today() - timedelta(days=2),
        notes="Entrenamiento de pecho y tríceps - Principiante",
        duration_min=45
    )
    
    # Ejercicio 1: Push-ups (bodyweight)
    we1 = WorkoutExercise.objects.create(
        workout=workout1,
        exercise=exercises[0],  # Push-ups
        order=1,
        target_sets=3,
        target_reps=10
    )
    
    # Sets para Push-ups
    for i in range(1, 4):
        WorkoutSet.objects.create(
            workout_exercise=we1,
            set_number=i,
            reps_completed=10 - i + 1,  # 10, 9, 8 reps
            weight_kg=None,  # Bodyweight
            rpe=6.0 + i,  # 7.0, 8.0, 9.0
            rest_sec=60
        )
    
    # Ejercicio 2: Bench Press
    if len(exercises) > 1:
        we2 = WorkoutExercise.objects.create(
            workout=workout1,
            exercise=exercises[1],  # Bench Press
            order=2,
            target_sets=3,
            target_reps=8
        )
        
        # Sets para Bench Press
        weights = [60.0, 62.5, 65.0]
        for i in range(1, 4):
            WorkoutSet.objects.create(
                workout_exercise=we2,
                set_number=i,
                reps_completed=8 if i < 3 else 6,  # 8, 8, 6 reps
                weight_kg=weights[i-1],
                rpe=7.0 + i * 0.5,  # 7.5, 8.0, 8.5
                rest_sec=90 + i * 10  # 100, 110, 120 sec
            )
    
    print(f"✅ Workout 1 creado: {workout1.notes}")
    
    # Workout 2: Entrenamiento avanzado
    workout2 = Workout.objects.create(
        user=user,
        date=date.today() - timedelta(days=1),
        notes="Entrenamiento completo - Avanzado",
        duration_min=90
    )
    
    # Múltiples ejercicios para workout avanzado
    exercise_configs = [
        {'exercise_idx': 3, 'order': 1, 'sets': 4, 'reps': 6, 'weights': [70, 75, 80, 82.5]},
        {'exercise_idx': 4, 'order': 2, 'sets': 3, 'reps': 8, 'weights': [None, None, None]},  # Pull-ups
        {'exercise_idx': 5, 'order': 3, 'sets': 3, 'reps': 12, 'weights': [20, 22.5, 25]},
    ]
    
    for config in exercise_configs:
        if config['exercise_idx'] < len(exercises):
            we = WorkoutExercise.objects.create(
                workout=workout2,
                exercise=exercises[config['exercise_idx']],
                order=config['order'],
                target_sets=config['sets'],
                target_reps=config['reps']
            )
            
            for i in range(1, config['sets'] + 1):
                WorkoutSet.objects.create(
                    workout_exercise=we,
                    set_number=i,
                    reps_completed=config['reps'] - (i-1),  # Reps decrecientes
                    weight_kg=config['weights'][i-1] if i <= len(config['weights']) else None,
                    rpe=6.0 + i * 0.5,
                    rest_sec=120 if config['weights'][0] else 90  # Más descanso para ejercicios con peso
                )
    
    print(f"✅ Workout 2 creado: {workout2.notes}")
    
    # Workout 3: Solo estructura (sin sets)
    workout3 = Workout.objects.create(
        user=user,
        date=date.today(),
        notes="Workout planeado para hoy - Sin ejecutar",
        duration_min=60
    )
    
    # Solo planificación, sin sets ejecutados
    if len(exercises) > 6:
        WorkoutExercise.objects.create(
            workout=workout3,
            exercise=exercises[6],
            order=1,
            target_sets=3,
            target_reps=10
        )
        
        WorkoutExercise.objects.create(
            workout=workout3,
            exercise=exercises[7],
            order=2,
            target_sets=4,
            target_reps=8
        )
    
    print(f"✅ Workout 3 creado: {workout3.notes}")
    
    return [workout1, workout2, workout3]


def print_summary(user):
    """Mostrar resumen de datos creados"""
    workouts = Workout.objects.filter(user=user)
    exercises_used = WorkoutExercise.objects.filter(workout__user=user).count()
    sets_completed = WorkoutSet.objects.filter(workout_exercise__workout__user=user).count()
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*50)
    print(f"👤 Usuario: {user.username}")
    print(f"🏋️ Workouts: {workouts.count()}")
    print(f"💪 Ejercicios en workouts: {exercises_used}")
    print(f"📈 Sets completados: {sets_completed}")
    print("\n📋 Lista de workouts:")
    
    for workout in workouts:
        exercise_count = workout.workout_exercises.count()
        set_count = WorkoutSet.objects.filter(workout_exercise__workout=workout).count()
        print(f"   • {workout.date} - {workout.notes[:40]}... ({exercise_count} ejercicios, {set_count} sets)")


def print_api_examples(user):
    """Mostrar ejemplos de cómo usar la API"""
    print("\n" + "="*50)
    print("🔗 EJEMPLOS PARA PROBAR LA API")
    print("="*50)
    
    print("1. Obtener token (necesario para workouts):")
    print(f'   curl -X POST http://127.0.0.1:8000/auth/login/ \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d "{{\\"username\\": \\"{user.username}\\", \\"password\\": \\"testpass123\\"}}"')
    
    print("\n2. Listar workouts:")
    print('   curl -H "Authorization: Bearer TU_TOKEN" http://127.0.0.1:8000/api/workouts/')
    
    print("\n3. Ver detalle de workout:")
    print('   curl -H "Authorization: Bearer TU_TOKEN" http://127.0.0.1:8000/api/workouts/1/')
    
    print("\n4. Crear workout completo:")
    print('   curl -X POST http://127.0.0.1:8000/api/workouts/ \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -H "Authorization: Bearer TU_TOKEN" \\')
    print('     -d "{ \\"date\\": \\"2025-08-30\\", \\"notes\\": \\"Nuevo workout\\", ... }"')


def main():
    """Función principal"""
    print("🚀 INICIANDO INYECCIÓN DE DATOS DE PRUEBA")
    print("="*50)
    
    try:
        # Crear usuario
        user = create_test_user()
        
        # Crear workouts
        workouts = create_test_workouts(user)
        
        # Mostrar resumen
        print_summary(user)
        
        # Mostrar ejemplos de API
        print_api_examples(user)
        
        print("\n✅ ¡Datos de prueba creados exitosamente!")
        print("💡 Ahora puedes probar la API con los ejemplos mostrados arriba.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
