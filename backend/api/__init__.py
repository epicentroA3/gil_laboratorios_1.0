# API REST - Sistema GIL
# Centro Minero de Sogamoso - SENA

from .blueprints import registrar_blueprints, api_bp
from .auth import auth_bp

__all__ = ['registrar_blueprints', 'api_bp', 'auth_bp']
