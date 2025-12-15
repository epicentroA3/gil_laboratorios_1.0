import mysql.connector

# Conectar a la base de datos
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='gil_laboratorios'
)

cursor = conn.cursor(dictionary=True)

# Consultar equipo AIRPORDS específicamente
print("\n=== INFORMACIÓN DEL EQUIPO AIRPORDS ===\n")
cursor.execute("""
    SELECT 
        id, 
        nombre, 
        codigo_interno, 
        estado, 
        estado_fisico, 
        fecha_adquisicion, 
        vida_util_anos,
        valor_adquisicion
    FROM equipos 
    WHERE codigo_interno LIKE '%AIRPORD%' OR nombre LIKE '%AIRPORD%'
""")

equipos_airpords = cursor.fetchall()
for e in equipos_airpords:
    print(f"ID: {e['id']:3} | {e['nombre']:40} | Código: {e['codigo_interno']:15} | Estado: {e['estado']:15} | Estado Físico: {e['estado_fisico']:10}")

# Consultar equipos con estado físico malo o regular
print("\n=== TODOS LOS EQUIPOS CON ESTADO FÍSICO MALO O REGULAR ===\n")
cursor.execute("""
    SELECT 
        id, 
        nombre, 
        codigo_interno, 
        estado, 
        estado_fisico, 
        fecha_adquisicion, 
        vida_util_anos,
        valor_adquisicion
    FROM equipos 
    WHERE estado_fisico IN ('malo', 'regular') 
    AND estado != 'dado_baja'
    ORDER BY estado_fisico DESC, nombre
""")

equipos = cursor.fetchall()

for e in equipos:
    print(f"ID: {e['id']:3} | {e['nombre']:40} | Código: {e['codigo_interno']:15} | Estado: {e['estado']:15} | Estado Físico: {e['estado_fisico']:10} | Adquisición: {e['fecha_adquisicion']} | Vida útil: {e['vida_util_anos']} años")

print(f"\n📊 Total equipos con estado malo/regular: {len(equipos)}")

# Consultar historial de mantenimiento de estos equipos
print("\n=== HISTORIAL DE MANTENIMIENTO DE ESTOS EQUIPOS ===\n")
if equipos:
    ids = [e['id'] for e in equipos]
    placeholders = ','.join(['%s'] * len(ids))
    
    cursor.execute(f"""
        SELECT 
            e.nombre as equipo,
            e.estado_fisico,
            COUNT(hm.id) as total_mantenimientos,
            MAX(hm.fecha_fin) as ultimo_mantenimiento,
            AVG(hm.costo_mantenimiento) as costo_promedio
        FROM equipos e
        LEFT JOIN historial_mantenimiento hm ON e.id = hm.id_equipo AND hm.estado = 'completado'
        WHERE e.id IN ({placeholders})
        GROUP BY e.id, e.nombre, e.estado_fisico
        ORDER BY e.estado_fisico DESC
    """, ids)
    
    historial = cursor.fetchall()
    
    for h in historial:
        print(f"Equipo: {h['equipo']:40} | Estado: {h['estado_fisico']:10} | Mantenimientos: {h['total_mantenimientos']:3} | Último: {h['ultimo_mantenimiento']} | Costo promedio: ${h['costo_promedio'] or 0:.2f}")

cursor.close()
conn.close()
