import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='gil_laboratorios'
)

cursor = conn.cursor(dictionary=True)

print("\n=== EJECUTANDO LA MISMA CONSULTA DEL MODELO PREDICTIVO ===\n")

# Esta es la MISMA consulta que usa obtener_datos_entrenamiento()
query = """
    SELECT 
        e.id as equipo_id,
        e.nombre,
        e.codigo_interno,
        e.estado_fisico,
        COALESCE(e.id_categoria, 1) as id_categoria,
        COALESCE(DATEDIFF(CURDATE(), e.fecha_adquisicion), 365) as dias_antiguedad,
        COALESCE(e.vida_util_anos, 5) * 365 as vida_util_dias,
        COALESCE(e.valor_adquisicion, 0) as valor,
        
        -- Historial de mantenimientos (incluir solo completados)
        COUNT(hm.id) as total_mantenimientos,
        COALESCE(AVG(hm.costo_mantenimiento), 0) as costo_promedio,
        COALESCE(AVG(hm.tiempo_inactividad_horas), 0) as inactividad_promedio,
        
        -- Días desde último mantenimiento
        COALESCE(DATEDIFF(CURDATE(), MAX(hm.fecha_fin)), 30) as dias_sin_mantenimiento,
        
        -- Estado actual
        CASE e.estado_fisico 
            WHEN 'excelente' THEN 4
            WHEN 'bueno' THEN 3
            WHEN 'regular' THEN 2
            WHEN 'malo' THEN 1
            ELSE 3
        END as estado_numerico,
        
        -- Préstamos (uso del equipo)
        (SELECT COUNT(*) FROM prestamos p WHERE p.id_equipo = e.id) as total_prestamos,
        
        -- Target: ¿Tuvo mantenimiento correctivo (no preventivo)?
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM historial_mantenimiento hm2
                JOIN tipos_mantenimiento tm ON hm2.id_tipo_mantenimiento = tm.id
                WHERE hm2.id_equipo = e.id 
                AND tm.es_preventivo = 0
                AND hm2.estado = 'completado'
            ) THEN 1
            ELSE 0
        END as tuvo_falla
        
    FROM equipos e
    LEFT JOIN historial_mantenimiento hm ON e.id = hm.id_equipo AND hm.estado = 'completado'
    WHERE e.estado != 'dado_baja'
    GROUP BY e.id, e.id_categoria, e.fecha_adquisicion, e.vida_util_anos, 
             e.valor_adquisicion, e.estado_fisico
    HAVING total_mantenimientos > 0 OR total_prestamos > 0 OR e.estado_fisico IN ('malo', 'regular')
"""

cursor.execute(query)
resultados = cursor.fetchall()

print(f"Total de equipos que cumplen la condición: {len(resultados)}\n")

# Buscar específicamente AIRPORDS
airpords_encontrado = False
for r in resultados:
    if 'AIRPORD' in r['nombre'].upper() or 'AIRPORD' in r['codigo_interno'].upper():
        airpords_encontrado = True
        print(f"✅ AIRPORDS ENCONTRADO:")
        print(f"   ID: {r['equipo_id']}")
        print(f"   Nombre: {r['nombre']}")
        print(f"   Código: {r['codigo_interno']}")
        print(f"   Estado Físico: {r['estado_fisico']}")
        print(f"   Total Mantenimientos: {r['total_mantenimientos']}")
        print(f"   Días sin mantenimiento: {r['dias_sin_mantenimiento']}")
        print(f"   Estado Numérico: {r['estado_numerico']}")
        print(f"   Total Préstamos: {r['total_prestamos']}")
        print(f"   Tuvo Falla: {r['tuvo_falla']}")
        print()

if not airpords_encontrado:
    print("❌ AIRPORDS NO ENCONTRADO en los resultados de la consulta")
    print("\nVerificando si existe en la base de datos...")
    
    cursor.execute("""
        SELECT id, nombre, codigo_interno, estado, estado_fisico
        FROM equipos
        WHERE nombre LIKE '%AIRPORD%' OR codigo_interno LIKE '%AIRPORD%'
    """)
    
    equipo = cursor.fetchone()
    if equipo:
        print(f"\n✅ Equipo existe en BD:")
        print(f"   ID: {equipo['id']}")
        print(f"   Nombre: {equipo['nombre']}")
        print(f"   Código: {equipo['codigo_interno']}")
        print(f"   Estado: {equipo['estado']}")
        print(f"   Estado Físico: {equipo['estado_fisico']}")
        
        # Verificar mantenimientos
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM historial_mantenimiento
            WHERE id_equipo = %s AND estado = 'completado'
        """, (equipo['id'],))
        
        mant = cursor.fetchone()
        print(f"   Mantenimientos completados: {mant['total']}")
        
        # Verificar por qué no aparece en la consulta
        print("\n🔍 Verificando condiciones del HAVING:")
        
        cursor.execute("""
            SELECT 
                COUNT(hm.id) as total_mantenimientos,
                (SELECT COUNT(*) FROM prestamos p WHERE p.id_equipo = %s) as total_prestamos,
                e.estado_fisico
            FROM equipos e
            LEFT JOIN historial_mantenimiento hm ON e.id = hm.id_equipo AND hm.estado = 'completado'
            WHERE e.id = %s
            GROUP BY e.id, e.estado_fisico
        """, (equipo['id'], equipo['id']))
        
        cond = cursor.fetchone()
        print(f"   total_mantenimientos: {cond['total_mantenimientos']}")
        print(f"   total_prestamos: {cond['total_prestamos']}")
        print(f"   estado_fisico: {cond['estado_fisico']}")
        print(f"   ¿Cumple HAVING? {cond['total_mantenimientos'] > 0 or cond['total_prestamos'] > 0 or cond['estado_fisico'] in ['malo', 'regular']}")

print(f"\n📊 Resumen: {len(resultados)} equipos incluidos en el entrenamiento")

cursor.close()
conn.close()
