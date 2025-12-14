"""
Configuración Central del Sistema GIL
Centro Minero de Sogamoso - SENA
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Configuración base del sistema"""
    
    # =========================================================
    # RUTAS BASE
    # =========================================================
    BASE_DIR = BASE_DIR
    
    # =========================================================
    # APLICACIÓN
    # =========================================================
    APP_NAME = os.getenv('APP_NAME', 'Sistema GIL')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    SECRET_KEY = os.getenv('APP_SECRET_KEY', 'gil_secret_key_2025_sena_sogamoso')
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', 5000))
    DEBUG = os.getenv('APP_DEBUG', 'true').lower() == 'true'
    
    # =========================================================
    # BASE DE DATOS MySQL
    # =========================================================
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'gil_laboratorios')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
    DB_COLLATION = os.getenv('DB_COLLATION', 'utf8mb4_unicode_ci')
    
    # Pool de conexiones
    DB_POOL_NAME = os.getenv('DB_POOL_NAME', 'gil_pool')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_POOL_RESET_SESSION = os.getenv('DB_POOL_RESET_SESSION', 'true').lower() == 'true'
    
    # =========================================================
    # FLASK
    # =========================================================
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # =========================================================
    # JWT / SEGURIDAD
    # =========================================================
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'gil_jwt_secret_2025')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    JWT_ACCESS_TOKEN_EXPIRES = JWT_EXPIRATION_HOURS * 3600  # En segundos
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))
    PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'true').lower() == 'true'
    
    # =========================================================
    # ARCHIVOS Y UPLOADS
    # =========================================================
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads/')
    STATIC_FOLDER = os.getenv('STATIC_FOLDER', './static/')
    TEMPLATES_FOLDER = os.getenv('TEMPLATES_FOLDER', './templates/')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # =========================================================
    # LOGGING
    # =========================================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'gil_system.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # =========================================================
    # ASISTENTE DE VOZ LUCIA
    # =========================================================
    LUCIA_ENABLED = os.getenv('LUCIA_ENABLED', 'true').lower() == 'true'
    LUCIA_LANGUAGE = os.getenv('LUCIA_LANGUAGE', 'es-CO')
    LUCIA_CONFIDENCE_THRESHOLD = float(os.getenv('LUCIA_CONFIDENCE_THRESHOLD', 0.7))
    LUCIA_TIMEOUT_SECONDS = int(os.getenv('LUCIA_TIMEOUT_SECONDS', 5))
    LUCIA_SAMPLE_RATE = int(os.getenv('LUCIA_SAMPLE_RATE', 16000))
    
    # =========================================================
    # RECONOCIMIENTO DE IMÁGENES (IA)
    # =========================================================
    AI_IMAGES_ENABLED = os.getenv('AI_IMAGES_ENABLED', 'true').lower() == 'true'
    AI_IMAGES_MODEL_PATH = os.getenv('AI_IMAGES_MODEL_PATH', './models/mobilenet_v2/')
    AI_IMAGES_CONFIDENCE_THRESHOLD = float(os.getenv('AI_IMAGES_CONFIDENCE_THRESHOLD', 0.85))
    AI_IMAGES_MAX_SIZE = int(os.getenv('AI_IMAGES_MAX_SIZE', 1024))
    AI_IMAGES_SUPPORTED_FORMATS = os.getenv('AI_IMAGES_SUPPORTED_FORMATS', 'jpg,jpeg,png,bmp').split(',')
    
    # =========================================================
    # EMAIL
    # =========================================================
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'Sistema GIL <laboratorios@sena.edu.co>')
    
    # =========================================================
    # NOTIFICACIONES
    # =========================================================
    NOTIFICATIONS_ENABLED = os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
    NOTIFICATIONS_MAINTENANCE_DAYS = int(os.getenv('NOTIFICATIONS_MAINTENANCE_DAYS', 7))
    NOTIFICATIONS_OVERDUE_LOANS = os.getenv('NOTIFICATIONS_OVERDUE_LOANS', 'true').lower() == 'true'
    NOTIFICATIONS_LOW_STOCK = os.getenv('NOTIFICATIONS_LOW_STOCK', 'true').lower() == 'true'
    
    # =========================================================
    # BACKUP
    # =========================================================
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
    BACKUP_FREQUENCY_HOURS = int(os.getenv('BACKUP_FREQUENCY_HOURS', 24))
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    BACKUP_PATH = os.getenv('BACKUP_PATH', './backups/')
    
    # =========================================================
    # REDIS (Tareas en segundo plano)
    # =========================================================
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    
    # =========================================================
    # NIVELES DE ACCESO (Roles)
    # =========================================================
    NIVEL_APRENDIZ = 1
    NIVEL_FUNCIONARIO = 2
    NIVEL_INSTRUCTOR = 3
    NIVEL_INSTRUCTOR_QUIMICA = 4
    NIVEL_INSTRUCTOR_INVENTARIO = 5
    NIVEL_ADMINISTRADOR = 6
    
    @classmethod
    def get_db_config(cls):
        """Retorna configuración de base de datos como diccionario"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'charset': cls.DB_CHARSET,
            'collation': cls.DB_COLLATION,
            'pool_name': cls.DB_POOL_NAME,
            'pool_size': cls.DB_POOL_SIZE,
            'pool_reset_session': cls.DB_POOL_RESET_SESSION
        }
    
    @classmethod
    def get_db_uri(cls):
        """Retorna URI de conexión MySQL"""
        return f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    FLASK_DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    FLASK_DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    DEBUG = True
    DB_NAME = 'gil_laboratorios_test'


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
