# Modelos de Mantenimiento Predictivo

Esta carpeta contiene los modelos entrenados para predicción de fallas en equipos.

## Archivos generados automáticamente:

- `modelo_predictivo.joblib` - Modelo Random Forest entrenado
- `scaler.joblib` - Normalizador de datos

## Uso:

1. Entrenar modelo: `POST /api/predictivo/entrenar`
2. Predecir falla: `GET /api/predictivo/predecir/{equipo_id}`
3. Analizar todos: `POST /api/predictivo/analizar`

## Requisitos mínimos:

- 20+ registros de mantenimiento
- 10+ equipos con historial
- Datos de fallas (mantenimientos correctivos)

## Precisión objetivo: >80%
