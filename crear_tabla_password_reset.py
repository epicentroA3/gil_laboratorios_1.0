"""
Script para crear la tabla password_reset_tokens
"""
import sys
sys.path.insert(0, '.')

from backend.utils.database import DatabaseManager

# Crear instancia del gestor de BD
db_manager = DatabaseManager()

# SQL para crear la tabla
sql = """
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    expira_en DATETIME NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_solicitud VARCHAR(45),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expira (expira_en),
    INDEX idx_usuario (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

try:
    print("Creando tabla password_reset_tokens...")
    db_manager.ejecutar_comando(sql)
    print("✅ Tabla creada exitosamente!")
    
    # Verificar que existe
    verificar = "SHOW TABLES LIKE 'password_reset_tokens'"
    resultado = db_manager.ejecutar_query(verificar)
    
    if resultado:
        print("✅ Tabla verificada en la base de datos")
        
        # Mostrar estructura
        desc = "DESCRIBE password_reset_tokens"
        estructura = db_manager.ejecutar_query(desc)
        print("\n📋 Estructura de la tabla:")
        for campo in estructura:
            print(f"  - {campo['Field']}: {campo['Type']}")
    else:
        print("❌ No se pudo verificar la tabla")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
