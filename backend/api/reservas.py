# API de Gestión de Reservas
# Centro Minero SENA

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import reservas_bp
from ..utils.database import DatabaseManager
from ..utils.helpers import generar_id
from datetime import datetime

db = DatabaseManager()

@reservas_bp.route('', methods=['GET'])
@jwt_required()
def listar_reservas():
    """GET /api/reservas - Listar todas las reservas"""
    try:
        query = """
            SELECT p.id_prestamo as id, p.id_usuario_solicitante as usuario_id, 
            p.id_equipo as equipo_id, p.estado_prestamo as estado, 
            p.observaciones_prestamo as observaciones,
            u.nombre as usuario_nombre,
            e.nombre_equipo as equipo_nombre,
            DATE_FORMAT(p.fecha_prestamo, '%Y-%m-%d %H:%i') as fecha_inicio,
            DATE_FORMAT(p.fecha_devolucion_programada, '%Y-%m-%d %H:%i') as fecha_fin
            FROM prestamos p
            JOIN usuarios u ON p.id_usuario_solicitante = u.id
            JOIN equipos e ON p.id_equipo = e.id_equipo
            ORDER BY p.fecha_prestamo DESC
        """
        reservas = db.ejecutar_query(query)
        
        return jsonify({'success': True, 'reservas': reservas}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error listando reservas: {str(e)}'}), 500

@reservas_bp.route('/activas', methods=['GET'])
@jwt_required()
def reservas_activas():
    """GET /api/reservas/activas - Reservas activas"""
    try:
        query = """
            SELECT p.id_prestamo as id, p.id_usuario_solicitante as usuario_id, p.id_equipo as equipo_id,
            u.nombre as usuario_nombre,
            e.nombre_equipo as equipo_nombre,
            DATE_FORMAT(p.fecha_prestamo, '%Y-%m-%d %H:%i') as fecha_inicio,
            DATE_FORMAT(p.fecha_devolucion_programada, '%Y-%m-%d %H:%i') as fecha_fin
            FROM prestamos p
            JOIN usuarios u ON p.id_usuario_solicitante = u.id
            JOIN equipos e ON p.id_equipo = e.id_equipo
            WHERE p.estado_prestamo = 'activo'
            ORDER BY p.fecha_prestamo
        """
        reservas = db.ejecutar_query(query)
        
        return jsonify({'success': True, 'reservas_activas': reservas}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo reservas activas: {str(e)}'}), 500

@reservas_bp.route('/usuario/<string:usuario_id>', methods=['GET'])
@jwt_required()
def reservas_usuario(usuario_id):
    """GET /api/reservas/usuario/{id} - Reservas de un usuario"""
    try:
        query = """
            SELECT p.id_prestamo as id, p.id_equipo as equipo_id, p.estado_prestamo as estado,
            e.nombre_equipo as equipo_nombre,
            DATE_FORMAT(p.fecha_prestamo, '%Y-%m-%d %H:%i') as fecha_inicio,
            DATE_FORMAT(p.fecha_devolucion_programada, '%Y-%m-%d %H:%i') as fecha_fin
            FROM prestamos p
            JOIN equipos e ON p.id_equipo = e.id_equipo
            WHERE p.id_usuario_solicitante = %s
            ORDER BY p.fecha_prestamo DESC
        """
        reservas = db.ejecutar_query(query, (usuario_id,))
        
        return jsonify({'success': True, 'reservas': reservas}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo reservas del usuario: {str(e)}'}), 500

@reservas_bp.route('', methods=['POST'])
@jwt_required()
def crear_reserva():
    """POST /api/reservas - Crear nueva reserva"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        if not data or 'equipo_id' not in data or 'fecha_inicio' not in data or 'fecha_fin' not in data:
            return jsonify({'error': 'Equipo, fecha inicio y fecha fin son requeridos'}), 400
        
        # Verificar que el equipo existe y está disponible
        equipo = db.obtener_uno('SELECT estado_equipo FROM equipos WHERE id_equipo = %s', (data['equipo_id'],))
        if not equipo:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        if equipo['estado_equipo'] != 'disponible':
            return jsonify({'error': 'Equipo no disponible'}), 400
        
        # Verificar conflictos de horario
        conflicto_query = """
            SELECT COUNT(*) as total FROM prestamos 
            WHERE id_equipo = %s 
            AND estado_prestamo IN ('aprobado', 'activo')
            AND (
                (fecha_prestamo <= %s AND fecha_devolucion_programada > %s) OR
                (fecha_prestamo < %s AND fecha_devolucion_programada >= %s) OR
                (fecha_prestamo >= %s AND fecha_devolucion_programada <= %s)
            )
        """
        conflicto = db.obtener_uno(conflicto_query, (
            data['equipo_id'],
            data['fecha_inicio'], data['fecha_inicio'],
            data['fecha_fin'], data['fecha_fin'],
            data['fecha_inicio'], data['fecha_fin']
        ))
        
        if conflicto and conflicto['total'] > 0:
            return jsonify({'error': 'Ya existe una reserva en ese horario'}), 400
        
        reserva_id = generar_id('RES', 8)
        
        datos_reserva = {
            'id': reserva_id,
            'usuario_id': data.get('usuario_id', current_user),
            'equipo_id': data['equipo_id'],
            'fecha_inicio': data['fecha_inicio'],
            'fecha_fin': data['fecha_fin'],
            'estado': 'programada',
            'observaciones': data.get('observaciones')
        }
        
        db.insertar('prestamos', datos_reserva)
        
        return jsonify({
            'success': True,
            'message': 'Reserva creada exitosamente',
            'reserva_id': reserva_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creando reserva: {str(e)}'}), 500

@reservas_bp.route('/<string:reserva_id>/cancelar', methods=['POST'])
@jwt_required()
def cancelar_reserva(reserva_id):
    """POST /api/reservas/{id}/cancelar - Cancelar reserva"""
    try:
        reserva = db.obtener_uno('SELECT estado_prestamo as estado FROM prestamos WHERE id_prestamo = %s', (reserva_id,))
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404
        
        if reserva['estado'] not in ['solicitado', 'aprobado', 'activo']:
            return jsonify({'error': 'La reserva no puede ser cancelada'}), 400
        
        db.actualizar('prestamos', {'estado_prestamo': 'cancelado'}, 'id_prestamo = %s', (reserva_id,))
        
        return jsonify({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error cancelando reserva: {str(e)}'}), 500

@reservas_bp.route('/<string:reserva_id>/completar', methods=['POST'])
@jwt_required()
def completar_reserva(reserva_id):
    """POST /api/reservas/{id}/completar - Completar reserva"""
    try:
        reserva = db.obtener_uno('SELECT estado_prestamo as estado FROM prestamos WHERE id_prestamo = %s', (reserva_id,))
        
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404
        
        if reserva['estado'] != 'activo':
            return jsonify({'error': 'Solo se pueden completar reservas activas'}), 400
        
        db.actualizar('prestamos', {'estado_prestamo': 'devuelto'}, 'id_prestamo = %s', (reserva_id,))
        
        return jsonify({
            'success': True,
            'message': 'Reserva completada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error completando reserva: {str(e)}'}), 500
