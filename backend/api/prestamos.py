# API de Gestión de Préstamos de Equipos
# Centro Minero SENA
# Sistema GIL - Plataforma Digital de Préstamos

from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.database import DatabaseManager
from backend.utils.validators import Validator

# Blueprint para préstamos
prestamos_bp = Blueprint('prestamos', __name__, url_prefix='/api/prestamos')

# Instancia de base de datos
db = DatabaseManager()

# =========================================================
# DECORADORES
# =========================================================

def require_auth_session(f):
    """Decorador para requerir autenticación por sesión"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated

def require_permission(permiso):
    """Decorador para requerir un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
            
            permisos = session.get('user_permisos', {})
            user_level = session.get('user_level', 1)
            if not permisos.get('all') and not permisos.get(permiso) and user_level < 3:
                return jsonify({'success': False, 'message': 'No tiene permisos para esta acción'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# =========================================================
# ENDPOINTS DE PRÉSTAMOS
# =========================================================

@prestamos_bp.route('', methods=['GET'])
@require_auth_session
def listar_prestamos():
    """GET /api/prestamos - Listar todos los préstamos con filtros"""
    try:
        estado = request.args.get('estado', '').strip()
        usuario = request.args.get('usuario', '').strip()
        equipo = request.args.get('equipo', '').strip()
        busqueda = request.args.get('busqueda', '').strip()
        solo_propios = request.args.get('solo_propios', '').strip().lower() == 'true'
        
        # Verificar permisos del usuario
        permisos = session.get('user_permisos', {})
        tiene_gestion = permisos.get('all') or permisos.get('prestamos')
        user_id = session.get('user_id')
        
        query = """
            SELECT p.id, p.codigo, p.id_equipo, p.id_usuario_solicitante,
                   p.id_usuario_autorizador, p.proposito, p.observaciones,
                   p.observaciones_devolucion, p.estado, p.calificacion_devolucion,
                   DATE_FORMAT(p.fecha_solicitud, '%d/%m/%Y %H:%i') as fecha_solicitud,
                   DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_prestamo,
                   DATE_FORMAT(p.fecha_devolucion_programada, '%d/%m/%Y %H:%i') as fecha_devolucion_programada,
                   DATE_FORMAT(p.fecha_devolucion_real, '%d/%m/%Y %H:%i') as fecha_devolucion_real,
                   e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo,
                   e.marca as equipo_marca, e.modelo as equipo_modelo,
                   CONCAT(us.nombres, ' ', us.apellidos) as solicitante_nombre,
                   us.documento as solicitante_documento,
                   CONCAT(ua.nombres, ' ', ua.apellidos) as autorizador_nombre
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id
            JOIN usuarios us ON p.id_usuario_solicitante = us.id
            LEFT JOIN usuarios ua ON p.id_usuario_autorizador = ua.id
            WHERE 1=1
        """
        params = []
        
        # Si solo tiene permiso prestamos_propios, filtrar por usuario actual
        if solo_propios or (not tiene_gestion and permisos.get('prestamos_propios')):
            query += " AND p.id_usuario_solicitante = %s"
            params.append(user_id)
        
        if estado:
            query += " AND p.estado = %s"
            params.append(estado)
        
        if usuario:
            query += " AND p.id_usuario_solicitante = %s"
            params.append(int(usuario))
        
        if equipo:
            query += " AND p.id_equipo = %s"
            params.append(int(equipo))
        
        if busqueda:
            query += """ AND (p.codigo LIKE %s OR e.nombre LIKE %s 
                        OR us.nombres LIKE %s OR us.apellidos LIKE %s)"""
            params.extend([f'%{busqueda}%'] * 4)
        
        query += " ORDER BY p.fecha_solicitud DESC"
        
        prestamos = db.ejecutar_query(query, tuple(params) if params else None) or []
        
        return jsonify({
            'success': True,
            'prestamos': prestamos,
            'total': len(prestamos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error listando préstamos: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>', methods=['GET'])
@require_auth_session
def obtener_prestamo(prestamo_id):
    """GET /api/prestamos/{id} - Obtener préstamo específico"""
    try:
        query = """
            SELECT p.id, p.codigo, p.id_equipo, p.id_usuario_solicitante,
                   p.id_usuario_autorizador, p.proposito, p.observaciones,
                   p.observaciones_devolucion, p.estado, p.calificacion_devolucion,
                   DATE_FORMAT(p.fecha_solicitud, '%Y-%m-%dT%H:%i') as fecha_solicitud,
                   DATE_FORMAT(p.fecha, '%Y-%m-%dT%H:%i') as fecha_prestamo,
                   DATE_FORMAT(p.fecha_devolucion_programada, '%Y-%m-%dT%H:%i') as fecha_devolucion_programada,
                   DATE_FORMAT(p.fecha_devolucion_real, '%Y-%m-%dT%H:%i') as fecha_devolucion_real,
                   e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo,
                   e.marca as equipo_marca, e.modelo as equipo_modelo,
                   CONCAT(us.nombres, ' ', us.apellidos) as solicitante_nombre,
                   us.documento as solicitante_documento,
                   CONCAT(ua.nombres, ' ', ua.apellidos) as autorizador_nombre
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id
            JOIN usuarios us ON p.id_usuario_solicitante = us.id
            LEFT JOIN usuarios ua ON p.id_usuario_autorizador = ua.id
            WHERE p.id = %s
        """
        prestamo = db.obtener_uno(query, (prestamo_id,))
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        return jsonify({'success': True, 'prestamo': prestamo}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo préstamo: {str(e)}'}), 500


@prestamos_bp.route('/mis-prestamos', methods=['GET'])
@require_auth_session
def mis_prestamos():
    """GET /api/prestamos/mis-prestamos - Préstamos del usuario actual"""
    try:
        user_id = session.get('user_id')
        
        query = """
            SELECT p.id, p.codigo, p.estado, p.proposito,
                   DATE_FORMAT(p.fecha_solicitud, '%d/%m/%Y %H:%i') as fecha_solicitud,
                   DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_prestamo,
                   DATE_FORMAT(p.fecha_devolucion_programada, '%d/%m/%Y %H:%i') as fecha_devolucion_programada,
                   e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id
            WHERE p.id_usuario_solicitante = %s
            ORDER BY p.fecha_solicitud DESC
        """
        prestamos = db.ejecutar_query(query, (user_id,)) or []
        
        return jsonify({
            'success': True,
            'prestamos': prestamos,
            'total': len(prestamos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo préstamos: {str(e)}'}), 500


@prestamos_bp.route('/activos', methods=['GET'])
@require_auth_session
def prestamos_activos():
    """GET /api/prestamos/activos - Préstamos activos"""
    try:
        query = """
            SELECT p.id, p.codigo, p.estado,
                   DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_prestamo,
                   DATE_FORMAT(p.fecha_devolucion_programada, '%d/%m/%Y %H:%i') as fecha_devolucion_programada,
                   e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo,
                   CONCAT(us.nombres, ' ', us.apellidos) as solicitante_nombre
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id
            JOIN usuarios us ON p.id_usuario_solicitante = us.id
            WHERE p.estado = 'activo'
            ORDER BY p.fecha_devolucion_programada ASC
        """
        prestamos = db.ejecutar_query(query) or []
        
        return jsonify({
            'success': True,
            'prestamos': prestamos,
            'total': len(prestamos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo préstamos activos: {str(e)}'}), 500


@prestamos_bp.route('/pendientes', methods=['GET'])
@require_auth_session
def prestamos_pendientes():
    """GET /api/prestamos/pendientes - Préstamos pendientes de aprobación"""
    try:
        query = """
            SELECT p.id, p.codigo, p.proposito,
                   DATE_FORMAT(p.fecha_solicitud, '%d/%m/%Y %H:%i') as fecha_solicitud,
                   DATE_FORMAT(p.fecha_devolucion_programada, '%d/%m/%Y %H:%i') as fecha_devolucion_programada,
                   e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo,
                   CONCAT(us.nombres, ' ', us.apellidos) as solicitante_nombre,
                   us.documento as solicitante_documento
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id
            JOIN usuarios us ON p.id_usuario_solicitante = us.id
            WHERE p.estado = 'solicitado'
            ORDER BY p.fecha_solicitud ASC
        """
        prestamos = db.ejecutar_query(query) or []
        
        return jsonify({
            'success': True,
            'prestamos': prestamos,
            'total': len(prestamos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo préstamos pendientes: {str(e)}'}), 500


@prestamos_bp.route('/validar', methods=['GET'])
@require_auth_session
def validar_prestamo():
    """GET /api/prestamos/validar - Validar campos del préstamo en tiempo real"""
    campo = request.args.get('campo', '').strip()
    valor = request.args.get('valor', '').strip()
    id_equipo = request.args.get('id_equipo', '').strip()
    
    errores = {}
    
    if campo == 'equipo' and valor:
        equipo = db.obtener_uno("SELECT id, estado, nombre FROM equipos WHERE id = %s", (valor,))
        if not equipo:
            errores['equipo'] = 'Equipo no encontrado'
        elif equipo['estado'] != 'disponible':
            errores['equipo'] = f'El equipo "{equipo["nombre"]}" no está disponible (estado: {equipo["estado"]})'
    
    elif campo == 'proposito':
        if not valor:
            errores['proposito'] = 'El propósito es requerido'
        elif len(valor) < 10:
            errores['proposito'] = f'El propósito debe tener al menos 10 caracteres (actual: {len(valor)})'
    
    elif campo == 'fecha_devolucion':
        if not valor:
            errores['fecha_devolucion'] = 'La fecha de devolución es requerida'
        else:
            try:
                from datetime import datetime
                fecha_dev = datetime.strptime(valor, '%Y-%m-%dT%H:%M')
                if fecha_dev <= datetime.now():
                    errores['fecha_devolucion'] = 'La fecha de devolución debe ser posterior a la fecha actual'
            except:
                pass
    
    return jsonify({
        'success': len(errores) == 0,
        'errores': errores,
        'valido': len(errores) == 0
    }), 200


@prestamos_bp.route('', methods=['POST'])
@require_auth_session
def crear_prestamo():
    """POST /api/prestamos - Crear nuevo préstamo (solicitud)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        errores = {}
        
        # Validar equipo
        id_equipo = data.get('id_equipo')
        if not id_equipo:
            errores['equipo'] = 'El equipo es requerido'
        else:
            equipo = db.obtener_uno("SELECT id, estado, nombre FROM equipos WHERE id = %s", (id_equipo,))
            if not equipo:
                errores['equipo'] = 'Equipo no encontrado'
            elif equipo['estado'] != 'disponible':
                errores['equipo'] = f'El equipo "{equipo["nombre"]}" no está disponible (estado: {equipo["estado"]})'
        
        # Validar fecha de devolución
        fecha_devolucion = data.get('fecha_devolucion_programada')
        if not fecha_devolucion:
            errores['fecha_devolucion'] = 'La fecha de devolución es requerida'
        
        # Validar propósito
        proposito = Validator.sanitizar_texto(data.get('proposito', ''))
        if not proposito:
            errores['proposito'] = 'El propósito es requerido'
        elif len(proposito) < 10:
            errores['proposito'] = 'El propósito debe tener al menos 10 caracteres'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Verificar conflictos de horario para el equipo
        fecha_inicio = data.get('fecha') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conflicto_query = """
            SELECT COUNT(*) as total FROM prestamos 
            WHERE id_equipo = %s 
            AND estado IN ('solicitado', 'aprobado', 'activo')
            AND (
                (fecha <= %s AND fecha_devolucion_programada > %s) OR
                (fecha < %s AND fecha_devolucion_programada >= %s) OR
                (fecha >= %s AND fecha_devolucion_programada <= %s)
            )
        """
        conflicto = db.obtener_uno(conflicto_query, (
            id_equipo,
            fecha_inicio, fecha_inicio,
            fecha_devolucion, fecha_devolucion,
            fecha_inicio, fecha_devolucion
        ))
        
        if conflicto and conflicto['total'] > 0:
            return jsonify({
                'success': False, 
                'message': 'Ya existe un préstamo para este equipo en el horario solicitado'
            }), 400
        
        # Generar código único
        codigo = f"PREST-{uuid.uuid4().hex[:8].upper()}"
        user_id = session.get('user_id')
        
        # Crear préstamo
        query = """
            INSERT INTO prestamos 
            (codigo, id_equipo, id_usuario_solicitante, fecha, fecha_devolucion_programada, 
             proposito, observaciones, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'solicitado')
        """
        db.ejecutar_comando(query, (
            codigo, id_equipo, user_id, fecha_inicio, fecha_devolucion,
            proposito, data.get('observaciones', '')
        ))
        
        # Obtener ID del préstamo creado
        result = db.obtener_uno("SELECT LAST_INSERT_ID() as id")
        nuevo_id = result['id'] if result else None
        
        return jsonify({
            'success': True,
            'message': 'Solicitud de préstamo creada exitosamente',
            'prestamo_id': nuevo_id,
            'codigo': codigo
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando préstamo: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>/aprobar', methods=['POST'])
@require_permission('prestamos')
def aprobar_prestamo(prestamo_id):
    """POST /api/prestamos/{id}/aprobar - Aprobar préstamo"""
    try:
        prestamo = db.obtener_uno(
            "SELECT estado, id_equipo FROM prestamos WHERE id = %s", 
            (prestamo_id,)
        )
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        if prestamo['estado'] != 'solicitado':
            return jsonify({
                'success': False, 
                'message': f'Solo se pueden aprobar préstamos en estado "solicitado". Estado actual: {prestamo["estado"]}'
            }), 400
        
        user_id = session.get('user_id')
        
        # Actualizar préstamo a aprobado
        db.actualizar('prestamos', {
            'estado': 'aprobado',
            'id_usuario_autorizador': user_id
        }, 'id = %s', (prestamo_id,))
        
        # Cambiar estado del equipo a 'prestado'
        db.actualizar('equipos', {'estado': 'prestado'}, 'id = %s', (prestamo['id_equipo'],))
        
        return jsonify({
            'success': True,
            'message': 'Préstamo aprobado. Equipo marcado como prestado.'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error aprobando préstamo: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>/rechazar', methods=['POST'])
@require_permission('prestamos')
def rechazar_prestamo(prestamo_id):
    """POST /api/prestamos/{id}/rechazar - Rechazar préstamo"""
    try:
        data = request.get_json() or {}
        motivo = data.get('motivo', '').strip()
        
        if not motivo:
            return jsonify({'success': False, 'message': 'El motivo del rechazo es requerido'}), 400
        
        prestamo = db.obtener_uno(
            "SELECT estado FROM prestamos WHERE id = %s", 
            (prestamo_id,)
        )
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        if prestamo['estado'] != 'solicitado':
            return jsonify({
                'success': False, 
                'message': f'Solo se pueden rechazar préstamos en estado "solicitado". Estado actual: {prestamo["estado"]}'
            }), 400
        
        user_id = session.get('user_id')
        
        # Actualizar préstamo a rechazado
        db.actualizar('prestamos', {
            'estado': 'rechazado',
            'id_usuario_autorizador': user_id,
            'observaciones': motivo
        }, 'id = %s', (prestamo_id,))
        
        return jsonify({
            'success': True,
            'message': 'Préstamo rechazado'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error rechazando préstamo: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>/activar', methods=['POST'])
@require_permission('prestamos')
def activar_prestamo(prestamo_id):
    """POST /api/prestamos/{id}/activar - Activar préstamo (entregar equipo)"""
    try:
        prestamo = db.obtener_uno(
            "SELECT estado, id_equipo FROM prestamos WHERE id = %s", 
            (prestamo_id,)
        )
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        if prestamo['estado'] != 'aprobado':
            return jsonify({
                'success': False, 
                'message': f'Solo se pueden activar préstamos aprobados. Estado actual: {prestamo["estado"]}'
            }), 400
        
        # Actualizar préstamo a activo
        db.actualizar('prestamos', {
            'estado': 'activo',
            'fecha': datetime.now()
        }, 'id = %s', (prestamo_id,))
        
        # Cambiar estado del equipo a 'prestado'
        db.actualizar('equipos', {'estado': 'prestado'}, 'id = %s', (prestamo['id_equipo'],))
        
        return jsonify({
            'success': True,
            'message': 'Préstamo activado. Equipo entregado.'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error activando préstamo: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>/devolver', methods=['POST'])
@require_auth_session
def devolver_prestamo(prestamo_id):
    """POST /api/prestamos/{id}/devolver - Registrar devolución de equipo"""
    try:
        data = request.get_json() or {}
        
        prestamo = db.obtener_uno(
            "SELECT estado, id_equipo FROM prestamos WHERE id = %s", 
            (prestamo_id,)
        )
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        if prestamo['estado'] != 'activo':
            return jsonify({
                'success': False, 
                'message': f'Solo se pueden devolver préstamos activos. Estado actual: {prestamo["estado"]}'
            }), 400
        
        # Validar calificación si se proporciona
        calificacion = data.get('calificacion')
        calificaciones_validas = ['excelente', 'bueno', 'regular', 'malo']
        if calificacion and calificacion not in calificaciones_validas:
            calificacion = None
        
        # Actualizar préstamo a devuelto
        db.actualizar('prestamos', {
            'estado': 'devuelto',
            'fecha_devolucion_real': datetime.now(),
            'observaciones_devolucion': data.get('observaciones', ''),
            'calificacion_devolucion': calificacion
        }, 'id = %s', (prestamo_id,))
        
        # Cambiar estado del equipo a 'disponible'
        db.actualizar('equipos', {'estado': 'disponible'}, 'id = %s', (prestamo['id_equipo'],))
        
        return jsonify({
            'success': True,
            'message': 'Devolución registrada exitosamente. Equipo disponible.'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error registrando devolución: {str(e)}'}), 500


@prestamos_bp.route('/<int:prestamo_id>/cancelar', methods=['POST'])
@require_auth_session
def cancelar_prestamo(prestamo_id):
    """POST /api/prestamos/{id}/cancelar - Cancelar préstamo"""
    try:
        user_id = session.get('user_id')
        user_level = session.get('user_level', 1)
        
        prestamo = db.obtener_uno(
            "SELECT estado, id_usuario_solicitante, id_equipo FROM prestamos WHERE id = %s", 
            (prestamo_id,)
        )
        
        if not prestamo:
            return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
        
        # Solo el solicitante o un administrador pueden cancelar
        if prestamo['id_usuario_solicitante'] != user_id and user_level < 3:
            return jsonify({
                'success': False, 
                'message': 'No tiene permisos para cancelar este préstamo'
            }), 403
        
        if prestamo['estado'] not in ['solicitado', 'aprobado']:
            return jsonify({
                'success': False, 
                'message': f'No se puede cancelar un préstamo en estado "{prestamo["estado"]}"'
            }), 400
        
        # Si estaba aprobado, liberar el equipo (volver a disponible)
        if prestamo['estado'] == 'aprobado':
            db.actualizar('equipos', {'estado': 'disponible'}, 'id = %s', (prestamo['id_equipo'],))
        
        # Actualizar préstamo a rechazado (cancelado)
        db.actualizar('prestamos', {
            'estado': 'rechazado',
            'observaciones': 'Cancelado por el usuario'
        }, 'id = %s', (prestamo_id,))
        
        return jsonify({
            'success': True,
            'message': 'Préstamo cancelado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error cancelando préstamo: {str(e)}'}), 500


@prestamos_bp.route('/estadisticas', methods=['GET'])
@require_auth_session
def estadisticas_prestamos():
    """GET /api/prestamos/estadisticas - Estadísticas de préstamos"""
    try:
        stats = {}
        solo_propios = request.args.get('solo_propios', '').strip().lower() == 'true'
        
        # Verificar permisos del usuario
        permisos = session.get('user_permisos', {})
        tiene_gestion = permisos.get('all') or permisos.get('prestamos')
        user_id = session.get('user_id')
        
        # Filtrar por usuario si solo tiene prestamos_propios
        filtro_usuario = ""
        params = []
        if solo_propios or (not tiene_gestion and permisos.get('prestamos_propios')):
            filtro_usuario = " WHERE id_usuario_solicitante = %s"
            params = [user_id]
        
        # Total por estado
        query_estados = f"""
            SELECT estado, COUNT(*) as total
            FROM prestamos
            {filtro_usuario}
            GROUP BY estado
        """
        estados = db.ejecutar_query(query_estados, tuple(params) if params else None) or []
        stats['por_estado'] = {e['estado']: e['total'] for e in estados}
        
        # Total general
        query_total = f"SELECT COUNT(*) as total FROM prestamos{filtro_usuario}"
        total = db.obtener_uno(query_total, tuple(params) if params else None)
        stats['total'] = total['total'] if total else 0
        
        # Préstamos del mes actual
        if filtro_usuario:
            query_mes = f"""
                SELECT COUNT(*) as total FROM prestamos 
                WHERE id_usuario_solicitante = %s
                AND MONTH(fecha_solicitud) = MONTH(CURRENT_DATE())
                AND YEAR(fecha_solicitud) = YEAR(CURRENT_DATE())
            """
            mes = db.obtener_uno(query_mes, (user_id,))
        else:
            query_mes = """
                SELECT COUNT(*) as total FROM prestamos 
                WHERE MONTH(fecha_solicitud) = MONTH(CURRENT_DATE())
                AND YEAR(fecha_solicitud) = YEAR(CURRENT_DATE())
            """
            mes = db.obtener_uno(query_mes)
        stats['mes_actual'] = mes['total'] if mes else 0
        
        # Equipos más solicitados (solo para gestión completa)
        if tiene_gestion:
            query_equipos = """
                SELECT e.nombre, COUNT(*) as total
                FROM prestamos p
                JOIN equipos e ON p.id_equipo = e.id
                GROUP BY p.id_equipo, e.nombre
                ORDER BY total DESC
                LIMIT 5
            """
            equipos = db.ejecutar_query(query_equipos) or []
            stats['equipos_mas_solicitados'] = equipos
        
        # Tiempo promedio de préstamo (en días)
        if filtro_usuario:
            query_promedio = """
                SELECT AVG(DATEDIFF(fecha_devolucion_real, fecha)) as promedio
                FROM prestamos
                WHERE id_usuario_solicitante = %s AND estado = 'devuelto' AND fecha_devolucion_real IS NOT NULL
            """
            promedio = db.obtener_uno(query_promedio, (user_id,))
        else:
            query_promedio = """
                SELECT AVG(DATEDIFF(fecha_devolucion_real, fecha)) as promedio
                FROM prestamos
                WHERE estado = 'devuelto' AND fecha_devolucion_real IS NOT NULL
            """
            promedio = db.obtener_uno(query_promedio)
        stats['promedio_dias'] = round(float(promedio['promedio'] or 0), 1) if promedio and promedio['promedio'] else 0
        
        return jsonify({
            'success': True,
            'estadisticas': stats
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo estadísticas: {str(e)}'}), 500
