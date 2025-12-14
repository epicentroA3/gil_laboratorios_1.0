# API de Gestión de Usuarios
# Centro Minero SENA
# Adaptado a schema.sql - tabla usuarios

from flask import request, jsonify, session
from .blueprints import usuarios_bp
from ..utils.database import DatabaseManager
import hashlib

db = DatabaseManager()

# Mapeo de id_rol a nivel de acceso
NIVELES_ROL = {1: 6, 2: 4, 3: 3, 4: 1, 5: 2, 6: 1}  # admin=6, instructor=4, tecnico=3, aprendiz=1, monitor=2, visitante=1

# Mapeo de nivel_acceso a id_rol
ROL_POR_NIVEL = {6: 1, 5: 1, 4: 2, 3: 3, 2: 5, 1: 4}  # nivel 6,5->admin, 4->instructor, 3->tecnico, 2->monitor, 1->aprendiz

def require_auth_session(f):
    """Decorador simple para verificar sesión"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated

def hash_password(password):
    """Genera hash de contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()


@usuarios_bp.route('', methods=['GET'])
@require_auth_session
def listar_usuarios():
    """GET /api/usuarios - Listar todos los usuarios"""
    try:
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email, u.telefono,
                   u.id_rol, u.estado, u.password_hash,
                   DATE_FORMAT(u.fecha_registro, '%d/%m/%Y') as fecha_registro,
                   r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            ORDER BY u.nombres, u.apellidos
        """
        usuarios = db.ejecutar_query(query)
        
        # Transformar para compatibilidad con frontend
        usuarios_formateados = []
        for u in usuarios:
            nivel = NIVELES_ROL.get(u['id_rol'], 1)
            usuarios_formateados.append({
                'id': u['id'],
                'nombre': f"{u['nombres']} {u['apellidos']}",
                'tipo': u['nombre_rol'] or 'usuario',
                'programa': '',
                'nivel_acceso': nivel,
                'activo': u['estado'] == 'activo',
                'email': u['email'],
                'telefono': u['telefono'],
                'registro': u['fecha_registro'],
                'tiene_rostro': 'No'
            })
        
        return jsonify({'success': True, 'usuarios': usuarios_formateados}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error listando usuarios: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@require_auth_session
def obtener_usuario(usuario_id):
    """GET /api/usuarios/{id} - Obtener usuario específico"""
    try:
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email, u.telefono,
                   u.id_rol, u.estado,
                   DATE_FORMAT(u.fecha_registro, '%d/%m/%Y') as fecha_registro,
                   DATE_FORMAT(u.ultimo_acceso, '%d/%m/%Y %H:%i') as ultimo_acceso,
                   r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE u.id = %s
        """
        usuario = db.obtener_uno(query, (usuario_id,))
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        nivel = NIVELES_ROL.get(usuario['id_rol'], 1)
        usuario_formateado = {
            'id': usuario['id'],
            'documento': usuario['documento'],
            'nombres': usuario['nombres'],
            'apellidos': usuario['apellidos'],
            'nombre': f"{usuario['nombres']} {usuario['apellidos']}",
            'rol': usuario['nombre_rol'] or 'Usuario',
            'id_rol': usuario['id_rol'],
            'tipo': usuario['nombre_rol'] or 'usuario',
            'nivel_acceso': nivel,
            'activo': usuario['estado'] == 'activo',
            'estado': usuario['estado'],
            'email': usuario['email'],
            'telefono': usuario['telefono'],
            'fecha_registro': usuario['fecha_registro'],
            'ultimo_acceso': usuario['ultimo_acceso'] or 'Nunca',
            'tiene_rostro': 'No'
        }
        
        return jsonify({'success': True, 'usuario': usuario_formateado}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo usuario: {str(e)}'}), 500


@usuarios_bp.route('/create', methods=['POST'])
@require_auth_session
def crear_usuario():
    """POST /api/usuarios/create - Crear nuevo usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        documento = data.get('documento', '').strip()
        nombres = data.get('nombres', '').strip()
        apellidos = data.get('apellidos', '').strip()
        email = data.get('email', '').strip()
        telefono = data.get('telefono', '').strip()
        id_rol = data.get('id_rol')
        password = data.get('password', '')
        estado = data.get('estado', 'activo')
        
        if not documento:
            return jsonify({'success': False, 'message': 'El documento es requerido'}), 400
        if not nombres:
            return jsonify({'success': False, 'message': 'Los nombres son requeridos'}), 400
        if not apellidos:
            return jsonify({'success': False, 'message': 'Los apellidos son requeridos'}), 400
        if not password:
            return jsonify({'success': False, 'message': 'La contraseña es requerida'}), 400
        if not id_rol:
            return jsonify({'success': False, 'message': 'El rol es requerido'}), 400
        
        # Verificar que el documento no exista
        if db.existe('usuarios', 'documento = %s', (documento,)):
            return jsonify({'success': False, 'message': 'Ya existe un usuario con ese documento'}), 400
        
        # Verificar email único si se proporciona
        if email:
            if db.existe('usuarios', 'email = %s', (email,)):
                return jsonify({'success': False, 'message': 'Ya existe un usuario con ese email'}), 400
        
        # Hash de contraseña
        password_hash = hash_password(password)
        
        datos_usuario = {
            'documento': documento,
            'nombres': nombres,
            'apellidos': apellidos,
            'email': email if email else None,
            'telefono': telefono if telefono else None,
            'id_rol': int(id_rol),
            'password_hash': password_hash,
            'estado': estado
        }
        
        nuevo_id = db.insertar('usuarios', datos_usuario)
        
        if nuevo_id:
            return jsonify({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'usuario_id': nuevo_id
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Error al insertar usuario'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando usuario: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>/update', methods=['PUT'])
@require_auth_session
def actualizar_usuario(usuario_id):
    """PUT /api/usuarios/{id}/update - Actualizar usuario"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No hay datos para actualizar'}), 400
        
        if not db.existe('usuarios', 'id = %s', (usuario_id,)):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        datos_actualizar = {}
        
        # Campos editables
        if 'documento' in data and data['documento']:
            # Verificar que no exista otro usuario con ese documento
            query_check = "SELECT id FROM usuarios WHERE documento = %s AND id != %s"
            existe = db.obtener_uno(query_check, (data['documento'], usuario_id))
            if existe:
                return jsonify({'success': False, 'message': 'Ya existe otro usuario con ese documento'}), 400
            datos_actualizar['documento'] = data['documento'].strip()
        
        if 'nombres' in data and data['nombres']:
            datos_actualizar['nombres'] = data['nombres'].strip()
        
        if 'apellidos' in data and data['apellidos']:
            datos_actualizar['apellidos'] = data['apellidos'].strip()
        
        if 'email' in data:
            email = data['email'].strip() if data['email'] else None
            if email:
                # Verificar email único
                query_check = "SELECT id FROM usuarios WHERE email = %s AND id != %s"
                existe = db.obtener_uno(query_check, (email, usuario_id))
                if existe:
                    return jsonify({'success': False, 'message': 'Ya existe otro usuario con ese email'}), 400
            datos_actualizar['email'] = email
        
        if 'telefono' in data:
            datos_actualizar['telefono'] = data['telefono'].strip() if data['telefono'] else None
        
        if 'id_rol' in data and data['id_rol']:
            datos_actualizar['id_rol'] = int(data['id_rol'])
        
        if 'estado' in data and data['estado']:
            datos_actualizar['estado'] = data['estado']
        
        # Actualizar contraseña si se proporciona
        if 'password' in data and data['password']:
            datos_actualizar['password_hash'] = hash_password(data['password'])
        
        if datos_actualizar:
            db.actualizar('usuarios', datos_actualizar, 'id = %s', (usuario_id,))
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando usuario: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>/toggle', methods=['PUT'])
@require_auth_session
def toggle_usuario(usuario_id):
    """PUT /api/usuarios/{id}/toggle - Activar/Desactivar usuario"""
    try:
        data = request.get_json()
        
        if not db.existe('usuarios', 'id = %s', (usuario_id,)):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Determinar nuevo estado
        activo = data.get('activo', 1)
        nuevo_estado = 'activo' if activo == 1 else 'inactivo'
        
        db.actualizar('usuarios', {'estado': nuevo_estado}, 'id = %s', (usuario_id,))
        
        return jsonify({
            'success': True,
            'message': f'Usuario {"activado" if activo == 1 else "desactivado"} exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error cambiando estado: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>/delete', methods=['DELETE'])
@require_auth_session
def eliminar_usuario(usuario_id):
    """DELETE /api/usuarios/{id}/delete - Eliminar usuario permanentemente"""
    try:
        if not db.existe('usuarios', 'id = %s', (usuario_id,)):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Verificar que no sea el usuario actual
        if session.get('user_id') == usuario_id:
            return jsonify({'success': False, 'message': 'No puedes eliminarte a ti mismo'}), 400
        
        # Eliminar usuario
        db.eliminar('usuarios', 'id = %s', (usuario_id,))
        
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado permanentemente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error eliminando usuario: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>/desactivar', methods=['POST'])
@require_auth_session
def desactivar_usuario(usuario_id):
    """POST /api/usuarios/{id}/desactivar - Desactivar usuario (legacy)"""
    try:
        if not db.existe('usuarios', 'id = %s', (usuario_id,)):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        db.actualizar('usuarios', {'estado': 'inactivo'}, 'id = %s', (usuario_id,))
        
        return jsonify({
            'success': True,
            'message': 'Usuario desactivado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error desactivando usuario: {str(e)}'}), 500


@usuarios_bp.route('/<int:usuario_id>/activar', methods=['POST'])
@require_auth_session
def activar_usuario(usuario_id):
    """POST /api/usuarios/{id}/activar - Activar usuario (legacy)"""
    try:
        if not db.existe('usuarios', 'id = %s', (usuario_id,)):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        db.actualizar('usuarios', {'estado': 'activo'}, 'id = %s', (usuario_id,))
        
        return jsonify({
            'success': True,
            'message': 'Usuario activado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error activando usuario: {str(e)}'}), 500
