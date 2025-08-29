# API Estadísticas - Documentación

## Endpoints de Estadísticas

### 1. Estadísticas de Volumen

**Endpoint:** `GET /api/stats/volume/`

**Descripción:** Obtiene estadísticas de volumen de entrenamiento (reps × peso) para un período específico.

**Parámetros de consulta:**

- `date_from` (opcional): Fecha de inicio en formato YYYY-MM-DD. Por defecto: 30 días atrás
- `date_to` (opcional): Fecha final en formato YYYY-MM-DD. Por defecto: hoy
- `exercise_id` (opcional): ID del ejercicio específico. Si no se proporciona, incluye todos los ejercicios

**Límites:**

- Rango máximo: 2 años
- Throttling: 30 requests/minuto por usuario

**Respuesta de ejemplo:**

```json
{
  "date_from": "2025-07-30",
  "date_to": "2025-08-29",
  "exercise": "Bench Press",
  "exercise_id": 1,
  "total_volume": "15750.00",
  "average_daily_volume": "525.00",
  "workout_count": 12,
  "daily_volumes": [
    {
      "date": "2025-08-29",
      "volume": "1250.00",
      "exercise_name": "Bench Press",
      "exercise_id": 1
    }
  ]
}
```

### 2. Sets Récord (Top Sets)

**Endpoint:** `GET /api/stats/top-sets/`

**Descripción:** Obtiene los mejores sets (récords personales) ordenados por volumen.

**Parámetros de consulta:**

- `date_from` (opcional): Fecha de inicio en formato YYYY-MM-DD
- `date_to` (opcional): Fecha final en formato YYYY-MM-DD. Por defecto: hoy
- `exercise_id` (opcional): ID del ejercicio específico
- `limit` (opcional): Número de sets a retornar (1-100). Por defecto: 10

**Throttling:** 100 requests/hora por usuario

**Respuesta de ejemplo:**

```json
{
  "date_from": null,
  "date_to": "2025-08-29",
  "exercise": null,
  "exercise_id": null,
  "limit": 10,
  "top_sets": [
    {
      "date": "2025-08-25",
      "exercise_name": "Bench Press",
      "exercise_id": 1,
      "weight": "100.00",
      "reps": 8,
      "volume": "800.00",
      "workout_id": 5,
      "estimated_1rm": "125.00"
    }
  ]
}
```

### 3. Estadísticas de 1RM Estimado

**Endpoint:** `GET /api/stats/1rm/`

**Descripción:** Calcula y rastrea el progreso del 1RM estimado para un ejercicio específico usando la fórmula de Epley.

**Parámetros de consulta:**

- `exercise_id` (requerido): ID del ejercicio
- `date_from` (opcional): Fecha de inicio en formato YYYY-MM-DD. Por defecto: 30 días atrás
- `date_to` (opcional): Fecha final en formato YYYY-MM-DD. Por defecto: hoy

**Límites:**

- Rango máximo: 1 año
- Throttling: 20 requests/minuto por usuario

**Respuesta de ejemplo:**

```json
{
  "exercise": "Bench Press",
  "exercise_id": 1,
  "date_from": "2025-07-30",
  "date_to": "2025-08-29",
  "current_estimated_1rm": "125.00",
  "max_estimated_1rm": "130.00",
  "improvement": "10.00",
  "improvement_percentage": "8.70",
  "data_points": [
    {
      "date": "2025-08-29",
      "estimated_1rm": "125.00",
      "weight": "100.00",
      "reps": 8,
      "workout_id": 5
    }
  ]
}
```

### 4. Estadísticas de Consistencia

**Endpoint:** `GET /api/stats/consistency/`

**Descripción:** Analiza la consistencia del entrenamiento en una ventana temporal.

**Parámetros de consulta:**

- `days` (opcional): Ventana temporal en días (1-365). Por defecto: 30

**Throttling:** 100 requests/hora por usuario

**Respuesta de ejemplo:**

```json
{
  "time_window_days": 30,
  "total_workouts": 12,
  "active_days": 10,
  "consistency_percentage": "33.33",
  "average_workouts_per_week": "2.80",
  "longest_streak_days": 5,
  "current_streak_days": 2
}
```

## Códigos de Estado

### Éxito

- `200 OK`: Solicitud exitosa

### Errores del Cliente

- `400 Bad Request`: Parámetros inválidos o fuera de rango
- `401 Unauthorized`: Token de autenticación requerido
- `404 Not Found`: Ejercicio no encontrado
- `429 Too Many Requests`: Límite de throttling alcanzado

### Errores del Servidor

- `500 Internal Server Error`: Error interno del servidor

## Formato de Errores

```json
{
  "error": "Descripción del error"
}
```

Para errores de validación:

```json
{
  "field_name": ["Error message"]
}
```

## Autenticación

Todos los endpoints requieren autenticación JWT. Incluir en el header:

```
Authorization: Bearer <token>
```

## Notas de Implementación

### Optimizaciones

- Las consultas utilizan agregaciones de base de datos para rendimiento
- Se recomienda implementar caché Redis para consultas frecuentes
- Los índices en date, user_id y exercise_id son esenciales

### Fórmulas Utilizadas

- **Volumen:** reps × peso
- **1RM Estimado (Epley):** peso × (1 + reps/30)
- **Consistencia:** (días_activos / días_totales) × 100

### Limitaciones

- Los datos se calculan en tiempo real sin caché por defecto
- Las fechas deben estar en formato ISO (YYYY-MM-DD)
- Los rangos temporales están limitados para prevenir sobrecarga
