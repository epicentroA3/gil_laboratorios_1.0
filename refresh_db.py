"""
Script para refrescar/recrear la base de datos
Sistema GIL - Centro Minero SENA
"""
import mysql.connector
from mysql.connector import Error
import sys
import os

# Agregar path para importar config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import Config

def refresh_database(drop_first=False):
    """
    Refresca la base de datos
    
    Args:
        drop_first: Si True, elimina la BD antes de recrearla
    """
    try:
        # Conectar sin base de datos específica
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset=Config.DB_CHARSET,
            use_unicode=True
        )
        
        cursor = connection.cursor()
        
        if drop_first:
            print(f"⚠️  Eliminando base de datos '{Config.DB_NAME}'...")
            cursor.execute(f"DROP DATABASE IF EXISTS {Config.DB_NAME}")
            print(f"✅ Base de datos eliminada")
        
        # Crear base de datos
        print(f"📦 Creando base de datos '{Config.DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {Config.DB_NAME}")
        
        # Crear tabla inventario (faltante)
        print("📋 Creando tabla 'inventario'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INT PRIMARY KEY AUTO_INCREMENT,
                codigo VARCHAR(50) NOT NULL UNIQUE,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                id_categoria INT,
                id_laboratorio INT,
                cantidad_actual INT DEFAULT 0,
                cantidad_minima INT DEFAULT 5,
                unidad_medida VARCHAR(50) DEFAULT 'unidad',
                ubicacion VARCHAR(200),
                fecha_vencimiento DATE,
                lote VARCHAR(100),
                proveedor VARCHAR(200),
                precio_unitario DECIMAL(12,2),
                estado ENUM('disponible', 'agotado', 'por_vencer', 'vencido') DEFAULT 'disponible',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_codigo (codigo),
                INDEX idx_estado (estado),
                INDEX idx_categoria (id_categoria),
                INDEX idx_laboratorio (id_laboratorio)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        connection.commit()
        print("✅ Tabla 'inventario' creada exitosamente")
        
        # Verificar tablas existentes
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Tablas en la base de datos:")
        for table in tables:
            print(f"   • {table[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ Refresh de base de datos completado!")
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 REFRESH DE BASE DE DATOS - GIL")
    print("=" * 60)
    
    # Preguntar si quiere eliminar todo
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        print("\n⚠️  ADVERTENCIA: Esto ELIMINARÁ todos los datos!")
        confirm = input("¿Estás seguro? (escribir 'SI' para confirmar): ")
        if confirm.upper() == "SI":
            refresh_database(drop_first=True)
        else:
            print("❌ Operación cancelada")
    else:
        # Solo crear tablas faltantes
        refresh_database(drop_first=False)
        print("\n💡 Para recrear TODO desde cero, usa: python refresh_db.py --drop")
