import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='gil_laboratorios'
)

cursor = conn.cursor(dictionary=True)

print("\n=== VERIFICACIÓN DE PERMISOS DE ROLES ===\n")

# Consultar todos los roles y sus permisos
cursor.execute("""
    SELECT id, nombre_rol, permisos, descripcion
    FROM roles
    ORDER BY id
""")

roles = cursor.fetchall()

for rol in roles:
    print(f"\n{'='*70}")
    print(f"ID: {rol['id']}")
    print(f"Rol: {rol['nombre_rol']}")
    print(f"Descripción: {rol['descripcion']}")
    
    # Parsear permisos JSON
    permisos_str = rol['permisos'] or '{}'
    try:
        permisos = json.loads(permisos_str)
        print(f"\nPermisos:")
        for key, value in permisos.items():
            print(f"  - {key}: {value}")
        
        # Verificar específicamente el permiso de mantenimiento
        tiene_mantenimiento = permisos.get('mantenimiento', False)
        print(f"\n¿Tiene permiso de mantenimiento? {'✅ SÍ' if tiene_mantenimiento else '❌ NO'}")
        
    except json.JSONDecodeError as e:
        print(f"  ⚠️ Error parseando permisos: {e}")
        print(f"  Permisos raw: {permisos_str}")

print(f"\n{'='*70}\n")

# Consultar usuarios y sus roles
print("\n=== USUARIOS Y SUS ROLES ===\n")
cursor.execute("""
    SELECT u.id, u.documento, u.nombres, u.apellidos, u.id_rol, r.nombre_rol
    FROM usuarios u
    LEFT JOIN roles r ON u.id_rol = r.id
    WHERE u.estado = 'activo'
    ORDER BY u.id
    LIMIT 10
""")

usuarios = cursor.fetchall()

for user in usuarios:
    print(f"{user['documento']:15} | {user['nombres']:20} {user['apellidos']:20} | Rol: {user['nombre_rol']:20} (ID: {user['id_rol']})")

cursor.close()
conn.close()
