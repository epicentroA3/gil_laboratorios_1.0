# API de Comandos de Voz
# Centro Minero SENA

from flask import request, jsonify, session
from .blueprints import comandos_voz_bp
from ..utils.database import DatabaseManager

db = DatabaseManager()

@comandos_voz_bp.route('/procesar', methods=['POST'])
def procesar_comando():
    """POST /api/voz/procesar - Procesar comando de voz"""
    try:
        # Verificar sesión activa
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        data = request.get_json()
        current_user = session.get('user_id')
        
        if not data or 'comando' not in data:
            return jsonify({'error': 'Comando es requerido'}), 400
        
        comando = data['comando'].lower()
        respuesta = {'success': True, 'comando': comando}
        
        # Procesar diferentes tipos de comandos
        if 'estado' in comando and 'equipo' in comando:
            # Consultar estado de equipos
            query = "SELECT id, nombre, estado FROM equipos WHERE estado = 'disponible' LIMIT 5"
            equipos = db.ejecutar_query(query)
            respuesta['tipo'] = 'estado_equipos'
            respuesta['datos'] = equipos
            respuesta['mensaje'] = f'Hay {len(equipos)} equipos disponibles'
            
        elif 'inventario' in comando or 'stock' in comando:
            # Consultar inventario crítico
            query = """
                SELECT nombre, cantidad_actual, cantidad_minima 
                FROM inventario 
                WHERE cantidad_actual <= cantidad_minima
                LIMIT 5
            """
            items = db.ejecutar_query(query)
            respuesta['tipo'] = 'inventario_critico'
            respuesta['datos'] = items
            respuesta['mensaje'] = f'Hay {len(items)} items con stock crítico'
            
        elif 'reserva' in comando or 'prestamo' in comando:
            # Consultar préstamos/reservas activas
            query = """
                SELECT p.id_prestamo as id, e.nombre_equipo as equipo, u.nombre as usuario
                FROM prestamos p
                JOIN equipos e ON p.id_equipo = e.id_equipo
                JOIN usuarios u ON p.id_usuario_solicitante = u.id
                WHERE p.estado_prestamo = 'activo'
                LIMIT 5
            """
            reservas = db.ejecutar_query(query)
            respuesta['tipo'] = 'reservas_activas'
            respuesta['datos'] = reservas
            respuesta['mensaje'] = f'Hay {len(reservas)} préstamos activos'
            
        else:
            respuesta['tipo'] = 'desconocido'
            respuesta['mensaje'] = 'Comando no reconocido'
        
        # Registrar comando en logs
        log_query = """
            INSERT INTO logs_comandos_voz (usuario_id, comando, respuesta, exitoso)
            VALUES (%s, %s, %s, TRUE)
        """
        db.ejecutar_comando(log_query, (current_user, comando, respuesta['mensaje']))
        
        return jsonify(respuesta), 200
        
    except Exception as e:
        return jsonify({'error': f'Error procesando comando: {str(e)}'}), 500

@comandos_voz_bp.route('/historial', methods=['GET'])
def historial_comandos():
    """GET /api/voz/historial - Historial de comandos de voz"""
    try:
        # Verificar sesión activa
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        current_user = session.get('user_id')
        
        query = """
            SELECT comando, respuesta, exitoso,
            DATE_FORMAT(fecha_hora, '%Y-%m-%d %H:%i:%s') as fecha_hora
            FROM logs_comandos_voz
            WHERE usuario_id = %s
            ORDER BY fecha_hora DESC
            LIMIT 20
        """
        historial = db.ejecutar_query(query, (current_user,))
        
        return jsonify({'success': True, 'historial': historial}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo historial: {str(e)}'}), 500
