import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='gil_laboratorios'
)

cursor = conn.cursor(dictionary=True)

# Lista de equipos que aparecen en la imagen
equipos_detectados = [
    'MICRO-001',
    'MICRO-003',
    'MICRO-004',
    'BAL-001',
    'BAL-002'
]

print("\n=== VERIFICACIÓN DE EQUIPOS DETECTADOS COMO CRÍTICO ===\n")

for codigo in equipos_detectados:
    cursor.execute("""
        SELECT 
            id,
            nombre,
            codigo_interno,
            estado,
            estado_fisico,
            fecha_adquisicion,
            vida_util_anos
        FROM equipos
        WHERE codigo_interno = %s
    """, (codigo,))
    
    equipo = cursor.fetchone()
    
    if equipo:
        print(f"\n{'='*70}")
        print(f"Código: {equipo['codigo_interno']}")
        print(f"Nombre: {equipo['nombre']}")
        print(f"Estado: {equipo['estado']}")
        print(f"Estado Físico: {equipo['estado_fisico']}")
        print(f"Fecha Adquisición: {equipo['fecha_adquisicion']}")
        print(f"Vida Útil: {equipo['vida_util_anos']} años")
        
        # Verificar mantenimientos
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM historial_mantenimiento
            WHERE id_equipo = %s AND estado = 'completado'
        """, (equipo['id'],))
        
        mant = cursor.fetchone()
        print(f"Mantenimientos completados: {mant['total']}")
        
        # Verificar si debería ser CRÍTICO
        es_critico = equipo['estado_fisico'] in ['malo', 'regular']
        print(f"¿Debería ser CRÍTICO? {'SÍ' if es_critico else 'NO'} (estado físico: {equipo['estado_fisico']})")

cursor.close()
conn.close()
