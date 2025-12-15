"""
Script para actualizar permisos de roles en la base de datos
Cambia 'practicas' por 'reservas' en los permisos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.utils.database import DatabaseManager

def actualizar_permisos():
    db = DatabaseManager()
    
    try:
        print("🔄 Actualizando permisos de roles...")
        
        # Actualizar Administrador (id=1)
        print("\n1️⃣ Actualizando rol Administrador...")
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 1",
            ('{"all": true, "reservas": true}',)
        )
        print("   ✅ Administrador actualizado: all=true, reservas=true")
        
        # Actualizar Instructor (id=2)
        print("\n2️⃣ Actualizando rol Instructor...")
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 2",
            ('{"reservas": true}',)
        )
        print("   ✅ Instructor actualizado: reservas=true")
        
        # Verificar cambios
        print("\n📋 Verificando cambios...")
        roles = db.ejecutar_query(
            "SELECT id, nombre_rol, permisos FROM roles WHERE id IN (1, 2)"
        )
        
        print("\n" + "="*60)
        print("PERMISOS ACTUALIZADOS:")
        print("="*60)
        for rol in roles:
            print(f"\n🔹 {rol['nombre_rol']} (ID: {rol['id']})")
            print(f"   Permisos: {rol['permisos']}")
        print("\n" + "="*60)
        
        print("\n✅ ¡Actualización completada exitosamente!")
        print("\n⚠️  IMPORTANTE: Reinicia la aplicación Flask para que los cambios surtan efecto.")
        
    except Exception as e:
        print(f"\n❌ Error actualizando permisos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.cerrar()

if __name__ == "__main__":
    actualizar_permisos()
