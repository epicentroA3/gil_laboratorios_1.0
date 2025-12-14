# API REST para Gestión de Roles
# Centro Minero SENA
# CRUD completo para roles y permisos

from flask import Blueprint, request, jsonify, session
from functools import wraps
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.database import DatabaseManager

# Blueprint para roles
roles_bp = Blueprint('roles', __name__, url_prefix='/api/roles')

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
            if not permisos.get('all') and not permisos.get(permiso):
                return jsonify({'success': False, 'message': 'No tiene permisos para esta acción'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# =========================================================
# ENDPOINTS DE ROLES
# =========================================================

@roles_bp.route('', methods=['GET'])
@require_auth_session
def listar_roles():
    """Obtener lista de todos los roles"""
    try:
        query = """
            SELECT id, nombre_rol, descripcion, permisos, estado,
                   DATE_FORMAT(fecha_creacion, '%d/%m/%Y') as fecha_creacion
            FROM roles
            ORDER BY id
        """
        roles = db.ejecutar_query(query) or []
        
        # Parsear permisos JSON
        for rol in roles:
            try:
                rol['permisos_obj'] = json.loads(rol.get('permisos', '{}') or '{}')
            except:
                rol['permisos_obj'] = {}
        
        return jsonify({'success': True, 'roles': roles}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo roles: {str(e)}'}), 500

@roles_bp.route('/validar', methods=['GET'])
@require_auth_session
def validar_nombre_rol():
    """GET /api/roles/validar?nombre=XXX&excluir_id=YYY - Verificar si nombre existe"""
    try:
        nombre = request.args.get('nombre', '').strip()
        excluir_id = request.args.get('excluir_id', '')
        
        if not nombre:
            return jsonify({'success': True, 'existe': False}), 200
        
        if excluir_id:
            query = "SELECT id FROM roles WHERE nombre_rol = %s AND id != %s"
            resultado = db.obtener_uno(query, (nombre, int(excluir_id)))
        else:
            query = "SELECT id FROM roles WHERE nombre_rol = %s"
            resultado = db.obtener_uno(query, (nombre,))
        
        return jsonify({'success': True, 'existe': resultado is not None}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@roles_bp.route('/<int:rol_id>', methods=['GET'])
@require_auth_session
def obtener_rol(rol_id):
    """Obtener un rol específico por ID"""
    try:
        query = """
            SELECT id, nombre_rol, descripcion, permisos, estado,
                   DATE_FORMAT(fecha_creacion, '%d/%m/%Y') as fecha_creacion
            FROM roles
            WHERE id = %s
        """
        rol = db.obtener_uno(query, (rol_id,))
        
        if not rol:
            return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
        
        # Parsear permisos JSON
        try:
            rol['permisos_obj'] = json.loads(rol.get('permisos', '{}') or '{}')
        except:
            rol['permisos_obj'] = {}
        
        return jsonify({'success': True, 'rol': rol}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo rol: {str(e)}'}), 500

@roles_bp.route('', methods=['POST'])
@require_permission('roles')
def crear_rol():
    """Crear un nuevo rol"""
    try:
        data = request.get_json()
        
        nombre_rol = data.get('nombre_rol', '').strip()
        descripcion = data.get('descripcion', '').strip()
        permisos = data.get('permisos', {})
        estado = data.get('estado', 'activo')
        
        if not nombre_rol:
            return jsonify({'success': False, 'message': 'El nombre del rol es requerido'}), 400
        
        # Verificar que no exista un rol con el mismo nombre
        query_check = "SELECT id FROM roles WHERE nombre_rol = %s"
        existe = db.obtener_uno(query_check, (nombre_rol,))
        if existe:
            return jsonify({'success': False, 'message': 'Ya existe un rol con ese nombre'}), 400
        
        # Convertir permisos a JSON string
        permisos_json = json.dumps(permisos) if isinstance(permisos, dict) else permisos
        
        query = """
            INSERT INTO roles (nombre_rol, descripcion, permisos, estado)
            VALUES (%s, %s, %s, %s)
        """
        db.ejecutar_comando(query, (nombre_rol, descripcion, permisos_json, estado))
        
        # Obtener el ID del rol creado
        query_id = "SELECT LAST_INSERT_ID() as id"
        result = db.obtener_uno(query_id)
        nuevo_id = result['id'] if result else None
        
        return jsonify({
            'success': True, 
            'message': 'Rol creado exitosamente',
            'rol_id': nuevo_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando rol: {str(e)}'}), 500

@roles_bp.route('/<int:rol_id>', methods=['PUT'])
@require_permission('roles')
def actualizar_rol(rol_id):
    """Actualizar un rol existente"""
    try:
        # Proteger roles del sistema (1-5)
        if rol_id <= 5:
            # Solo permitir actualizar permisos, no nombre ni descripción base
            pass
        
        data = request.get_json()
        
        nombre_rol = data.get('nombre_rol', '').strip()
        descripcion = data.get('descripcion', '').strip()
        permisos = data.get('permisos', {})
        estado = data.get('estado')
        
        # Verificar que el rol existe
        query_check = "SELECT id FROM roles WHERE id = %s"
        existe = db.obtener_uno(query_check, (rol_id,))
        if not existe:
            return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
        
        # Verificar nombre duplicado (si se está cambiando)
        if nombre_rol:
            query_dup = "SELECT id FROM roles WHERE nombre_rol = %s AND id != %s"
            duplicado = db.obtener_uno(query_dup, (nombre_rol, rol_id))
            if duplicado:
                return jsonify({'success': False, 'message': 'Ya existe otro rol con ese nombre'}), 400
        
        # Construir query de actualización
        updates = []
        params = []
        
        if nombre_rol:
            updates.append("nombre_rol = %s")
            params.append(nombre_rol)
        
        if descripcion is not None:
            updates.append("descripcion = %s")
            params.append(descripcion)
        
        if permisos:
            permisos_json = json.dumps(permisos) if isinstance(permisos, dict) else permisos
            updates.append("permisos = %s")
            params.append(permisos_json)
        
        if estado:
            updates.append("estado = %s")
            params.append(estado)
        
        if not updates:
            return jsonify({'success': False, 'message': 'No hay datos para actualizar'}), 400
        
        params.append(rol_id)
        query = f"UPDATE roles SET {', '.join(updates)} WHERE id = %s"
        db.ejecutar_comando(query, tuple(params))
        
        return jsonify({'success': True, 'message': 'Rol actualizado exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando rol: {str(e)}'}), 500

@roles_bp.route('/<int:rol_id>/permisos', methods=['GET'])
@require_auth_session
def obtener_permisos_rol(rol_id):
    """Obtener permisos de un rol específico"""
    try:
        query = "SELECT permisos FROM roles WHERE id = %s"
        rol = db.obtener_uno(query, (rol_id,))
        
        if not rol:
            return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
        
        try:
            permisos = json.loads(rol.get('permisos', '{}') or '{}')
        except:
            permisos = {}
        
        return jsonify({'success': True, 'permisos': permisos}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo permisos: {str(e)}'}), 500

@roles_bp.route('/<int:rol_id>/permisos', methods=['PUT'])
@require_permission('roles')
def actualizar_permisos_rol(rol_id):
    """Actualizar permisos de un rol"""
    try:
        data = request.get_json()
        permisos = data.get('permisos', {})
        
        if not isinstance(permisos, dict):
            return jsonify({'success': False, 'message': 'Formato de permisos inválido'}), 400
        
        # Verificar que el rol existe
        query_check = "SELECT id FROM roles WHERE id = %s"
        existe = db.obtener_uno(query_check, (rol_id,))
        if not existe:
            return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
        
        permisos_json = json.dumps(permisos)
        
        query = "UPDATE roles SET permisos = %s WHERE id = %s"
        db.ejecutar_comando(query, (permisos_json, rol_id))
        
        return jsonify({'success': True, 'message': 'Permisos actualizados exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando permisos: {str(e)}'}), 500

@roles_bp.route('/permisos-disponibles', methods=['GET'])
@require_auth_session
def listar_permisos_disponibles():
    """Obtener lista de todos los permisos disponibles en el sistema"""
    permisos_disponibles = [
        {'key': 'all', 'nombre': 'Acceso Total', 'descripcion': 'Acceso completo a todo el sistema', 'categoria': 'Sistema'},
        {'key': 'usuarios', 'nombre': 'Gestión Usuarios', 'descripcion': 'Crear, editar y gestionar usuarios', 'categoria': 'Administración'},
        {'key': 'roles', 'nombre': 'Gestión Roles', 'descripcion': 'Crear, editar y gestionar roles', 'categoria': 'Administración'},
        {'key': 'programas', 'nombre': 'Gestión Programas', 'descripcion': 'Gestionar programas de formación', 'categoria': 'Administración'},
        {'key': 'equipos', 'nombre': 'Gestión Equipos', 'descripcion': 'Crear, editar y gestionar equipos', 'categoria': 'Inventario'},
        {'key': 'equipos_ver', 'nombre': 'Ver Equipos', 'descripcion': 'Solo visualizar equipos', 'categoria': 'Inventario'},
        {'key': 'laboratorios', 'nombre': 'Gestión Laboratorios', 'descripcion': 'Gestionar laboratorios', 'categoria': 'Inventario'},
        {'key': 'laboratorios_ver', 'nombre': 'Ver Laboratorios', 'descripcion': 'Solo visualizar laboratorios', 'categoria': 'Inventario'},
        {'key': 'practicas', 'nombre': 'Gestión Prácticas', 'descripcion': 'Gestionar prácticas de laboratorio', 'categoria': 'Académico'},
        {'key': 'reservas', 'nombre': 'Gestión Reservas', 'descripcion': 'Gestionar todas las reservas', 'categoria': 'Operaciones'},
        {'key': 'reservas_ver', 'nombre': 'Ver Reservas', 'descripcion': 'Solo visualizar reservas', 'categoria': 'Operaciones'},
        {'key': 'reservas_propias', 'nombre': 'Reservas Propias', 'descripcion': 'Solo gestionar reservas propias', 'categoria': 'Operaciones'},
        {'key': 'prestamos', 'nombre': 'Gestión Préstamos', 'descripcion': 'Aprobar, rechazar y gestionar todos los préstamos', 'categoria': 'Operaciones'},
        {'key': 'prestamos_propios', 'nombre': 'Préstamos Propios', 'descripcion': 'Solicitar préstamos y ver los propios', 'categoria': 'Operaciones'},
        {'key': 'reportes', 'nombre': 'Reportes', 'descripcion': 'Acceso a reportes del sistema', 'categoria': 'Análisis'},
        {'key': 'mantenimiento', 'nombre': 'Gestión Mantenimiento', 'descripcion': 'Gestionar mantenimientos', 'categoria': 'Operaciones'},
        {'key': 'mantenimiento_ver', 'nombre': 'Ver Mantenimiento', 'descripcion': 'Solo visualizar mantenimientos', 'categoria': 'Operaciones'},
        {'key': 'capacitaciones', 'nombre': 'Gestión Capacitaciones', 'descripcion': 'Gestionar capacitaciones', 'categoria': 'Académico'},
        {'key': 'capacitaciones_ver', 'nombre': 'Ver Capacitaciones', 'descripcion': 'Solo visualizar capacitaciones', 'categoria': 'Académico'},
        {'key': 'reconocimiento', 'nombre': 'Reconocimiento Equipos', 'descripcion': 'Usar reconocimiento de equipos', 'categoria': 'IA'},
        {'key': 'ia_visual', 'nombre': 'IA Visual', 'descripcion': 'Entrenar y gestionar modelos IA', 'categoria': 'IA'},
        {'key': 'backups', 'nombre': 'Backups', 'descripcion': 'Gestionar respaldos del sistema', 'categoria': 'Sistema'},
        {'key': 'configuracion', 'nombre': 'Configuración', 'descripcion': 'Configuración del sistema', 'categoria': 'Sistema'},
        {'key': 'ayuda', 'nombre': 'Ayuda', 'descripcion': 'Acceso a la ayuda del sistema', 'categoria': 'General'},
    ]
    
    return jsonify({'success': True, 'permisos': permisos_disponibles}), 200
