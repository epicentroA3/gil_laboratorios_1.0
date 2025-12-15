"""
API de Mantenimiento Predictivo con IA
Endpoints para entrenar modelo, predecir fallas y generar alertas automáticas
Precisión objetivo: >80%
"""
from flask import Blueprint, request, jsonify
from ..services.predictivo_service import MantenimientoPredictivo
from ..utils.database import DatabaseManager

predictivo_bp = Blueprint('predictivo', __name__)
db = DatabaseManager()
servicio = MantenimientoPredictivo(db)


@predictivo_bp.route('/estado', methods=['GET'])
def estado_modelo():
    """
    GET /api/predictivo/estado
    Retorna estado del modelo (entrenado o no, precisión, etc.)
    """
    try:
        info = servicio.obtener_estado_modelo()
        return jsonify({
            'success': True,
            **info,
            'mensaje': 'Modelo listo para predicciones' if info['modelo_entrenado'] else 'Modelo no entrenado. Ejecute POST /api/predictivo/entrenar'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@predictivo_bp.route('/entrenar', methods=['POST'])
def entrenar_modelo():
    """
    POST /api/predictivo/entrenar
    Entrena el modelo con datos históricos de mantenimiento.
    Requiere al menos 5 equipos con historial de mantenimiento.
    """
    print("🤖 API Predictivo: POST /api/predictivo/entrenar llamado")
    try:
        resultado = servicio.entrenar_modelo()
        status_code = 200 if resultado.get('success') else 400
        return jsonify(resultado), status_code
    except Exception as e:
        print(f"❌ Error entrenando modelo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@predictivo_bp.route('/predecir/<int:equipo_id>', methods=['GET'])
def predecir_equipo(equipo_id):
    """
    GET /api/predictivo/predecir/{equipo_id}
    Predice probabilidad de falla para un equipo específico.
    Retorna probabilidad y nivel de riesgo.
    """
    print(f"🤖 API Predictivo: GET /api/predictivo/predecir/{equipo_id} llamado")
    try:
        prob = servicio.predecir_falla(equipo_id)
        
        if prob is None:
            return jsonify({
                'success': False, 
                'error': 'No se pudo predecir. Verifique que el modelo esté entrenado y el equipo exista.'
            }), 400
        
        # Determinar nivel de riesgo
        if prob >= 0.85:
            riesgo = 'CRÍTICO'
            color = '#dc2626'
            recomendacion = 'Programar mantenimiento inmediato'
        elif prob >= 0.7:
            riesgo = 'ALTO'
            color = '#ea580c'
            recomendacion = 'Programar mantenimiento en los próximos 7 días'
        elif prob >= 0.5:
            riesgo = 'MEDIO'
            color = '#ca8a04'
            recomendacion = 'Monitorear y programar revisión'
        else:
            riesgo = 'BAJO'
            color = '#16a34a'
            recomendacion = 'Continuar con mantenimiento preventivo normal'
        
        return jsonify({
            'success': True,
            'equipo_id': equipo_id,
            'probabilidad_falla': round(prob * 100, 2),
            'riesgo': riesgo,
            'color': color,
            'recomendacion': recomendacion,
            'anticipacion_dias': 7 if prob >= 0.7 else 14
        }), 200
        
    except Exception as e:
        print(f"❌ Error prediciendo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@predictivo_bp.route('/analizar', methods=['POST'])
def analizar_equipos():
    """
    POST /api/predictivo/analizar
    Analiza todos los equipos y genera alertas predictivas automáticas.
    Solo genera alertas para equipos con >70% probabilidad de falla.
    """
    print("🤖 API Predictivo: POST /api/predictivo/analizar llamado")
    try:
        resultado = servicio.analizar_todos_equipos()
        status_code = 200 if resultado.get('success') else 400
        return jsonify(resultado), status_code
    except Exception as e:
        print(f"❌ Error analizando equipos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@predictivo_bp.route('/estadisticas', methods=['GET'])
def estadisticas_predictivo():
    """
    GET /api/predictivo/estadisticas
    Retorna estadísticas del sistema predictivo.
    """
    try:
        # Contar alertas predictivas
        alertas_predictivas = db.obtener_uno("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado_alerta = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
                SUM(CASE WHEN estado_alerta = 'resuelta' THEN 1 ELSE 0 END) as resueltas,
                SUM(CASE WHEN prioridad = 'critica' THEN 1 ELSE 0 END) as criticas
            FROM alertas_mantenimiento
            WHERE tipo_alerta = 'falla_predicha'
        """)
        
        # Equipos analizables
        equipos = db.obtener_uno("""
            SELECT COUNT(*) as total FROM equipos WHERE estado != 'dado_baja'
        """)
        
        # Datos de entrenamiento disponibles
        datos_entrenamiento = db.obtener_uno("""
            SELECT COUNT(DISTINCT e.id) as equipos_con_historial
            FROM equipos e
            INNER JOIN historial_mantenimiento hm ON e.id = hm.id_equipo
        """)
        
        info_modelo = servicio.obtener_estado_modelo()
        
        return jsonify({
            'success': True,
            'modelo': info_modelo,
            'alertas_predictivas': {
                'total': alertas_predictivas['total'] or 0,
                'pendientes': alertas_predictivas['pendientes'] or 0,
                'resueltas': alertas_predictivas['resueltas'] or 0,
                'criticas': alertas_predictivas['criticas'] or 0
            },
            'equipos': {
                'total': equipos['total'] or 0,
                'con_historial': datos_entrenamiento['equipos_con_historial'] or 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
