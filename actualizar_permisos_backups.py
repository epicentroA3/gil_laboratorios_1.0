#!/usr/bin/env python3
"""
Script para actualizar permisos de backups en la base de datos
Solo el Administrador (id_rol = 1) debe tener acceso a backups
"""

import sys
import os

# Agregar rutas al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.database import DatabaseManager
from config.config import Config

def actualizar_permisos_backups():
    """Actualizar permisos para que solo el Administrador tenga acceso a backups"""
    
    print("=" * 60)
    print("ACTUALIZANDO PERMISOS DE BACKUPS")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        # Verificar permisos actuales
        print("\n📋 Permisos actuales:")
        query_ver = "SELECT id, nombre_rol, permisos FROM roles ORDER BY id"
        roles_actuales = db.ejecutar_query(query_ver)
        
        for rol in roles_actuales:
            print(f"  - {rol['nombre_rol']} (ID: {rol['id']})")
            print(f"    Permisos: {rol['permisos'][:100]}...")
        
        # Actualizar Administrador (id=1) - CON backups
        print("\n✅ Actualizando Administrador (id=1)...")
        permisos_admin = '{"all": true, "usuarios": true, "roles": true, "programas": true, "equipos": true, "laboratorios": true, "practicas": true, "reservas": true, "prestamos": true, "reportes": true, "mantenimiento": true, "capacitaciones": true, "reconocimiento": true, "ia_visual": true, "backups": true, "configuracion": true, "ayuda": true}'
        
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 1",
            (permisos_admin,)
        )
        
        # Actualizar Instructor (id=2) - SIN backups
        print("✅ Actualizando Instructor (id=2)...")
        permisos_instructor = '{"equipos": true, "laboratorios_ver": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones": true, "reconocimiento": true, "ayuda": true}'
        
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 2",
            (permisos_instructor,)
        )
        
        # Actualizar Técnico (id=3) - SIN backups
        print("✅ Actualizando Técnico Laboratorio (id=3)...")
        permisos_tecnico = '{"equipos": true, "reservas": true, "mantenimiento": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
        
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 3",
            (permisos_tecnico,)
        )
        
        # Actualizar Aprendiz (id=4) - SIN backups
        print("✅ Actualizando Aprendiz (id=4)...")
        permisos_aprendiz = '{"equipos_ver": true, "reservas_propias": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
        
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 4",
            (permisos_aprendiz,)
        )
        
        # Actualizar Coordinador (id=5) - SIN backups
        print("✅ Actualizando Coordinador (id=5)...")
        permisos_coordinador = '{"equipos_ver": true, "laboratorios_ver": true, "reservas_ver": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
        
        db.ejecutar_comando(
            "UPDATE roles SET permisos = %s WHERE id = 5",
            (permisos_coordinador,)
        )
        
        # Registrar en logs
        print("\n📝 Registrando en logs del sistema...")
        log_query = """
            INSERT INTO logs_sistema (modulo, nivel_log, mensaje, ip_address)
            VALUES ('sistema', 'INFO', %s, '127.0.0.1')
        """
        db.ejecutar_comando(
            log_query,
            ('Permisos de backups actualizados - Solo Administrador tiene acceso',)
        )
        
        # Verificar resultado final
        print("\n📋 Permisos actualizados:")
        roles_nuevos = db.ejecutar_query(query_ver)
        
        for rol in roles_nuevos:
            import json
            permisos_obj = json.loads(rol['permisos'])
            tiene_backups = permisos_obj.get('backups', False)
            
            print(f"\n  - {rol['nombre_rol']} (ID: {rol['id']})")
            print(f"    Permiso 'backups': {'✅ SÍ' if tiene_backups else '❌ NO'}")
            print(f"    Permiso 'all': {'✅ SÍ' if permisos_obj.get('all', False) else '❌ NO'}")
        
        print("\n" + "=" * 60)
        print("✅ PERMISOS ACTUALIZADOS CORRECTAMENTE")
        print("=" * 60)
        print("\n🔐 Solo el Administrador (id_rol=1) tiene acceso a backups")
        print("📌 Los demás roles NO tienen permiso de backups\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n🚀 Iniciando actualización de permisos...\n")
    
    if actualizar_permisos_backups():
        print("✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("❌ Proceso completado con errores")
        sys.exit(1)
