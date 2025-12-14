"""
Configuración de API REST
Sistema GIL - Centro Minero de Sogamoso - SENA
"""
import os
from functools import wraps
from flask import jsonify, request
import jwt
from datetime import datetime, timedelta

try:
    from config.config import Config
except ImportError:
    from .config import Config


# =========================================================
# CONFIGURACIÓN BASE DE LA API
# =========================================================

class APIConfig:
    """Configuración y utilidades para la API REST"""
    
    # =========================================================
    # INFORMACIÓN DE LA API
    # =========================================================
    API_TITLE = "Sistema GIL - API REST"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API REST para el Sistema de Gestión Inteligente de Laboratorios"
    
    # Prefijos y versioning
    API_PREFIX = '/api'
    API_VERSION_PREFIX = '/v1'
    API_FULL_PREFIX = f'{API_PREFIX}{API_VERSION_PREFIX}'
    
    # =========================================================
    # CÓDIGOS DE ESTADO HTTP
    # =========================================================
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_NO_CONTENT = 204
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_CONFLICT = 409
    HTTP_UNPROCESSABLE = 422
    HTTP_TOO_MANY_REQUESTS = 429
    HTTP_INTERNAL_ERROR = 500
    HTTP_SERVICE_UNAVAILABLE = 503
    
    # =========================================================
    # MENSAJES DE RESPUESTA ESTÁNDAR
    # =========================================================
    MESSAGES = {
        'success': 'Operación exitosa',
        'created': 'Recurso creado exitosamente',
        'updated': 'Recurso actualizado exitosamente',
        'deleted': 'Recurso eliminado exitosamente',
        'not_found': 'Recurso no encontrado',
        'unauthorized': 'No autorizado. Inicie sesión',
        'forbidden': 'No tiene permisos para esta acción',
        'bad_request': 'Datos de solicitud inválidos',
        'conflict': 'El recurso ya existe',
        'internal_error': 'Error interno del servidor',
        'token_expired': 'Token expirado. Inicie sesión nuevamente',
        'token_invalid': 'Token inválido',
        'rate_limit': 'Demasiadas solicitudes. Intente más tarde',
        'validation_error': 'Error de validación en los datos',
        'service_unavailable': 'Servicio no disponible temporalmente'
    }
    
    # =========================================================
    # RATE LIMITING
    # =========================================================
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Límites por tipo de usuario
    RATELIMIT_ADMIN = "1000 per hour"
    RATELIMIT_INSTRUCTOR = "500 per hour"
    RATELIMIT_APRENDIZ = "200 per hour"
    RATELIMIT_PUBLIC = "50 per hour"
    
    # =========================================================
    # PAGINACIÓN
    # =========================================================
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # =========================================================
    # TIMEOUTS
    # =========================================================
    API_TIMEOUT = 30
    LONG_RUNNING_TIMEOUT = 300  # 5 minutos para operaciones largas
    
    # =========================================================
    # CACHÉ
    # =========================================================
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    CACHE_KEY_PREFIX = 'gil_api_'
    
    # =========================================================
    # CORS
    # =========================================================
    API_CORS_ORIGINS = os.getenv('API_CORS_ORIGINS', '*').split(',')
    API_CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    API_CORS_ALLOW_HEADERS = [
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'X-API-Key'
    ]
    API_CORS_EXPOSE_HEADERS = [
        'X-Total-Count',
        'X-Page-Number',
        'X-Page-Size',
        'X-RateLimit-Limit',
        'X-RateLimit-Remaining'
    ]
    API_CORS_MAX_AGE = 3600
    
    # =========================================================
    # COMPRESIÓN
    # =========================================================
    COMPRESS_ENABLED = True
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500  # bytes
    
    # =========================================================
    # VALIDACIÓN
    # =========================================================
    VALIDATE_REQUEST = True
    VALIDATE_RESPONSE = False  # En producción puede afectar performance
    
    # =========================================================
    # DOCUMENTACIÓN (SWAGGER)
    # =========================================================
    SWAGGER_ENABLED = os.getenv('SWAGGER_ENABLED', 'true').lower() == 'true'
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    
    # =========================================================
    # FORMATO DE RESPUESTAS JSON
    # =========================================================
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # =========================================================
    # HEADERS DE SEGURIDAD
    # =========================================================
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # =========================================================
    # ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN)
    # =========================================================
    PUBLIC_ENDPOINTS = [
        f'{API_PREFIX}/auth/login',
        f'{API_PREFIX}/auth/refresh',
        f'{API_PREFIX}/health',
        f'{API_PREFIX}/docs',
        f'{API_PREFIX}/swagger',
        f'{API_PREFIX}{API_VERSION_PREFIX}/auth/login',
        f'{API_PREFIX}{API_VERSION_PREFIX}/auth/refresh',
    ]
    
    # =========================================================
    # ENDPOINTS DE SOLO LECTURA
    # =========================================================
    READ_ONLY_ENDPOINTS = [
        f'{API_PREFIX}/equipos/disponibles',
        f'{API_PREFIX}/inventario/critico',
        f'{API_PREFIX}/estadisticas'
    ]
    
    # =========================================================
    # DEFINICIÓN DE ENDPOINTS
    # =========================================================
    ENDPOINTS = {
        # Autenticación
        'auth_login': f'{API_FULL_PREFIX}/auth/login',
        'auth_logout': f'{API_FULL_PREFIX}/auth/logout',
        'auth_refresh': f'{API_FULL_PREFIX}/auth/refresh',
        'auth_me': f'{API_FULL_PREFIX}/auth/me',
        
        # Usuarios
        'usuarios': f'{API_FULL_PREFIX}/usuarios',
        'usuario': f'{API_FULL_PREFIX}/usuarios/<int:id>',
        
        # Equipos
        'equipos': f'{API_FULL_PREFIX}/equipos',
        'equipo': f'{API_FULL_PREFIX}/equipos/<int:id>',
        'equipos_buscar': f'{API_FULL_PREFIX}/equipos/buscar',
        'equipos_qr': f'{API_FULL_PREFIX}/equipos/qr/<string:codigo>',
        'equipos_disponibles': f'{API_FULL_PREFIX}/equipos/disponibles',
        
        # Préstamos
        'prestamos': f'{API_FULL_PREFIX}/prestamos',
        'prestamo': f'{API_FULL_PREFIX}/prestamos/<int:id>',
        'prestamos_activos': f'{API_FULL_PREFIX}/prestamos/activos',
        'prestamo_devolver': f'{API_FULL_PREFIX}/prestamos/<int:id>/devolver',
        
        # Laboratorios
        'laboratorios': f'{API_FULL_PREFIX}/laboratorios',
        'laboratorio': f'{API_FULL_PREFIX}/laboratorios/<int:id>',
        
        # Mantenimiento
        'mantenimientos': f'{API_FULL_PREFIX}/mantenimientos',
        'mantenimiento': f'{API_FULL_PREFIX}/mantenimientos/<int:id>',
        'alertas': f'{API_FULL_PREFIX}/mantenimientos/alertas',
        
        # Prácticas
        'practicas': f'{API_FULL_PREFIX}/practicas',
        'practica': f'{API_FULL_PREFIX}/practicas/<int:id>',
        
        # LUCIA (Asistente de voz)
        'lucia_comando': f'{API_FULL_PREFIX}/lucia/comando',
        'lucia_historial': f'{API_FULL_PREFIX}/lucia/historial',
        
        # Reconocimiento de imágenes
        'imagen_identificar': f'{API_FULL_PREFIX}/imagen/identificar',
        'imagen_historial': f'{API_FULL_PREFIX}/imagen/historial',
        
        # Reportes
        'reportes_dashboard': f'{API_FULL_PREFIX}/reportes/dashboard',
        'reportes_equipos': f'{API_FULL_PREFIX}/reportes/equipos',
        'reportes_prestamos': f'{API_FULL_PREFIX}/reportes/prestamos',
        
        # Health & Status
        'health': f'{API_PREFIX}/health',
        'status': f'{API_PREFIX}/status',
    }
    
    # =========================================================
    # MÉTODOS DE RESPUESTA
    # =========================================================
    
    @staticmethod
    def response_success(data=None, message=None, status_code=200):
        """Genera respuesta exitosa estándar"""
        response = {
            'success': True,
            'message': message or APIConfig.MESSAGES['success'],
            'timestamp': datetime.now().isoformat()
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code
    
    @staticmethod
    def response_error(message=None, status_code=400, errors=None):
        """Genera respuesta de error estándar"""
        response = {
            'success': False,
            'message': message or APIConfig.MESSAGES['bad_request'],
            'timestamp': datetime.now().isoformat()
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), status_code
    
    @staticmethod
    def response_paginated(data, page, per_page, total):
        """Genera respuesta paginada con headers"""
        response = jsonify({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            },
            'timestamp': datetime.now().isoformat()
        })
        # Headers adicionales para paginación
        response.headers['X-Total-Count'] = str(total)
        response.headers['X-Page-Number'] = str(page)
        response.headers['X-Page-Size'] = str(per_page)
        return response, 200
    
    @staticmethod
    def response_created(data=None, message=None):
        """Respuesta para recurso creado"""
        return APIConfig.response_success(
            data=data,
            message=message or APIConfig.MESSAGES['created'],
            status_code=APIConfig.HTTP_CREATED
        )
    
    @staticmethod
    def response_not_found(message=None):
        """Respuesta para recurso no encontrado"""
        return APIConfig.response_error(
            message=message or APIConfig.MESSAGES['not_found'],
            status_code=APIConfig.HTTP_NOT_FOUND
        )
    
    @staticmethod
    def response_unauthorized(message=None):
        """Respuesta para no autorizado"""
        return APIConfig.response_error(
            message=message or APIConfig.MESSAGES['unauthorized'],
            status_code=APIConfig.HTTP_UNAUTHORIZED
        )
    
    @staticmethod
    def response_forbidden(message=None):
        """Respuesta para acceso prohibido"""
        return APIConfig.response_error(
            message=message or APIConfig.MESSAGES['forbidden'],
            status_code=APIConfig.HTTP_FORBIDDEN
        )
    
    @staticmethod
    def response_validation_error(errors):
        """Respuesta para errores de validación"""
        return APIConfig.response_error(
            message=APIConfig.MESSAGES['validation_error'],
            status_code=APIConfig.HTTP_UNPROCESSABLE,
            errors=errors
        )
    
    @classmethod
    def get_pagination_params(cls):
        """Obtiene parámetros de paginación del request"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', cls.DEFAULT_PAGE_SIZE, type=int)
        per_page = min(per_page, cls.MAX_PAGE_SIZE)  # Limitar máximo
        return page, per_page
    
    @classmethod
    def is_public_endpoint(cls, path):
        """Verifica si un endpoint es público"""
        return any(path.startswith(ep) for ep in cls.PUBLIC_ENDPOINTS)


# =========================================================
# CONFIGURACIONES POR ENTORNO
# =========================================================

class APIConfigDevelopment(APIConfig):
    """Configuración de API para desarrollo"""
    RATELIMIT_ENABLED = False
    SWAGGER_ENABLED = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    VALIDATE_RESPONSE = True
    API_CORS_ORIGINS = ['*']


class APIConfigProduction(APIConfig):
    """Configuración de API para producción"""
    RATELIMIT_ENABLED = True
    SWAGGER_ENABLED = False
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Límites más estrictos
    RATELIMIT_ADMIN = "500 per hour"
    RATELIMIT_INSTRUCTOR = "300 per hour"
    RATELIMIT_APRENDIZ = "100 per hour"
    RATELIMIT_PUBLIC = "30 per hour"
    
    # Solo orígenes específicos
    API_CORS_ORIGINS = os.getenv('API_CORS_ORIGINS', 'https://gil.sena.edu.co').split(',')


class APIConfigTesting(APIConfig):
    """Configuración de API para testing"""
    RATELIMIT_ENABLED = False
    CACHE_ENABLED = False
    SWAGGER_ENABLED = True
    VALIDATE_RESPONSE = True


# =========================================================
# MANEJO DE JWT
# =========================================================

class JWTManager:
    """Manejo de tokens JWT"""
    
    @staticmethod
    def generate_token(user_id: int, user_role: int, extra_claims: dict = None):
        """Genera un token JWT"""
        payload = {
            'user_id': user_id,
            'user_role': user_role,
            'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def generate_refresh_token(user_id: int):
        """Genera un token de refresh (mayor duración)"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def decode_token(token: str):
        """Decodifica un token JWT"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, APIConfig.MESSAGES['token_expired']
        except jwt.InvalidTokenError:
            return None, APIConfig.MESSAGES['token_invalid']
    
    @staticmethod
    def get_token_from_header():
        """Obtiene el token del header Authorization"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    
    @staticmethod
    def get_current_user():
        """Obtiene información del usuario actual del token"""
        token = JWTManager.get_token_from_header()
        if token:
            payload, error = JWTManager.decode_token(token)
            if payload:
                return {
                    'user_id': payload.get('user_id'),
                    'user_role': payload.get('user_role')
                }
        return None


# =========================================================
# DECORADORES DE AUTENTICACIÓN Y AUTORIZACIÓN
# =========================================================

def token_required(f):
    """Decorador para proteger rutas con JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = JWTManager.get_token_from_header()
        
        if not token:
            return APIConfig.response_unauthorized()
        
        payload, error = JWTManager.decode_token(token)
        if error:
            return APIConfig.response_error(error, APIConfig.HTTP_UNAUTHORIZED)
        
        # Agregar información del usuario al request
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('user_role')
        
        return f(*args, **kwargs)
    return decorated


def role_required(min_role: int):
    """Decorador para verificar rol mínimo requerido"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user_role') or request.user_role < min_role:
                return APIConfig.response_forbidden()
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    """Decorador para rutas que requieren administrador"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role < Config.NIVEL_ADMINISTRADOR:
            return APIConfig.response_forbidden()
        return f(*args, **kwargs)
    return decorated


def instructor_required(f):
    """Decorador para rutas que requieren instructor"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role < Config.NIVEL_INSTRUCTOR:
            return APIConfig.response_forbidden()
        return f(*args, **kwargs)
    return decorated


def tecnico_required(f):
    """Decorador para rutas que requieren técnico de laboratorio"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role < Config.NIVEL_FUNCIONARIO:
            return APIConfig.response_forbidden()
        return f(*args, **kwargs)
    return decorated


# =========================================================
# DICCIONARIO DE CONFIGURACIONES
# =========================================================

api_config = {
    'development': APIConfigDevelopment,
    'production': APIConfigProduction,
    'testing': APIConfigTesting,
    'default': APIConfigDevelopment
}


def get_api_config(env=None):
    """
    Obtiene la configuración de API según el entorno
    
    Args:
        env: Nombre del entorno
        
    Returns:
        Clase de configuración de API
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return api_config.get(env, api_config['default'])
