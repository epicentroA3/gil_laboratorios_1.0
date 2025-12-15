"""
API de Mantenimiento de Equipos
Gestión de mantenimientos preventivos y correctivos
"""

from flask import Blueprint, request, jsonify, session
from ..utils.database import DatabaseManager
from datetime import datetime, timedelta
import json

mantenimiento_bp = Blueprint('mantenimiento', __name__)
db = DatabaseManager()

# =========================================================
# HISTORIAL DE MANTENIMIENTO - CRUD
# =========================================================

@mantenimiento_bp.route('', methods=['GET'])
def listar_mantenimientos():
    """
    GET /api/mantenimiento
    Lista el historial de mantenimientos con filtros opcionales
    
    Query params:
    - equipo_id: Filtrar por equipo
    - tipo_id: Filtrar por tipo de mantenimiento
    - estado: Filtrar por estado (en_proceso, completado, cancelado)
    - fecha_desde: Fecha inicio (YYYY-MM-DD)
    - fecha_hasta: Fecha fin (YYYY-MM-DD)
    - limit: Límite de resultados (default 100)
    """
    print("📋 API Mantenimiento: GET /api/mantenimiento llamado")
    try:
        equipo_id = request.args.get('equipo_id')
        tipo_id = request.args.get('tipo_id')
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limit = request.args.get('limit', 100, type=int)
        
        query = """
            SELECT 
                hm.id,
                hm.id_equipo,
                hm.id_tipo_mantenimiento,
                hm.estado,
                hm.fecha_inicio,
                hm.fecha_fin,
                hm.tecnico_responsable_id,
                hm.descripcion_trabajo,
                hm.partes_reemplazadas,
                hm.costo_mantenimiento,
                hm.tiempo_inactividad_horas,
                hm.observaciones,
                hm.estado_post_mantenimiento,
                hm.proxima_fecha_mantenimiento,
                hm.fecha_registro,
                e.nombre as equipo_nombre,
                e.codigo_interno,
                e.estado as equipo_estado,
                e.estado_fisico as equipo_estado_fisico,
                tm.nombre as tipo_nombre,
                tm.es_preventivo,
                tm.frecuencia_dias as tipo_frecuencia_dias,
                CONCAT(u.nombres, ' ', u.apellidos) as tecnico_nombre
            FROM historial_mantenimiento hm
            LEFT JOIN equipos e ON hm.id_equipo = e.id
            LEFT JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
            LEFT JOIN usuarios u ON hm.tecnico_responsable_id = u.id
            WHERE 1=1
        """
        params = []
        
        if equipo_id:
            query += " AND hm.id_equipo = %s"
            params.append(equipo_id)
        
        if tipo_id:
            query += " AND hm.id_tipo_mantenimiento = %s"
            params.append(tipo_id)
        
        if estado:
            query += " AND hm.estado = %s"
            params.append(estado)
        
        if fecha_desde:
            query += " AND hm.fecha_inicio >= %s"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND hm.fecha_inicio <= %s"
            params.append(fecha_hasta)
        
        query += " ORDER BY hm.fecha_inicio DESC LIMIT %s"
        params.append(limit)
        
        mantenimientos = db.ejecutar_query(query, tuple(params)) or []
        
        # Formatear fechas
        for m in mantenimientos:
            if m.get('fecha_inicio'):
                m['fecha_inicio'] = m['fecha_inicio'].strftime('%Y-%m-%d %H:%M')
            if m.get('fecha_fin'):
                m['fecha_fin'] = m['fecha_fin'].strftime('%Y-%m-%d %H:%M')
            if m.get('proxima_fecha_mantenimiento'):
                m['proxima_fecha_mantenimiento'] = m['proxima_fecha_mantenimiento'].strftime('%Y-%m-%d')
            if m.get('fecha_registro'):
                m['fecha_registro'] = m['fecha_registro'].strftime('%Y-%m-%d %H:%M')
        
        return jsonify({
            'success': True,
            'mantenimientos': mantenimientos,
            'total': len(mantenimientos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/<int:id>', methods=['GET'])
def obtener_mantenimiento(id):
    """
    GET /api/mantenimiento/{id}
    Obtiene detalle de un mantenimiento específico
    """
    try:
        query = """
            SELECT 
                hm.*,
                e.nombre as equipo_nombre,
                e.codigo_interno,
                e.estado as equipo_estado,
                e.estado_fisico as equipo_estado_fisico,
                tm.nombre as tipo_nombre,
                tm.descripcion as tipo_descripcion,
                tm.es_preventivo,
                tm.frecuencia_dias as tipo_frecuencia_dias,
                CONCAT(u.nombres, ' ', u.apellidos) as tecnico_nombre
            FROM historial_mantenimiento hm
            LEFT JOIN equipos e ON hm.id_equipo = e.id
            LEFT JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
            LEFT JOIN usuarios u ON hm.tecnico_responsable_id = u.id
            WHERE hm.id = %s
        """
        mantenimiento = db.obtener_uno(query, (id,))
        
        if not mantenimiento:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Formatear fechas
        if mantenimiento.get('fecha_inicio'):
            mantenimiento['fecha_inicio'] = mantenimiento['fecha_inicio'].strftime('%Y-%m-%d %H:%M')
        if mantenimiento.get('fecha_fin'):
            mantenimiento['fecha_fin'] = mantenimiento['fecha_fin'].strftime('%Y-%m-%d %H:%M')
        if mantenimiento.get('proxima_fecha_mantenimiento'):
            mantenimiento['proxima_fecha_mantenimiento'] = mantenimiento['proxima_fecha_mantenimiento'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'mantenimiento': mantenimiento
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/iniciar', methods=['POST'])
def iniciar_mantenimiento():
    """
    POST /api/mantenimiento/iniciar
    PASO 1: Inicia un mantenimiento - crea registro en estado 'en_proceso' y cambia estado del equipo
    
    Body:
    {
        "id_equipo": 1,
        "id_tipo_mantenimiento": 1,
        "tecnico_responsable_id": 1,  // opcional
        "descripcion_trabajo": "Descripción inicial del trabajo a realizar"  // opcional
    }
    
    Returns: ID del mantenimiento creado para usar en /completar/{id}
    """
    try:
        data = request.get_json() or {}
        errores = {}
        
        # Validaciones
        if not data.get('id_equipo'):
            errores['id_equipo'] = 'El equipo es requerido'
        
        if not data.get('id_tipo_mantenimiento'):
            errores['id_tipo_mantenimiento'] = 'El tipo de mantenimiento es requerido'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Verificar que el equipo existe
        equipo = db.obtener_uno(
            "SELECT id, nombre, estado, estado_fisico FROM equipos WHERE id = %s", 
            (data['id_equipo'],)
        )
        if not equipo:
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        # Verificar que el equipo no esté prestado o dado de baja
        if equipo['estado'] == 'prestado':
            return jsonify({
                'success': False, 
                'error': 'No se puede iniciar mantenimiento. El equipo está prestado.'
            }), 400
        
        if equipo['estado'] == 'dado_baja':
            return jsonify({
                'success': False, 
                'error': 'No se puede iniciar mantenimiento. El equipo está dado de baja.'
            }), 400
        
        # Verificar que no tenga un mantenimiento en proceso
        mant_en_proceso = db.obtener_uno(
            "SELECT id FROM historial_mantenimiento WHERE id_equipo = %s AND estado = 'en_proceso'",
            (data['id_equipo'],)
        )
        if mant_en_proceso:
            return jsonify({
                'success': False, 
                'error': f'El equipo ya tiene un mantenimiento en proceso (ID: {mant_en_proceso["id"]})'
            }), 400
        
        # Obtener tipo de mantenimiento
        tipo = db.obtener_uno(
            "SELECT id, nombre, es_preventivo FROM tipos_mantenimiento WHERE id = %s",
            (data['id_tipo_mantenimiento'],)
        )
        if not tipo:
            return jsonify({'success': False, 'error': 'Tipo de mantenimiento no encontrado'}), 404
        
        # Determinar el nuevo estado del equipo
        nuevo_estado_equipo = 'mantenimiento' if tipo['es_preventivo'] else 'reparacion'
        
        # Crear registro de mantenimiento en estado 'en_proceso'
        nuevo_id = db.insertar('historial_mantenimiento', {
            'id_equipo': data['id_equipo'],
            'id_tipo_mantenimiento': data['id_tipo_mantenimiento'],
            'estado': 'en_proceso',
            'fecha_inicio': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tecnico_responsable_id': data.get('tecnico_responsable_id') or session.get('user_id'),
            'descripcion_trabajo': data.get('descripcion_trabajo', '')
        })
        
        # Actualizar estado del equipo
        db.actualizar('equipos', {
            'estado': nuevo_estado_equipo
        }, 'id = %s', (data['id_equipo'],))
        
        return jsonify({
            'success': True,
            'message': f'Mantenimiento iniciado. Equipo "{equipo["nombre"]}" ahora está en {nuevo_estado_equipo}',
            'id': nuevo_id,
            'equipo': {
                'id': equipo['id'],
                'nombre': equipo['nombre'],
                'estado_anterior': equipo['estado'],
                'estado_nuevo': nuevo_estado_equipo
            },
            'tipo': {
                'id': tipo['id'],
                'nombre': tipo['nombre'],
                'es_preventivo': tipo['es_preventivo']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/completar/<int:id>', methods=['PUT'])
def completar_mantenimiento(id):
    """
    PUT /api/mantenimiento/completar/{id}
    PASO 2: Completa un mantenimiento en proceso
    
    Body:
    {
        "descripcion_trabajo": "Trabajo realizado detallado",
        "partes_reemplazadas": "Lista de partes",
        "costo_mantenimiento": 150000,
        "tiempo_inactividad_horas": 2.5,
        "observaciones": "Observaciones finales",
        "estado_post_mantenimiento": "bueno"  // excelente, bueno, regular, malo
    }
    """
    try:
        data = request.get_json() or {}
        print(f"📋 Completar Mantenimiento ID {id} - Datos recibidos:", data)
        
        # Verificar que el mantenimiento existe y está en proceso
        mantenimiento = db.obtener_uno("""
            SELECT hm.*, e.nombre as equipo_nombre, e.estado as equipo_estado,
                   tm.frecuencia_dias, tm.es_preventivo
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
            WHERE hm.id = %s
        """, (id,))
        
        if not mantenimiento:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        if mantenimiento['estado'] == 'completado':
            return jsonify({'success': False, 'error': 'Este mantenimiento ya fue completado'}), 400
        
        if mantenimiento['estado'] == 'cancelado':
            return jsonify({'success': False, 'error': 'Este mantenimiento fue cancelado'}), 400
        
        # Validaciones
        errores = {}
        descripcion = data.get('descripcion_trabajo', '').strip()
        if descripcion and len(descripcion) < 10:
            errores['descripcion_trabajo'] = 'La descripción debe tener al menos 10 caracteres'
        
        estado_validos = ['excelente', 'bueno', 'regular', 'malo']
        estado_post = data.get('estado_post_mantenimiento', 'bueno')
        print(f"✅ Estado post-mantenimiento recibido: {estado_post}")
        if estado_post not in estado_validos:
            errores['estado_post_mantenimiento'] = f'Estado inválido. Valores válidos: {estado_validos}'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Calcular próxima fecha de mantenimiento
        proxima_fecha = None
        if mantenimiento['frecuencia_dias'] and mantenimiento['frecuencia_dias'] > 0:
            proxima_fecha = datetime.now() + timedelta(days=mantenimiento['frecuencia_dias'])
        
        # Calcular tiempo de inactividad si no se proporciona
        tiempo_inactividad = data.get('tiempo_inactividad_horas')
        if tiempo_inactividad is None and mantenimiento.get('fecha_inicio'):
            fecha_inicio = mantenimiento['fecha_inicio']
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
            tiempo_inactividad = round((datetime.now() - fecha_inicio).total_seconds() / 3600, 2)
        
        # Actualizar el registro de mantenimiento
        db.actualizar('historial_mantenimiento', {
            'estado': 'completado',
            'fecha_fin': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'descripcion_trabajo': descripcion or mantenimiento.get('descripcion_trabajo', ''),
            'partes_reemplazadas': data.get('partes_reemplazadas', ''),
            'costo_mantenimiento': data.get('costo_mantenimiento', 0),
            'tiempo_inactividad_horas': tiempo_inactividad or 0,
            'observaciones': data.get('observaciones', ''),
            'estado_post_mantenimiento': estado_post,
            'proxima_fecha_mantenimiento': proxima_fecha.strftime('%Y-%m-%d') if proxima_fecha else None
        }, 'id = %s', (id,))
        
        # Actualizar estado del equipo
        estado_anterior = mantenimiento['equipo_estado']
        if estado_post in ['excelente', 'bueno', 'regular']:
            db.actualizar('equipos', {
                'estado': 'disponible',
                'estado_fisico': estado_post
            }, 'id = %s', (mantenimiento['id_equipo'],))
            nuevo_estado_equipo = 'disponible'
        else:
            db.actualizar('equipos', {
                'estado': 'reparacion',
                'estado_fisico': 'malo'
            }, 'id = %s', (mantenimiento['id_equipo'],))
            nuevo_estado_equipo = 'reparacion'
        
        # Resolver alertas pendientes (solo si el equipo quedó operativo)
        if estado_post in ['excelente', 'bueno', 'regular']:
            db.ejecutar_query("""
                UPDATE alertas_mantenimiento 
                SET estado_alerta = 'resuelta', 
                    fecha_resolucion = NOW(),
                    observaciones_resolucion = %s
                WHERE id_equipo = %s AND estado_alerta IN ('pendiente', 'en_proceso')
            """, (f'Resuelto por mantenimiento #{id}', mantenimiento['id_equipo']))
        
        return jsonify({
            'success': True,
            'message': f'Mantenimiento completado. Equipo "{mantenimiento["equipo_nombre"]}" ahora está {nuevo_estado_equipo}',
            'id': id,
            'proxima_fecha': proxima_fecha.strftime('%Y-%m-%d') if proxima_fecha else None,
            'equipo': {
                'id': mantenimiento['id_equipo'],
                'nombre': mantenimiento['equipo_nombre'],
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado_equipo,
                'estado_fisico': estado_post
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/cancelar/<int:id>', methods=['PUT'])
def cancelar_mantenimiento(id):
    """
    PUT /api/mantenimiento/cancelar/{id}
    Cancela un mantenimiento en proceso y devuelve el equipo a disponible
    """
    try:
        data = request.get_json() or {}
        
        # Verificar que el mantenimiento existe y está en proceso
        mantenimiento = db.obtener_uno("""
            SELECT hm.*, e.nombre as equipo_nombre, e.estado_fisico
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            WHERE hm.id = %s
        """, (id,))
        
        if not mantenimiento:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        if mantenimiento['estado'] != 'en_proceso':
            return jsonify({'success': False, 'error': 'Solo se pueden cancelar mantenimientos en proceso'}), 400
        
        # Actualizar el registro
        db.actualizar('historial_mantenimiento', {
            'estado': 'cancelado',
            'fecha_fin': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'observaciones': data.get('observaciones', 'Cancelado por usuario')
        }, 'id = %s', (id,))
        
        # Devolver equipo a disponible
        db.actualizar('equipos', {
            'estado': 'disponible'
        }, 'id = %s', (mantenimiento['id_equipo'],))
        
        return jsonify({
            'success': True,
            'message': f'Mantenimiento cancelado. Equipo "{mantenimiento["equipo_nombre"]}" vuelve a estar disponible',
            'id': id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/en-proceso', methods=['GET'])
def listar_en_proceso():
    """
    GET /api/mantenimiento/en-proceso
    Lista todos los mantenimientos en proceso
    """
    try:
        query = """
            SELECT 
                hm.id, hm.id_equipo, hm.estado, hm.fecha_inicio,
                hm.tecnico_responsable_id, hm.descripcion_trabajo,
                e.nombre as equipo_nombre, e.codigo_interno, e.estado as equipo_estado,
                tm.nombre as tipo_nombre, tm.es_preventivo,
                CONCAT(u.nombres, ' ', u.apellidos) as tecnico_nombre
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
            LEFT JOIN usuarios u ON hm.tecnico_responsable_id = u.id
            WHERE hm.estado = 'en_proceso'
            ORDER BY hm.fecha_inicio DESC
        """
        mantenimientos = db.ejecutar_query(query) or []
        
        for m in mantenimientos:
            if m.get('fecha_inicio'):
                m['fecha_inicio'] = m['fecha_inicio'].strftime('%Y-%m-%d %H:%M')
                # Calcular tiempo transcurrido
                fecha_inicio = datetime.strptime(m['fecha_inicio'], '%Y-%m-%d %H:%M')
                m['tiempo_transcurrido_horas'] = round((datetime.now() - fecha_inicio).total_seconds() / 3600, 2)
        
        return jsonify({
            'success': True,
            'mantenimientos': mantenimientos,
            'total': len(mantenimientos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('', methods=['POST'])
def crear_mantenimiento():
    """
    POST /api/mantenimiento
    Registra un mantenimiento completo en un solo paso (para casos donde el trabajo ya se realizó)
    Equivale a iniciar + completar inmediatamente
    
    Body:
    {
        "id_equipo": 1,
        "id_tipo_mantenimiento": 1,
        "fecha_inicio": "2025-12-14 10:00",  // opcional, default: ahora
        "tecnico_responsable_id": 1,
        "descripcion_trabajo": "Limpieza y calibración",
        "partes_reemplazadas": "Filtro, tornillos",
        "costo_mantenimiento": 150000,
        "tiempo_inactividad_horas": 2.5,
        "observaciones": "Equipo en buen estado",
        "estado_post_mantenimiento": "bueno"
    }
    """
    try:
        data = request.get_json()
        errores = {}
        
        # Validaciones
        if not data.get('id_equipo'):
            errores['id_equipo'] = 'El equipo es requerido'
        
        if not data.get('id_tipo_mantenimiento'):
            errores['id_tipo_mantenimiento'] = 'El tipo de mantenimiento es requerido'
        
        descripcion = data.get('descripcion_trabajo', '').strip()
        if not descripcion:
            errores['descripcion_trabajo'] = 'La descripción del trabajo es requerida'
        elif len(descripcion) < 10:
            errores['descripcion_trabajo'] = 'La descripción debe tener al menos 10 caracteres'
        
        estado_validos = ['excelente', 'bueno', 'regular', 'malo']
        estado_post = data.get('estado_post_mantenimiento', 'bueno')
        if estado_post not in estado_validos:
            errores['estado_post_mantenimiento'] = f'Estado inválido. Valores válidos: {estado_validos}'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Verificar que el equipo existe
        equipo = db.obtener_uno("SELECT id, nombre, estado, estado_fisico FROM equipos WHERE id = %s", (data['id_equipo'],))
        if not equipo:
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        # Verificar estado del equipo
        if equipo['estado'] == 'prestado':
            return jsonify({'success': False, 'error': 'No se puede registrar mantenimiento. El equipo está prestado.'}), 400
        if equipo['estado'] == 'dado_baja':
            return jsonify({'success': False, 'error': 'No se puede registrar mantenimiento. El equipo está dado de baja.'}), 400
        
        # Obtener tipo de mantenimiento
        tipo = db.obtener_uno(
            "SELECT frecuencia_dias, es_preventivo, nombre FROM tipos_mantenimiento WHERE id = %s",
            (data['id_tipo_mantenimiento'],)
        )
        if not tipo:
            return jsonify({'success': False, 'error': 'Tipo de mantenimiento no encontrado'}), 404
        
        # Fechas
        fecha_inicio = data.get('fecha_inicio') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fecha_fin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calcular próxima fecha de mantenimiento
        proxima_fecha = None
        if tipo.get('frecuencia_dias') and tipo['frecuencia_dias'] > 0:
            proxima_fecha = datetime.now() + timedelta(days=tipo['frecuencia_dias'])
        
        # Insertar mantenimiento como completado
        nuevo_id = db.insertar('historial_mantenimiento', {
            'id_equipo': data['id_equipo'],
            'id_tipo_mantenimiento': data['id_tipo_mantenimiento'],
            'estado': 'completado',
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'tecnico_responsable_id': data.get('tecnico_responsable_id') or session.get('user_id'),
            'descripcion_trabajo': descripcion,
            'partes_reemplazadas': data.get('partes_reemplazadas', ''),
            'costo_mantenimiento': data.get('costo_mantenimiento', 0),
            'tiempo_inactividad_horas': data.get('tiempo_inactividad_horas', 0),
            'observaciones': data.get('observaciones', ''),
            'estado_post_mantenimiento': estado_post,
            'proxima_fecha_mantenimiento': proxima_fecha.strftime('%Y-%m-%d') if proxima_fecha else None
        })
        
        # Actualizar estado del equipo
        estado_anterior = equipo['estado']
        if estado_post in ['excelente', 'bueno', 'regular']:
            db.actualizar('equipos', {
                'estado': 'disponible',
                'estado_fisico': estado_post
            }, 'id = %s', (data['id_equipo'],))
            nuevo_estado_equipo = 'disponible'
        else:
            db.actualizar('equipos', {
                'estado': 'reparacion',
                'estado_fisico': 'malo'
            }, 'id = %s', (data['id_equipo'],))
            nuevo_estado_equipo = 'reparacion'
        
        # Resolver alertas pendientes
        if estado_post in ['excelente', 'bueno', 'regular']:
            db.ejecutar_query("""
                UPDATE alertas_mantenimiento 
                SET estado_alerta = 'resuelta', 
                    fecha_resolucion = NOW(),
                    observaciones_resolucion = %s
                WHERE id_equipo = %s AND estado_alerta IN ('pendiente', 'en_proceso')
            """, (f'Resuelto por mantenimiento #{nuevo_id}', data['id_equipo']))
        
        return jsonify({
            'success': True,
            'message': f'Mantenimiento registrado. Equipo "{equipo["nombre"]}" ahora está {nuevo_estado_equipo}',
            'id': nuevo_id,
            'proxima_fecha': proxima_fecha.strftime('%Y-%m-%d') if proxima_fecha else None,
            'equipo': {
                'id': equipo['id'],
                'nombre': equipo['nombre'],
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado_equipo,
                'estado_fisico': estado_post
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/<int:id>', methods=['PUT'])
def actualizar_mantenimiento(id):
    """
    PUT /api/mantenimiento/{id}
    Actualiza un registro de mantenimiento completado.
    Si cambia el estado_post_mantenimiento, también actualiza el estado_fisico del equipo.
    """
    try:
        data = request.get_json()
        
        # Verificar que existe y obtener datos del equipo
        existente = db.obtener_uno("""
            SELECT hm.id, hm.id_equipo, hm.estado, hm.estado_post_mantenimiento,
                   e.nombre as equipo_nombre, e.estado_fisico as equipo_estado_fisico
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            WHERE hm.id = %s
        """, (id,))
        if not existente:
            return jsonify({'success': False, 'error': 'Mantenimiento no encontrado'}), 404
        
        # Solo permitir editar mantenimientos completados
        if existente['estado'] == 'en_proceso':
            return jsonify({'success': False, 'error': 'No se puede editar un mantenimiento en proceso. Use el endpoint /completar para finalizarlo.'}), 400
        
        # Validaciones
        errores = {}
        if 'descripcion_trabajo' in data:
            descripcion = data['descripcion_trabajo'].strip()
            if len(descripcion) < 10:
                errores['descripcion_trabajo'] = 'La descripción debe tener al menos 10 caracteres'
        
        estado_validos = ['excelente', 'bueno', 'regular', 'malo']
        nuevo_estado_post = data.get('estado_post_mantenimiento')
        if nuevo_estado_post and nuevo_estado_post not in estado_validos:
            errores['estado_post_mantenimiento'] = f'Estado inválido. Valores válidos: {estado_validos}'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Campos actualizables
        campos_permitidos = [
            'id_tipo_mantenimiento', 'fecha_inicio', 'fecha_fin', 'tecnico_responsable_id',
            'descripcion_trabajo', 'partes_reemplazadas', 'costo_mantenimiento',
            'tiempo_inactividad_horas', 'observaciones', 'estado_post_mantenimiento',
            'proxima_fecha_mantenimiento'
        ]
        
        datos_actualizar = {k: v for k, v in data.items() if k in campos_permitidos}
        
        if datos_actualizar:
            db.actualizar('historial_mantenimiento', datos_actualizar, 'id = %s', (id,))
        
        # Si cambió el estado_post_mantenimiento, actualizar estado_fisico del equipo
        equipo_actualizado = False
        mantenimiento_reactivado = False
        if nuevo_estado_post and nuevo_estado_post != existente['estado_post_mantenimiento']:
            if nuevo_estado_post in ['excelente', 'bueno', 'regular']:
                db.actualizar('equipos', {
                    'estado': 'disponible',
                    'estado_fisico': nuevo_estado_post
                }, 'id = %s', (existente['id_equipo'],))
            else:
                # Si el estado es 'malo', el equipo pasa a reparación y el mantenimiento vuelve a en_proceso
                db.actualizar('equipos', {
                    'estado': 'reparacion',
                    'estado_fisico': 'malo'
                }, 'id = %s', (existente['id_equipo'],))
                
                # Reactivar el mantenimiento a en_proceso
                db.actualizar('historial_mantenimiento', {
                    'estado': 'en_proceso',
                    'fecha_fin': None
                }, 'id = %s', (id,))
                mantenimiento_reactivado = True
            equipo_actualizado = True
        
        mensaje = 'Mantenimiento actualizado correctamente'
        if mantenimiento_reactivado:
            mensaje = f'El equipo "{existente["equipo_nombre"]}" requiere más trabajo. Mantenimiento reactivado a "en proceso"'
        elif equipo_actualizado:
            mensaje += f'. Estado físico del equipo "{existente["equipo_nombre"]}" actualizado a {nuevo_estado_post}'
        
        return jsonify({
            'success': True,
            'message': mensaje,
            'equipo_actualizado': equipo_actualizado,
            'mantenimiento_reactivado': mantenimiento_reactivado
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =========================================================
# TIPOS DE MANTENIMIENTO - CRUD
# =========================================================

@mantenimiento_bp.route('/tipos/inicializar', methods=['POST'])
def inicializar_tipos():
    """
    POST /api/mantenimiento/tipos/inicializar
    Inserta tipos de mantenimiento por defecto si no existen
    """
    print("📋 API Mantenimiento: POST /api/mantenimiento/tipos/inicializar llamado")
    try:
        tipos_default = [
            ('Preventivo General', 'Mantenimiento preventivo rutinario para asegurar el buen funcionamiento del equipo', 30, True),
            ('Correctivo', 'Mantenimiento correctivo para reparar fallas o averías', 0, False),
            ('Calibración', 'Calibración y ajuste de equipos de medición', 90, True),
            ('Limpieza Profunda', 'Limpieza exhaustiva de componentes internos y externos', 15, True),
            ('Revisión Técnica', 'Inspección técnica completa del equipo', 60, True),
            ('Reparación Mayor', 'Reparación de componentes críticos o reemplazo de piezas importantes', 0, False),
            ('Actualización de Software', 'Actualización de firmware o software del equipo', 180, True),
            ('Verificación de Seguridad', 'Verificación de sistemas de seguridad y protección', 45, True)
        ]
        
        insertados = 0
        for nombre, descripcion, frecuencia, es_preventivo in tipos_default:
            existente = db.obtener_uno("SELECT id FROM tipos_mantenimiento WHERE nombre = %s", (nombre,))
            if not existente:
                db.insertar('tipos_mantenimiento', {
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'frecuencia_dias': frecuencia,
                    'es_preventivo': es_preventivo
                })
                insertados += 1
        
        return jsonify({
            'success': True,
            'message': f'Se insertaron {insertados} tipos de mantenimiento',
            'insertados': insertados
        }), 200
    except Exception as e:
        print(f"Error inicializando tipos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/tecnicos', methods=['GET'])
def listar_tecnicos_mantenimiento():
    """
    GET /api/mantenimiento/tecnicos
    Lista los usuarios que tienen permiso de mantenimiento según su rol.
    Filtra por roles que tengan el permiso 'mantenimiento' o 'all' en su JSON de permisos.
    """
    print("📋 API Mantenimiento: GET /api/mantenimiento/tecnicos llamado")
    try:
        # Obtener usuarios activos cuyos roles tienen permiso de mantenimiento
        query = """
            SELECT 
                u.id,
                u.documento,
                u.nombres,
                u.apellidos,
                CONCAT(u.nombres, ' ', u.apellidos) as nombre_completo,
                u.email,
                u.telefono,
                r.id as id_rol,
                r.nombre_rol,
                r.permisos
            FROM usuarios u
            INNER JOIN roles r ON u.id_rol = r.id
            WHERE u.estado = 'activo'
              AND r.estado = 'activo'
              AND (
                  JSON_EXTRACT(r.permisos, '$.mantenimiento') = true
                  OR JSON_EXTRACT(r.permisos, '$.all') = true
              )
            ORDER BY u.nombres, u.apellidos
        """
        tecnicos = db.ejecutar_query(query) or []
        
        # Formatear respuesta
        tecnicos_formateados = []
        for t in tecnicos:
            tecnicos_formateados.append({
                'id': t['id'],
                'documento': t['documento'],
                'nombre': t['nombre_completo'],
                'nombres': t['nombres'],
                'apellidos': t['apellidos'],
                'email': t['email'],
                'telefono': t['telefono'],
                'rol_id': t['id_rol'],
                'rol_nombre': t['nombre_rol']
            })
        
        return jsonify({
            'success': True,
            'tecnicos': tecnicos_formateados,
            'total': len(tecnicos_formateados)
        }), 200
        
    except Exception as e:
        print(f"Error listando técnicos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/tipos', methods=['GET'])
def listar_tipos():
    """
    GET /api/mantenimiento/tipos
    Lista todos los tipos de mantenimiento
    """
    print("📋 API Mantenimiento: GET /api/mantenimiento/tipos llamado")
    try:
        tipos = db.ejecutar_query("""
            SELECT id, nombre, descripcion, frecuencia_dias, es_preventivo
            FROM tipos_mantenimiento
            ORDER BY nombre
        """) or []
        
        return jsonify({
            'success': True,
            'tipos': tipos
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/tipos', methods=['POST'])
def crear_tipo():
    """
    POST /api/mantenimiento/tipos
    Crea un nuevo tipo de mantenimiento
    """
    try:
        data = request.get_json()
        errores = {}
        
        nombre = data.get('nombre', '').strip()
        if not nombre:
            errores['nombre'] = 'El nombre es requerido'
        elif len(nombre) < 3:
            errores['nombre'] = 'El nombre debe tener al menos 3 caracteres'
        
        # Verificar unicidad
        existente = db.obtener_uno(
            "SELECT id FROM tipos_mantenimiento WHERE nombre = %s",
            (nombre,)
        )
        if existente:
            errores['nombre'] = 'Ya existe un tipo con este nombre'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        nuevo_id = db.insertar('tipos_mantenimiento', {
            'nombre': nombre,
            'descripcion': data.get('descripcion', ''),
            'frecuencia_dias': data.get('frecuencia_dias', 30),
            'es_preventivo': data.get('es_preventivo', True)
        })
        
        return jsonify({
            'success': True,
            'message': 'Tipo de mantenimiento creado',
            'id': nuevo_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/tipos/<int:id>', methods=['PUT'])
def actualizar_tipo(id):
    """
    PUT /api/mantenimiento/tipos/{id}
    Actualiza un tipo de mantenimiento
    """
    try:
        data = request.get_json()
        
        existente = db.obtener_uno("SELECT id FROM tipos_mantenimiento WHERE id = %s", (id,))
        if not existente:
            return jsonify({'success': False, 'error': 'Tipo no encontrado'}), 404
        
        errores = {}
        if 'nombre' in data:
            nombre = data['nombre'].strip()
            if len(nombre) < 3:
                errores['nombre'] = 'El nombre debe tener al menos 3 caracteres'
            
            # Verificar unicidad (excluyendo el actual)
            duplicado = db.obtener_uno(
                "SELECT id FROM tipos_mantenimiento WHERE nombre = %s AND id != %s",
                (nombre, id)
            )
            if duplicado:
                errores['nombre'] = 'Ya existe un tipo con este nombre'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        campos_permitidos = ['nombre', 'descripcion', 'frecuencia_dias', 'es_preventivo']
        datos_actualizar = {k: v for k, v in data.items() if k in campos_permitidos}
        
        if datos_actualizar:
            db.actualizar('tipos_mantenimiento', datos_actualizar, 'id = %s', (id,))
        
        return jsonify({
            'success': True,
            'message': 'Tipo actualizado correctamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/tipos/<int:id>', methods=['DELETE'])
def eliminar_tipo(id):
    """
    DELETE /api/mantenimiento/tipos/{id}
    Elimina un tipo de mantenimiento
    """
    try:
        # Verificar que no tenga mantenimientos asociados
        en_uso = db.obtener_uno(
            "SELECT COUNT(*) as total FROM historial_mantenimiento WHERE id_tipo_mantenimiento = %s",
            (id,)
        )
        if en_uso and en_uso['total'] > 0:
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar. Hay {en_uso["total"]} mantenimientos asociados a este tipo.'
            }), 400
        
        db.eliminar('tipos_mantenimiento', 'id = %s', (id,))
        
        return jsonify({
            'success': True,
            'message': 'Tipo eliminado correctamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =========================================================
# ALERTAS DE MANTENIMIENTO
# =========================================================

@mantenimiento_bp.route('/alertas', methods=['GET'])
def listar_alertas():
    """
    GET /api/mantenimiento/alertas
    Lista alertas de mantenimiento
    
    Query params:
    - estado: pendiente, en_proceso, resuelta, cancelada
    - prioridad: baja, media, alta, critica
    - equipo_id: Filtrar por equipo
    """
    try:
        estado = request.args.get('estado')
        prioridad = request.args.get('prioridad')
        equipo_id = request.args.get('equipo_id')
        
        query = """
            SELECT 
                am.id,
                am.id_equipo,
                am.tipo_alerta,
                am.descripcion_alerta,
                am.fecha_alerta,
                am.fecha_limite,
                am.prioridad,
                am.estado_alerta,
                am.asignado_a,
                am.fecha_resolucion,
                am.observaciones_resolucion,
                e.nombre as equipo_nombre,
                e.codigo_interno,
                CONCAT(u.nombres, ' ', u.apellidos) as asignado_nombre
            FROM alertas_mantenimiento am
            LEFT JOIN equipos e ON am.id_equipo = e.id
            LEFT JOIN usuarios u ON am.asignado_a = u.id
            WHERE 1=1
        """
        params = []
        
        if estado:
            query += " AND am.estado_alerta = %s"
            params.append(estado)
        
        if prioridad:
            query += " AND am.prioridad = %s"
            params.append(prioridad)
        
        if equipo_id:
            query += " AND am.id_equipo = %s"
            params.append(equipo_id)
        
        query += " ORDER BY FIELD(am.prioridad, 'critica', 'alta', 'media', 'baja'), am.fecha_limite ASC"
        
        alertas = db.ejecutar_query(query, tuple(params)) or []
        
        # Formatear fechas
        for a in alertas:
            if a.get('fecha_alerta'):
                a['fecha_alerta'] = a['fecha_alerta'].strftime('%Y-%m-%d %H:%M')
            if a.get('fecha_limite'):
                a['fecha_limite'] = a['fecha_limite'].strftime('%Y-%m-%d')
            if a.get('fecha_resolucion'):
                a['fecha_resolucion'] = a['fecha_resolucion'].strftime('%Y-%m-%d %H:%M')
        
        return jsonify({
            'success': True,
            'alertas': alertas,
            'total': len(alertas)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/alertas/<int:id>/asignar', methods=['PUT'])
def asignar_alerta(id):
    """
    PUT /api/mantenimiento/alertas/{id}/asignar
    Asigna una alerta a un técnico
    """
    try:
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        
        if not usuario_id:
            return jsonify({'success': False, 'error': 'Usuario requerido'}), 400
        
        db.actualizar('alertas_mantenimiento', {
            'asignado_a': usuario_id,
            'estado_alerta': 'en_proceso'
        }, 'id = %s', (id,))
        
        return jsonify({
            'success': True,
            'message': 'Alerta asignada correctamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/alertas/<int:id>/resolver', methods=['PUT'])
def resolver_alerta(id):
    """
    PUT /api/mantenimiento/alertas/{id}/resolver
    Marca una alerta como resuelta
    """
    try:
        data = request.get_json()
        observaciones = data.get('observaciones', '')
        
        db.actualizar('alertas_mantenimiento', {
            'estado_alerta': 'resuelta',
            'fecha_resolucion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'observaciones_resolucion': observaciones
        }, 'id = %s', (id,))
        
        return jsonify({
            'success': True,
            'message': 'Alerta resuelta correctamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/alertas/<int:id>/cancelar', methods=['PUT'])
def cancelar_alerta(id):
    """
    PUT /api/mantenimiento/alertas/{id}/cancelar
    Cancela una alerta
    """
    try:
        data = request.get_json()
        observaciones = data.get('observaciones', 'Cancelada por usuario')
        
        db.actualizar('alertas_mantenimiento', {
            'estado_alerta': 'cancelada',
            'observaciones_resolucion': observaciones
        }, 'id = %s', (id,))
        
        return jsonify({
            'success': True,
            'message': 'Alerta cancelada'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mantenimiento_bp.route('/alertas/generar', methods=['POST'])
def generar_alertas():
    """
    POST /api/mantenimiento/alertas/generar
    Genera alertas automáticas basadas en:
    - Mantenimientos vencidos (próxima fecha pasada)
    - Mantenimientos próximos (7 días)
    - Equipos en mal estado
    """
    try:
        alertas_creadas = 0
        
        # 1. Alertas por mantenimiento vencido
        vencidos = db.ejecutar_query("""
            SELECT DISTINCT hm.id_equipo, e.nombre, hm.proxima_fecha_mantenimiento
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            WHERE hm.proxima_fecha_mantenimiento < CURDATE()
            AND hm.id_equipo NOT IN (
                SELECT id_equipo FROM alertas_mantenimiento 
                WHERE tipo_alerta = 'mantenimiento_vencido' 
                AND estado_alerta IN ('pendiente', 'en_proceso')
            )
        """) or []
        
        for v in vencidos:
            db.insertar('alertas_mantenimiento', {
                'id_equipo': v['id_equipo'],
                'tipo_alerta': 'mantenimiento_vencido',
                'descripcion_alerta': f"Mantenimiento vencido para {v['nombre']}. Fecha programada: {v['proxima_fecha_mantenimiento']}",
                'fecha_limite': v['proxima_fecha_mantenimiento'],
                'prioridad': 'alta',
                'estado_alerta': 'pendiente'
            })
            alertas_creadas += 1
        
        # 2. Alertas por mantenimiento próximo (7 días)
        proximos = db.ejecutar_query("""
            SELECT DISTINCT hm.id_equipo, e.nombre, hm.proxima_fecha_mantenimiento
            FROM historial_mantenimiento hm
            JOIN equipos e ON hm.id_equipo = e.id
            WHERE hm.proxima_fecha_mantenimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            AND hm.id_equipo NOT IN (
                SELECT id_equipo FROM alertas_mantenimiento 
                WHERE tipo_alerta = 'mantenimiento_programado' 
                AND estado_alerta IN ('pendiente', 'en_proceso')
            )
        """) or []
        
        for p in proximos:
            db.insertar('alertas_mantenimiento', {
                'id_equipo': p['id_equipo'],
                'tipo_alerta': 'mantenimiento_programado',
                'descripcion_alerta': f"Mantenimiento programado para {p['nombre']}. Fecha: {p['proxima_fecha_mantenimiento']}",
                'fecha_limite': p['proxima_fecha_mantenimiento'],
                'prioridad': 'media',
                'estado_alerta': 'pendiente'
            })
            alertas_creadas += 1
        
        # 3. Alertas por equipos en mal estado
        mal_estado = db.ejecutar_query("""
            SELECT id, nombre, codigo_interno
            FROM equipos
            WHERE estado_fisico = 'malo'
            AND id NOT IN (
                SELECT id_equipo FROM alertas_mantenimiento 
                WHERE tipo_alerta = 'revision_urgente' 
                AND estado_alerta IN ('pendiente', 'en_proceso')
            )
        """) or []
        
        for m in mal_estado:
            db.insertar('alertas_mantenimiento', {
                'id_equipo': m['id'],
                'tipo_alerta': 'revision_urgente',
                'descripcion_alerta': f"Revisión urgente requerida para {m['nombre']} ({m['codigo_interno']}). Estado físico: malo",
                'fecha_limite': datetime.now().strftime('%Y-%m-%d'),
                'prioridad': 'critica',
                'estado_alerta': 'pendiente'
            })
            alertas_creadas += 1
        
        return jsonify({
            'success': True,
            'message': f'Se generaron {alertas_creadas} alertas',
            'alertas_creadas': alertas_creadas
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =========================================================
# ESTADÍSTICAS
# =========================================================

@mantenimiento_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """
    GET /api/mantenimiento/estadisticas
    Obtiene estadísticas del módulo de mantenimiento
    """
    print("📋 API Mantenimiento: GET /api/mantenimiento/estadisticas llamado")
    try:
        stats = {}
        
        # Total de mantenimientos
        total = db.obtener_uno("SELECT COUNT(*) as total FROM historial_mantenimiento")
        stats['total_mantenimientos'] = total['total'] if total else 0
        
        # Mantenimientos este mes
        este_mes = db.obtener_uno("""
            SELECT COUNT(*) as total FROM historial_mantenimiento 
            WHERE MONTH(fecha_fin) = MONTH(CURDATE()) 
            AND YEAR(fecha_fin) = YEAR(CURDATE())
            AND estado = 'completado'
        """)
        stats['mantenimientos_mes'] = este_mes['total'] if este_mes else 0
        
        # Por tipo
        por_tipo = db.ejecutar_query("""
            SELECT tm.nombre, COUNT(hm.id) as total
            FROM tipos_mantenimiento tm
            LEFT JOIN historial_mantenimiento hm ON tm.id = hm.id_tipo_mantenimiento
            GROUP BY tm.id, tm.nombre
        """) or []
        stats['por_tipo'] = {t['nombre']: t['total'] for t in por_tipo}
        
        # Alertas pendientes
        alertas = db.obtener_uno("""
            SELECT 
                SUM(CASE WHEN estado_alerta = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
                SUM(CASE WHEN estado_alerta = 'en_proceso' THEN 1 ELSE 0 END) as en_proceso,
                SUM(CASE WHEN prioridad = 'critica' AND estado_alerta = 'pendiente' THEN 1 ELSE 0 END) as criticas
            FROM alertas_mantenimiento
        """)
        stats['alertas_pendientes'] = alertas['pendientes'] if alertas else 0
        stats['alertas_en_proceso'] = alertas['en_proceso'] if alertas else 0
        stats['alertas_criticas'] = alertas['criticas'] if alertas else 0
        
        # Costo total de mantenimientos
        costos = db.obtener_uno("""
            SELECT 
                SUM(costo_mantenimiento) as total,
                AVG(costo_mantenimiento) as promedio
            FROM historial_mantenimiento
        """)
        stats['costo_total'] = float(costos['total']) if costos and costos['total'] else 0
        stats['costo_promedio'] = float(costos['promedio']) if costos and costos['promedio'] else 0
        
        # Tiempo de inactividad total
        tiempo = db.obtener_uno("""
            SELECT SUM(tiempo_inactividad_horas) as total
            FROM historial_mantenimiento
        """)
        stats['tiempo_inactividad_total'] = float(tiempo['total']) if tiempo and tiempo['total'] else 0
        
        # Equipos que requieren mantenimiento pronto (próximos 7 días)
        proximos = db.obtener_uno("""
            SELECT COUNT(DISTINCT id_equipo) as total
            FROM historial_mantenimiento
            WHERE proxima_fecha_mantenimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        """)
        stats['equipos_mantenimiento_proximo'] = proximos['total'] if proximos else 0
        
        return jsonify({
            'success': True,
            'estadisticas': stats
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =========================================================
# VALIDACIÓN HÍBRIDA
# =========================================================

@mantenimiento_bp.route('/validar', methods=['GET'])
def validar_campos():
    """
    GET /api/mantenimiento/validar
    Validación en tiempo real para el formulario
    
    Query params:
    - campo: nombre del campo a validar
    - valor: valor a validar
    - equipo_id: (opcional) para validaciones específicas
    """
    try:
        campo = request.args.get('campo')
        valor = request.args.get('valor', '').strip()
        equipo_id = request.args.get('equipo_id')
        
        resultado = {'valido': True, 'mensaje': ''}
        
        if campo == 'descripcion_trabajo':
            if not valor:
                resultado = {'valido': False, 'mensaje': 'La descripción es requerida'}
            elif len(valor) < 10:
                resultado = {'valido': False, 'mensaje': f'Mínimo 10 caracteres (actual: {len(valor)})'}
            elif len(valor) > 1000:
                resultado = {'valido': False, 'mensaje': 'Máximo 1000 caracteres'}
        
        elif campo == 'costo_mantenimiento':
            try:
                costo = float(valor) if valor else 0
                if costo < 0:
                    resultado = {'valido': False, 'mensaje': 'El costo no puede ser negativo'}
            except ValueError:
                resultado = {'valido': False, 'mensaje': 'Ingrese un valor numérico válido'}
        
        elif campo == 'tiempo_inactividad':
            try:
                tiempo = float(valor) if valor else 0
                if tiempo < 0:
                    resultado = {'valido': False, 'mensaje': 'El tiempo no puede ser negativo'}
            except ValueError:
                resultado = {'valido': False, 'mensaje': 'Ingrese un valor numérico válido'}
        
        elif campo == 'equipo_id':
            if not valor:
                resultado = {'valido': False, 'mensaje': 'Seleccione un equipo'}
            else:
                equipo = db.obtener_uno("SELECT id, nombre FROM equipos WHERE id = %s", (valor,))
                if not equipo:
                    resultado = {'valido': False, 'mensaje': 'Equipo no encontrado'}
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'valido': False, 'mensaje': str(e)}), 500


# =========================================================
# HISTORIAL POR EQUIPO
# =========================================================

@mantenimiento_bp.route('/equipo/<int:equipo_id>', methods=['GET'])
def historial_equipo(equipo_id):
    """
    GET /api/mantenimiento/equipo/{equipo_id}
    Obtiene el historial completo de mantenimientos de un equipo
    """
    try:
        # Verificar que el equipo existe
        equipo = db.obtener_uno("""
            SELECT id, nombre, codigo_interno, estado, estado_fisico
            FROM equipos WHERE id = %s
        """, (equipo_id,))
        
        if not equipo:
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        # Obtener historial
        historial = db.ejecutar_query("""
            SELECT 
                hm.*,
                tm.nombre as tipo_nombre,
                tm.es_preventivo,
                CONCAT(u.nombres, ' ', u.apellidos) as tecnico_nombre
            FROM historial_mantenimiento hm
            LEFT JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
            LEFT JOIN usuarios u ON hm.tecnico_responsable_id = u.id
            WHERE hm.id_equipo = %s
            ORDER BY hm.fecha_fin DESC
        """, (equipo_id,)) or []
        
        # Formatear fechas
        for h in historial:
            if h.get('fecha_inicio'):
                h['fecha_inicio'] = h['fecha_inicio'].strftime('%Y-%m-%d %H:%M')
            if h.get('fecha_fin'):
                h['fecha_fin'] = h['fecha_fin'].strftime('%Y-%m-%d %H:%M')
            if h.get('proxima_fecha_mantenimiento'):
                h['proxima_fecha_mantenimiento'] = h['proxima_fecha_mantenimiento'].strftime('%Y-%m-%d')
        
        # Estadísticas del equipo
        stats = db.obtener_uno("""
            SELECT 
                COUNT(*) as total_mantenimientos,
                SUM(costo_mantenimiento) as costo_total,
                SUM(tiempo_inactividad_horas) as tiempo_total,
                MAX(fecha_fin) as ultimo_mantenimiento,
                MIN(proxima_fecha_mantenimiento) as proximo_mantenimiento
            FROM historial_mantenimiento
            WHERE id_equipo = %s
        """, (equipo_id,))
        
        return jsonify({
            'success': True,
            'equipo': equipo,
            'historial': historial,
            'estadisticas': {
                'total_mantenimientos': stats['total_mantenimientos'] if stats else 0,
                'costo_total': float(stats['costo_total']) if stats and stats['costo_total'] else 0,
                'tiempo_inactividad_total': float(stats['tiempo_total']) if stats and stats['tiempo_total'] else 0,
                'ultimo_mantenimiento': stats['ultimo_mantenimiento'].strftime('%Y-%m-%d') if stats and stats['ultimo_mantenimiento'] else None,
                'proximo_mantenimiento': stats['proximo_mantenimiento'].strftime('%Y-%m-%d') if stats and stats['proximo_mantenimiento'] else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
