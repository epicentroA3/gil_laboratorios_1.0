# API de Autenticación - Adaptada a schema.sql
# Centro Minero SENA

from flask import request, jsonify, Blueprint
from functools import wraps
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.config import Config
from config.api_config import JWTManager
from backend.utils.database import DatabaseManager

# Crear blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Inicializar gestor de base de datos
db = DatabaseManager()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/v1/auth/login
    Autenticación de usuario con contraseña - Adaptado a schema.sql
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
        
        user_id = data['user_id']
        password = data.get('password', '')
        
        if not password:
            return jsonify({'success': False, 'message': 'Contraseña requerida'}), 400
        
        # Query adaptada a schema.sql (tabla usuarios con JOIN a roles)
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email,
                   u.id_rol, u.estado, u.password_hash, r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE (u.id = %s OR u.documento = %s) AND u.estado = 'activo'
        """
        usuario = db.obtener_uno(query, (user_id, user_id))
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado o inactivo'}), 401
        
        # Validar contraseña con bcrypt
        password_hash = usuario.get('password_hash', '')
        if not password_hash:
            return jsonify({'success': False, 'message': 'Usuario sin contraseña configurada'}), 401
        
        try:
            import bcrypt
            password_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Error verificando contraseña: {e}")
            password_valid = False
        
        if not password_valid:
            # Registrar intento fallido
            try:
                log_query = """
                    INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                    VALUES ('auth_api', 'WARNING', 'Intento de login API fallido - contraseña incorrecta', %s, %s)
                """
                db.ejecutar_comando(log_query, (usuario['id'], request.remote_addr))
            except:
                pass
            return jsonify({'success': False, 'message': 'Contraseña incorrecta'}), 401
        
        # Calcular nivel de acceso según rol
        niveles_rol = {1: 5, 2: 4, 3: 3, 4: 2, 5: 2, 6: 1}
        nivel = niveles_rol.get(usuario['id_rol'], 1)
        nombre_completo = f"{usuario['nombres']} {usuario['apellidos']}"
        
        # Crear token JWT
        token = JWTManager.generate_token(
            user_id=usuario['id'],
            user_role=nivel,
            extra_claims={
                'documento': usuario['documento'],
                'nombre': nombre_completo,
                'rol': usuario['nombre_rol']
            }
        )
        
        # Registrar login en logs_sistema (según schema.sql)
        try:
            log_query = """
                INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                VALUES ('auth', 'INFO', 'Login exitoso desde API', %s, %s)
            """
            db.ejecutar_comando(log_query, (usuario['id'], request.remote_addr))
        except:
            pass  # No fallar si el log falla
        
        # Actualizar último acceso
        try:
            db.ejecutar_comando(
                "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s",
                (usuario['id'],)
            )
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'access_token': token,
            'user': {
                'id': usuario['id'],
                'documento': usuario['documento'],
                'nombre': nombre_completo,
                'email': usuario['email'],
                'rol': usuario['nombre_rol'],
                'nivel_acceso': nivel
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en autenticación: {str(e)}'}), 500


@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """
    GET /api/v1/auth/verify
    Verifica si el token es válido
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token requerido'}), 401
        
        payload, error = JWTManager.decode_token(token)
        
        if error:
            return jsonify({'success': False, 'message': error}), 401
        
        user_id = payload.get('user_id')
        
        # Obtener información actualizada del usuario
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email,
                   u.id_rol, u.estado, r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE u.id = %s AND u.estado = 'activo'
        """
        usuario = db.obtener_uno(query, (user_id,))
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        niveles_rol = {1: 5, 2: 4, 3: 3, 4: 2, 5: 2, 6: 1}
        nivel = niveles_rol.get(usuario['id_rol'], 1)
        
        return jsonify({
            'success': True,
            'user': {
                'id': usuario['id'],
                'documento': usuario['documento'],
                'nombre': f"{usuario['nombres']} {usuario['apellidos']}",
                'email': usuario['email'],
                'rol': usuario['nombre_rol'],
                'nivel_acceso': nivel
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error verificando token: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    POST /api/v1/auth/logout
    Cierra sesión del usuario
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            payload, _ = JWTManager.decode_token(token)
            if payload:
                user_id = payload.get('user_id')
                # Registrar logout en logs_sistema
                try:
                    log_query = """
                        INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                        VALUES ('auth', 'INFO', 'Logout desde API', %s, %s)
                    """
                    db.ejecutar_comando(log_query, (user_id, request.remote_addr))
                except:
                    pass
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en logout: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    GET /api/v1/auth/me
    Obtiene información del usuario actual
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token requerido'}), 401
        
        payload, error = JWTManager.decode_token(token)
        
        if error:
            return jsonify({'success': False, 'message': error}), 401
        
        return jsonify({
            'success': True,
            'user': payload
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
