"""
Módulo de Configuración - Sistema GIL
Centro Minero de Sogamoso - SENA
"""
from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, config, get_config
from .database_config import DatabaseManager
from .api_config import (
    APIConfig,
    APIConfigDevelopment,
    APIConfigProduction,
    APIConfigTesting,
    JWTManager,
    token_required,
    role_required,
    admin_required,
    instructor_required,
    tecnico_required,
    api_config,
    get_api_config
)

__all__ = [
    # Configuración general
    'Config',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'config',
    'get_config',
    
    # Base de datos
    'DatabaseManager',
    
    # API - Configuración
    'APIConfig',
    'APIConfigDevelopment',
    'APIConfigProduction',
    'APIConfigTesting',
    'api_config',
    'get_api_config',
    
    # API - JWT
    'JWTManager',
    
    # API - Decoradores
    'token_required',
    'role_required',
    'admin_required',
    'instructor_required',
    'tecnico_required'
]
