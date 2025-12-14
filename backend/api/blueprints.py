# API REST Blueprints
# Centro Minero SENA
# Integrado con configuración centralizada y schema.sql

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sys
import os

# Agregar paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import Config
    from config.api_config import APIConfig, JWTManager, token_required
except ImportError:
    Config = None
    APIConfig = None

from backend.utils.database import DatabaseManager

# Crear blueprint principal de la API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Blueprint para equipos (usado por backend/api/equipos.py)
equipos_bp = Blueprint('equipos', __name__, url_prefix='/api/equipos')

# Blueprint para reconocimiento IA (usado por backend/api/reconocimiento_ia.py)
reconocimiento_bp = Blueprint('reconocimiento', __name__, url_prefix='/api/reconocimiento')

# Blueprint para usuarios (usado por backend/api/usuarios.py)
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

# Instancia de base de datos
db = DatabaseManager()


# =========================================================
# DECORADORES
# =========================================================

def require_auth(f):
    """Decorador para requerir autenticación (sesión o JWT)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verificar sesión
        if 'user_id' in session:
            return f(*args, **kwargs)
        
        # Verificar JWT
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token and JWTManager:
            payload, error = JWTManager.decode_token(token)
            if payload:
                request.user_id = payload.get('user_id')
                request.user_role = payload.get('user_role')
                return f(*args, **kwargs)
        
        return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
    return decorated


def require_level(min_level):
    """Decorador para requerir nivel mínimo"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            level = session.get('user_level', 0)
            if hasattr(request, 'user_role'):
                level = request.user_role
            
            if level < min_level:
                return jsonify({'success': False, 'message': 'Permisos insuficientes'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# =========================================================
# ENDPOINTS DE AUTENTICACIÓN
# =========================================================

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """Login por API - retorna JWT"""
    data = request.get_json() or {}
    user_id = data.get('user_id') or data.get('documento')
    password = data.get('password')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'ID de usuario requerido'}), 400
    
    try:
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email,
                   u.id_rol, u.estado, u.password_hash, r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE (u.id = %s OR u.documento = %s) AND u.estado = 'activo'
        """
        usuario = db.obtener_uno(query, (user_id, user_id))
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # Calcular nivel de acceso
        niveles_rol = {1: 5, 2: 4, 3: 3, 4: 2, 5: 2, 6: 1}
        nivel = niveles_rol.get(usuario['id_rol'], 1)
        
        # Generar token JWT
        if JWTManager:
            token = JWTManager.generate_token(
                user_id=usuario['id'],
                user_role=nivel,
                extra_claims={
                    'documento': usuario['documento'],
                    'nombre': f"{usuario['nombres']} {usuario['apellidos']}",
                    'rol': usuario['nombre_rol']
                }
            )
        else:
            token = None
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'data': {
                'user_id': usuario['id'],
                'nombre': f"{usuario['nombres']} {usuario['apellidos']}",
                'rol': usuario['nombre_rol'],
                'nivel': nivel,
                'token': token
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/auth/me', methods=['GET'])
@require_auth
def api_me():
    """Obtiene información del usuario actual"""
    user_id = session.get('user_id') or getattr(request, 'user_id', None)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    query = """
        SELECT u.id, u.documento, u.nombres, u.apellidos, u.email, u.telefono,
               u.id_rol, u.estado, r.nombre_rol
        FROM usuarios u
        LEFT JOIN roles r ON u.id_rol = r.id
        WHERE u.id = %s
    """
    usuario = db.obtener_uno(query, (user_id,))
    
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': usuario['id'],
            'documento': usuario['documento'],
            'nombres': usuario['nombres'],
            'apellidos': usuario['apellidos'],
            'nombre_completo': f"{usuario['nombres']} {usuario['apellidos']}",
            'email': usuario['email'],
            'telefono': usuario['telefono'],
            'rol': usuario['nombre_rol'],
            'estado': usuario['estado']
        }
    })


# =========================================================
# ENDPOINTS DE EQUIPOS
# =========================================================

@api_bp.route('/equipos', methods=['GET'])
@require_auth
def api_equipos_lista():
    """Lista todos los equipos"""
    try:
        # Parámetros de filtrado
        estado = request.args.get('estado')
        laboratorio = request.args.get('laboratorio')
        categoria = request.args.get('categoria')
        buscar = request.args.get('q')
        
        query = """
            SELECT e.id, e.codigo_interno, e.codigo_qr, e.nombre, e.marca, e.modelo,
                   e.estado, e.estado_fisico, e.ubicacion_especifica,
                   c.nombre as categoria_nombre,
                   l.nombre as laboratorio_nombre
            FROM equipos e
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            WHERE 1=1
        """
        params = []
        
        if estado:
            query += " AND e.estado = %s"
            params.append(estado)
        if laboratorio:
            query += " AND e.id_laboratorio = %s"
            params.append(laboratorio)
        if categoria:
            query += " AND e.id_categoria = %s"
            params.append(categoria)
        if buscar:
            query += " AND (e.nombre LIKE %s OR e.codigo_interno LIKE %s)"
            params.extend([f"%{buscar}%", f"%{buscar}%"])
        
        query += " ORDER BY e.nombre LIMIT 100"
        
        equipos = db.ejecutar_query(query, tuple(params) if params else None)
        
        return jsonify({
            'success': True,
            'data': equipos,
            'total': len(equipos)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/equipos/<int:equipo_id>', methods=['GET'])
@require_auth
def api_equipo_detalle(equipo_id):
    """Obtiene detalle de un equipo"""
    query = """
        SELECT e.*, c.nombre as categoria_nombre, l.nombre as laboratorio_nombre
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
        LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
        WHERE e.id = %s
    """
    equipo = db.obtener_uno(query, (equipo_id,))
    
    if not equipo:
        return jsonify({'success': False, 'message': 'Equipo no encontrado'}), 404
    
    return jsonify({'success': True, 'data': equipo})


@api_bp.route('/equipos/disponibles', methods=['GET'])
@require_auth
def api_equipos_disponibles():
    """Lista equipos disponibles para préstamo"""
    query = """
        SELECT e.id, e.codigo_interno, e.nombre, e.marca, e.modelo,
               e.estado_fisico, e.ubicacion_especifica,
               c.nombre as categoria, l.nombre as laboratorio
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
        LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
        WHERE e.estado = 'disponible'
        ORDER BY e.nombre
    """
    equipos = db.ejecutar_query(query)
    
    return jsonify({
        'success': True,
        'data': equipos,
        'total': len(equipos)
    })


# =========================================================
# ENDPOINTS DE PRÉSTAMOS
# =========================================================

@api_bp.route('/prestamos', methods=['GET'])
@require_auth
def api_prestamos_lista():
    """Lista préstamos"""
    estado = request.args.get('estado')
    
    query = """
        SELECT p.id, p.codigo, p.fecha, p.fecha_devolucion_programada,
               p.fecha_devolucion_real, p.estado, p.proposito,
               e.nombre as equipo_nombre, e.codigo_interno as equipo_codigo,
               CONCAT(u.nombres, ' ', u.apellidos) as solicitante
        FROM prestamos p
        LEFT JOIN equipos e ON p.id_equipo = e.id
        LEFT JOIN usuarios u ON p.id_usuario_solicitante = u.id
        WHERE 1=1
    """
    params = []
    
    if estado:
        query += " AND p.estado = %s"
        params.append(estado)
    
    query += " ORDER BY p.fecha_solicitud DESC LIMIT 100"
    
    prestamos = db.ejecutar_query(query, tuple(params) if params else None)
    
    return jsonify({
        'success': True,
        'data': prestamos,
        'total': len(prestamos)
    })


@api_bp.route('/prestamos', methods=['POST'])
@require_auth
def api_prestamo_crear():
    """Crea un nuevo préstamo"""
    data = request.get_json() or {}
    
    id_equipo = data.get('id_equipo')
    proposito = data.get('proposito')
    fecha_devolucion = data.get('fecha_devolucion_programada')
    
    if not id_equipo:
        return jsonify({'success': False, 'message': 'ID de equipo requerido'}), 400
    
    # Verificar equipo disponible
    equipo = db.obtener_uno("SELECT estado FROM equipos WHERE id = %s", (id_equipo,))
    if not equipo:
        return jsonify({'success': False, 'message': 'Equipo no encontrado'}), 404
    if equipo['estado'] != 'disponible':
        return jsonify({'success': False, 'message': 'Equipo no disponible'}), 400
    
    user_id = session.get('user_id') or getattr(request, 'user_id', None)
    
    # Generar código único
    import uuid
    codigo = f"PREST-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Crear préstamo
        prestamo_id = db.insertar('prestamos', {
            'codigo': codigo,
            'id_equipo': id_equipo,
            'id_usuario_solicitante': user_id,
            'proposito': proposito,
            'fecha_devolucion_programada': fecha_devolucion,
            'estado': 'solicitado'
        })
        
        return jsonify({
            'success': True,
            'message': 'Préstamo solicitado exitosamente',
            'data': {'id': prestamo_id, 'codigo': codigo}
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/prestamos/<int:prestamo_id>/aprobar', methods=['POST'])
@require_auth
@require_level(3)
def api_prestamo_aprobar(prestamo_id):
    """Aprueba un préstamo"""
    user_id = session.get('user_id') or getattr(request, 'user_id', None)
    
    prestamo = db.obtener_uno("SELECT estado, id_equipo FROM prestamos WHERE id = %s", (prestamo_id,))
    if not prestamo:
        return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
    if prestamo['estado'] != 'solicitado':
        return jsonify({'success': False, 'message': 'Solo se pueden aprobar préstamos solicitados'}), 400
    
    try:
        db.actualizar('prestamos', 
            {'estado': 'aprobado', 'id_usuario_autorizador': user_id},
            'id = %s', (prestamo_id,))
        
        return jsonify({'success': True, 'message': 'Préstamo aprobado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/prestamos/<int:prestamo_id>/devolver', methods=['POST'])
@require_auth
def api_prestamo_devolver(prestamo_id):
    """Registra devolución de préstamo"""
    data = request.get_json() or {}
    observaciones = data.get('observaciones')
    calificacion = data.get('calificacion')
    
    prestamo = db.obtener_uno("SELECT estado, id_equipo FROM prestamos WHERE id = %s", (prestamo_id,))
    if not prestamo:
        return jsonify({'success': False, 'message': 'Préstamo no encontrado'}), 404
    if prestamo['estado'] != 'activo':
        return jsonify({'success': False, 'message': 'Solo se pueden devolver préstamos activos'}), 400
    
    try:
        from datetime import datetime
        
        db.actualizar('prestamos', {
            'estado': 'devuelto',
            'fecha_devolucion_real': datetime.now(),
            'observaciones_devolucion': observaciones,
            'calificacion_devolucion': calificacion
        }, 'id = %s', (prestamo_id,))
        
        # Marcar equipo como disponible
        db.actualizar('equipos', {'estado': 'disponible'}, 'id = %s', (prestamo['id_equipo'],))
        
        return jsonify({'success': True, 'message': 'Devolución registrada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =========================================================
# ENDPOINTS DE USUARIOS
# =========================================================

@api_bp.route('/usuarios', methods=['GET'])
@require_auth
@require_level(3)
def api_usuarios_lista():
    """Lista usuarios"""
    query = """
        SELECT u.id, u.documento, u.nombres, u.apellidos, u.email, u.telefono,
               u.estado, r.nombre_rol
        FROM usuarios u
        LEFT JOIN roles r ON u.id_rol = r.id
        ORDER BY u.nombres, u.apellidos
        LIMIT 100
    """
    usuarios = db.ejecutar_query(query)
    
    return jsonify({
        'success': True,
        'data': usuarios,
        'total': len(usuarios)
    })


# =========================================================
# ENDPOINTS DE ESTADÍSTICAS
# =========================================================

@api_bp.route('/estadisticas/dashboard', methods=['GET'])
@require_auth
def api_estadisticas_dashboard():
    """Estadísticas para dashboard"""
    stats = {}
    
    # Equipos por estado
    query = "SELECT estado, COUNT(*) as total FROM equipos GROUP BY estado"
    estados = db.ejecutar_query(query)
    stats['equipos_estado'] = {e['estado']: e['total'] for e in estados}
    
    # Préstamos activos
    query = "SELECT COUNT(*) as total FROM prestamos WHERE estado = 'activo'"
    result = db.obtener_uno(query)
    stats['prestamos_activos'] = result['total'] if result else 0
    
    # Usuarios activos
    query = "SELECT COUNT(*) as total FROM usuarios WHERE estado = 'activo'"
    result = db.obtener_uno(query)
    stats['usuarios_activos'] = result['total'] if result else 0
    
    # Alertas pendientes
    query = "SELECT COUNT(*) as total FROM alertas_mantenimiento WHERE estado_alerta = 'pendiente'"
    try:
        result = db.obtener_uno(query)
        stats['alertas_pendientes'] = result['total'] if result else 0
    except:
        stats['alertas_pendientes'] = 0
    
    return jsonify({'success': True, 'data': stats})


# =========================================================
# ENDPOINTS DE LABORATORIOS
# =========================================================

@api_bp.route('/laboratorios', methods=['GET'])
@require_auth
def api_laboratorios_lista():
    """Lista laboratorios"""
    query = """
        SELECT l.id, l.codigo_lab, l.nombre, l.tipo, l.ubicacion,
               l.capacidad_personas, l.estado,
               CONCAT(u.nombres, ' ', u.apellidos) as responsable
        FROM laboratorios l
        LEFT JOIN usuarios u ON l.responsable_id = u.id
        ORDER BY l.nombre
    """
    laboratorios = db.ejecutar_query(query)
    
    return jsonify({
        'success': True,
        'data': laboratorios,
        'total': len(laboratorios)
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check del API"""
    try:
        db.ejecutar_query("SELECT 1")
        db_status = 'ok'
    except:
        db_status = 'error'
    
    return jsonify({
        'success': True,
        'status': 'ok',
        'database': db_status,
        'version': '1.0.0'
    })


# =========================================================
# FUNCIÓN PARA REGISTRAR BLUEPRINTS
# =========================================================

def registrar_blueprints(app):
    """Registra todos los blueprints en la aplicación Flask"""
    app.register_blueprint(api_bp)
    print("✅ API REST registrada en /api/v1")
    
    # Registrar blueprint de autenticación
    try:
        from backend.api.auth import auth_bp
        app.register_blueprint(auth_bp)
        print("✅ API Auth registrada en /api/v1/auth")
    except ImportError as e:
        print(f"⚠️  No se pudo cargar auth_bp: {e}")
    
    # Registrar blueprint de equipos - importar módulo para cargar rutas
    try:
        import backend.api.equipos  # Esto carga las rutas en equipos_bp
        app.register_blueprint(equipos_bp)
        print("✅ API Equipos registrada en /api/equipos")
    except Exception as e:
        print(f"⚠️  Error registrando equipos_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de reconocimiento IA
    try:
        import backend.api.reconocimiento_ia  # Esto carga las rutas en reconocimiento_bp
        app.register_blueprint(reconocimiento_bp)
        print("✅ API Reconocimiento IA registrada en /api/reconocimiento")
    except Exception as e:
        print(f"⚠️  Error registrando reconocimiento_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de usuarios
    try:
        import backend.api.usuarios  # Esto carga las rutas en usuarios_bp
        app.register_blueprint(usuarios_bp)
        print("✅ API Usuarios registrada en /api/usuarios")
    except Exception as e:
        print(f"⚠️  Error registrando usuarios_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de roles
    try:
        from backend.api.roles import roles_bp
        app.register_blueprint(roles_bp)
        print("✅ API Roles registrada en /api/roles")
    except Exception as e:
        print(f"⚠️  Error registrando roles_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de programas
    try:
        from backend.api.programas import programas_bp
        app.register_blueprint(programas_bp)
        print("✅ API Programas registrada en /api/programas")
    except Exception as e:
        print(f"⚠️  Error registrando programas_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de laboratorios
    try:
        from backend.api.laboratorios import laboratorios_bp
        app.register_blueprint(laboratorios_bp)
        print("✅ API Laboratorios registrada en /api/laboratorios")
    except Exception as e:
        print(f"⚠️  Error registrando laboratorios_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de prácticas
    try:
        from backend.api.practicas import practicas_bp
        app.register_blueprint(practicas_bp)
        print("✅ API Prácticas registrada en /api/practicas")
    except Exception as e:
        print(f"⚠️  Error registrando practicas_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de asistente de voz LUCIA
    try:
        from backend.api.asistente_voz import asistente_voz_bp
        app.register_blueprint(asistente_voz_bp)
        print("✅ API Asistente de Voz LUCIA registrada en /api/voz")
    except Exception as e:
        print(f"⚠️  Error registrando asistente_voz_bp: {e}")
        import traceback
        traceback.print_exc()
    
    # Registrar blueprint de préstamos
    try:
        from backend.api.prestamos import prestamos_bp
        app.register_blueprint(prestamos_bp)
        print("✅ API Préstamos registrada en /api/prestamos")
    except Exception as e:
        print(f"⚠️  Error registrando prestamos_bp: {e}")
        import traceback
        traceback.print_exc()
