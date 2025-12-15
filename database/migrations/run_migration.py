"""
Script para ejecutar la migración de la tabla historial_mantenimiento
Ejecutar desde la raíz del proyecto: python database/migrations/run_migration.py
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.utils.database import DatabaseManager

def run_migration():
    db = DatabaseManager()
    
    print("=" * 60)
    print("MIGRACIÓN: Actualizar tabla historial_mantenimiento")
    print("=" * 60)
    
    try:
        # 1. Verificar si la columna 'estado' ya existe
        check_estado = db.ejecutar_query("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'historial_mantenimiento' 
            AND COLUMN_NAME = 'estado'
        """)
        
        if check_estado and check_estado[0]['count'] == 0:
            print("➕ Agregando columna 'estado'...")
            db.ejecutar_query("""
                ALTER TABLE historial_mantenimiento 
                ADD COLUMN estado ENUM('en_proceso', 'completado', 'cancelado') DEFAULT 'completado' 
                AFTER id_tipo_mantenimiento
            """)
            print("   ✅ Columna 'estado' agregada")
        else:
            print("   ⏭️ Columna 'estado' ya existe")
        
        # 2. Verificar si existe fecha_mantenimiento (para renombrar a fecha_inicio)
        check_fecha_mant = db.ejecutar_query("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'historial_mantenimiento' 
            AND COLUMN_NAME = 'fecha_mantenimiento'
        """)
        
        if check_fecha_mant and check_fecha_mant[0]['count'] > 0:
            print("🔄 Renombrando 'fecha_mantenimiento' a 'fecha_inicio'...")
            db.ejecutar_query("""
                ALTER TABLE historial_mantenimiento 
                CHANGE COLUMN fecha_mantenimiento fecha_inicio DATETIME NOT NULL
            """)
            print("   ✅ Columna renombrada")
        else:
            # Verificar si fecha_inicio ya existe
            check_fecha_inicio = db.ejecutar_query("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'historial_mantenimiento' 
                AND COLUMN_NAME = 'fecha_inicio'
            """)
            if check_fecha_inicio and check_fecha_inicio[0]['count'] > 0:
                print("   ⏭️ Columna 'fecha_inicio' ya existe")
            else:
                print("   ⚠️ No se encontró 'fecha_mantenimiento' ni 'fecha_inicio'")
        
        # 3. Agregar columna fecha_fin si no existe
        check_fecha_fin = db.ejecutar_query("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'historial_mantenimiento' 
            AND COLUMN_NAME = 'fecha_fin'
        """)
        
        if check_fecha_fin and check_fecha_fin[0]['count'] == 0:
            print("➕ Agregando columna 'fecha_fin'...")
            db.ejecutar_query("""
                ALTER TABLE historial_mantenimiento 
                ADD COLUMN fecha_fin DATETIME NULL AFTER fecha_inicio
            """)
            print("   ✅ Columna 'fecha_fin' agregada")
        else:
            print("   ⏭️ Columna 'fecha_fin' ya existe")
        
        # 4. Actualizar registros existentes
        print("🔄 Actualizando registros existentes...")
        db.ejecutar_query("""
            UPDATE historial_mantenimiento 
            SET estado = 'completado', 
                fecha_fin = fecha_inicio 
            WHERE fecha_fin IS NULL
        """)
        print("   ✅ Registros actualizados")
        
        # 5. Verificar resultado
        print("\n" + "=" * 60)
        print("VERIFICACIÓN")
        print("=" * 60)
        
        stats = db.ejecutar_query("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as completados,
                SUM(CASE WHEN estado = 'en_proceso' THEN 1 ELSE 0 END) as en_proceso,
                SUM(CASE WHEN estado = 'cancelado' THEN 1 ELSE 0 END) as cancelados
            FROM historial_mantenimiento
        """)
        
        if stats:
            s = stats[0]
            print(f"📊 Total registros: {s['total']}")
            print(f"   ✅ Completados: {s['completados']}")
            print(f"   🔄 En proceso: {s['en_proceso']}")
            print(f"   ❌ Cancelados: {s['cancelados']}")
        
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    run_migration()
