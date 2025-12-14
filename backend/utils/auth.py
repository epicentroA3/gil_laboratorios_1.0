# Autenticación y Seguridad
# Centro Minero SENA
# Integrado con configuración centralizada

import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, flash
from typing import Optional, Dict, Callable
import sys
import os

# Agregar path para importar config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import Config
    from config.api_config import APIConfig
except ImportError:
    Config = None
    APIConfig = None


class AuthManager:
    """Gestor de autenticación y seguridad"""
    
    def __init__(self, secret_key: str = None, token_expiration_hours: int = None):
        """
        Inicializa el gestor de autenticación usando Config centralizada
        
        Args:
            secret_key: Clave secreta para JWT (opcional, usa Config por defecto)
            token_expiration_hours: Horas de validez del token (opcional, usa Config por defecto)
        """
        if Config:
            self.secret_key = secret_key or Config.JWT_SECRET_KEY
            self.token_expiration = timedelta(hours=token_expiration_hours or Config.JWT_EXPIRATION_HOURS)
        else:
            self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'default_secret')
            self.token_expiration = timedelta(hours=token_expiration_hours or 8)
        
        self.algorithm = 'HS256'
    
    def generar_token(self, usuario_id: str, datos_adicionales: Optional[Dict] = None) -> str:
        """
        Genera un token JWT para un usuario
        
        Args:
            usuario_id: ID del usuario
            datos_adicionales: Datos adicionales para incluir en el token
            
        Returns:
            Token JWT
        """
        payload = {
            'usuario_id': usuario_id,
            'exp': datetime.utcnow() + self.token_expiration,
            'iat': datetime.utcnow()
        }
        
        if datos_adicionales:
            payload.update(datos_adicionales)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verificar_token(self, token: str) -> Optional[Dict]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Payload del token o None si es inválido
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def hash_password(self, password: str) -> str:
        """
        Genera un hash de una contraseña usando bcrypt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash (bcrypt)
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado
            
        Returns:
            True si coinciden
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            # Fallback para hashes SHA256 antiguos
            return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    def generar_api_key(self) -> str:
        """
        Genera una API key aleatoria
        
        Returns:
            API key
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def extraer_token_header(headers) -> Optional[str]:
        """
        Extrae el token del header Authorization
        
        Args:
            headers: Headers de la petición
            
        Returns:
            Token o None
        """
        auth_header = headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

# Decoradores para Flask

def require_auth(f: Callable) -> Callable:
    """
    Decorador que requiere autenticación para acceder a una ruta
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_level(min_level: int) -> Callable:
    """
    Decorador que requiere un nivel mínimo de acceso
    
    Args:
        min_level: Nivel mínimo requerido
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_level' not in session:
                return jsonify({'error': 'Autenticación requerida'}), 401
            
            if session['user_level'] < min_level:
                return jsonify({'error': 'Permisos insuficientes'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_jwt(auth_manager: AuthManager) -> Callable:
    """
    Decorador que requiere un token JWT válido
    
    Args:
        auth_manager: Instancia de AuthManager
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = AuthManager.extraer_token_header(request.headers)
            
            if not token:
                return jsonify({'error': 'Token requerido'}), 401
            
            payload = auth_manager.verificar_token(token)
            
            if not payload:
                return jsonify({'error': 'Token inválido o expirado'}), 401
            
            # Agregar payload al request para uso posterior
            request.user_data = payload
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
