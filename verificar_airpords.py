import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='gil_laboratorios'
)

cursor = conn.cursor(dictionary=True)

# Buscar equipo AIRPORDS
print("\n=== EQUIPO AIRPORDS ===\n")
cursor.execute("""
    SELECT id, nombre, codigo_interno, estado, estado_fisico
    FROM equipos 
    WHERE nombre LIKE '%AIRPORD%'
""")
equipo = cursor.fetchone()

if equipo:
    print(f"ID: {equipo['id']}")
    print(f"Nombre: {equipo['nombre']}")
    print(f"Código: {equipo['codigo_interno']}")
    print(f"Estado: {equipo['estado']}")
    print(f"Estado Físico: {equipo['estado_fisico']}")
    
    # Contar mantenimientos completados
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM historial_mantenimiento
        WHERE id_equipo = %s AND estado = 'completado'
    """, (equipo['id'],))
    
    resultado = cursor.fetchone()
    print(f"\nMantenimientos completados: {resultado['total']}")
    
    # Mostrar los mantenimientos
    cursor.execute("""
        SELECT id, fecha_inicio, fecha_fin, estado, estado_post_mantenimiento
        FROM historial_mantenimiento
        WHERE id_equipo = %s
        ORDER BY fecha_inicio DESC
    """, (equipo['id'],))
    
    mantenimientos = cursor.fetchall()
    print(f"\n=== HISTORIAL DE MANTENIMIENTOS ===\n")
    for m in mantenimientos:
        print(f"ID: {m['id']} | Inicio: {m['fecha_inicio']} | Fin: {m['fecha_fin']} | Estado: {m['estado']} | Estado Post: {m['estado_post_mantenimiento']}")
else:
    print("No se encontró el equipo AIRPORDS")

cursor.close()
conn.close()
