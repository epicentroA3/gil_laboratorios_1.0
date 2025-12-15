"""
Script para verificar la consistencia entre la BD actual y schema.sql
Compara todas las tablas y sus estructuras
"""
import sys
sys.path.insert(0, '.')

from backend.utils.database import DatabaseManager

db_manager = DatabaseManager()

print("=" * 80)
print("VERIFICACIÓN DE CONSISTENCIA DE BASE DE DATOS")
print("=" * 80)

# Obtener todas las tablas
print("\n📋 Obteniendo lista de tablas...")
query_tablas = "SHOW TABLES"
tablas_result = db_manager.ejecutar_query(query_tablas)

if not tablas_result:
    print("❌ No se pudieron obtener las tablas")
    sys.exit(1)

tablas = [list(t.values())[0] for t in tablas_result]
print(f"✅ Encontradas {len(tablas)} tablas\n")

# Tablas esperadas según schema.sql
tablas_esperadas = [
    'roles',
    'usuarios',
    'laboratorios',
    'categorias_equipos',
    'equipos',
    'prestamos',
    'tipos_mantenimiento',
    'historial_mantenimiento',
    'alertas_mantenimiento',
    'programas_formacion',
    'instructores',
    'practicas_laboratorio',
    'capacitaciones',
    'encuestas',
    'comandos_voz',
    'interacciones_voz',
    'modelos_ia',
    'reconocimientos_imagen',
    'imagenes_entrenamiento',
    'configuracion_sistema',
    'logs_sistema',
    'logs_cambios',
    'password_reset_tokens'
]

# Verificar tablas faltantes o extras
print("🔍 VERIFICACIÓN DE TABLAS:")
print("-" * 80)

tablas_faltantes = set(tablas_esperadas) - set(tablas)
tablas_extras = set(tablas) - set(tablas_esperadas)

if tablas_faltantes:
    print(f"\n⚠️  TABLAS FALTANTES ({len(tablas_faltantes)}):")
    for tabla in sorted(tablas_faltantes):
        print(f"  ❌ {tabla}")
else:
    print("\n✅ Todas las tablas esperadas existen")

if tablas_extras:
    print(f"\n⚠️  TABLAS EXTRAS ({len(tablas_extras)}):")
    for tabla in sorted(tablas_extras):
        print(f"  ℹ️  {tabla}")

# Verificar estructura de tablas críticas
print("\n" + "=" * 80)
print("VERIFICACIÓN DE ESTRUCTURAS CRÍTICAS")
print("=" * 80)

tablas_criticas = {
    'usuarios': ['id', 'documento', 'nombres', 'apellidos', 'email', 'telefono', 'id_rol', 
                 'password_hash', 'fecha_registro', 'ultimo_acceso', 'estado'],
    'capacitaciones': ['id', 'titulo', 'descripcion', 'tipo_capacitacion', 'producto', 'medicion',
                       'cantidad_meta', 'cantidad_actual', 'actividad', 'porcentaje_avance',
                       'duracion_horas', 'fecha_inicio', 'fecha_fin', 'estado', 'id_instructor',
                       'fecha_creacion', 'fecha_actualizacion'],
    'password_reset_tokens': ['id', 'id_usuario', 'token', 'email', 'expira_en', 'usado',
                              'fecha_creacion', 'ip_solicitud'],
    'equipos': ['id', 'codigo_interno', 'codigo_qr', 'nombre', 'marca', 'modelo', 'numero_serie',
                'id_categoria', 'id_laboratorio', 'estado', 'estado_fisico'],
    'prestamos': ['id', 'codigo', 'id_equipo', 'id_usuario_solicitante', 'id_usuario_autorizador',
                  'fecha', 'fecha_devolucion_programada', 'estado']
}

for tabla, campos_esperados in tablas_criticas.items():
    print(f"\n📊 Tabla: {tabla}")
    print("-" * 80)
    
    if tabla not in tablas:
        print(f"  ❌ TABLA NO EXISTE")
        continue
    
    # Obtener estructura actual
    desc_query = f"DESCRIBE {tabla}"
    try:
        estructura = db_manager.ejecutar_query(desc_query)
        campos_actuales = [campo['Field'] for campo in estructura]
        
        # Comparar campos
        campos_faltantes = set(campos_esperados) - set(campos_actuales)
        campos_extras = set(campos_actuales) - set(campos_esperados)
        
        if not campos_faltantes and not campos_extras:
            print(f"  ✅ Estructura correcta ({len(campos_actuales)} campos)")
        else:
            if campos_faltantes:
                print(f"  ⚠️  Campos faltantes: {', '.join(campos_faltantes)}")
            if campos_extras:
                print(f"  ℹ️  Campos extras: {', '.join(campos_extras)}")
        
        # Mostrar estructura completa
        print(f"\n  Campos actuales:")
        for campo in estructura:
            tipo = campo['Type']
            null = "NULL" if campo['Null'] == 'YES' else "NOT NULL"
            key = f" [{campo['Key']}]" if campo['Key'] else ""
            default = f" DEFAULT {campo['Default']}" if campo['Default'] else ""
            print(f"    • {campo['Field']}: {tipo} {null}{key}{default}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Contar registros en tablas principales
print("\n" + "=" * 80)
print("CONTEO DE REGISTROS")
print("=" * 80)

tablas_conteo = ['usuarios', 'roles', 'equipos', 'prestamos', 'capacitaciones', 
                 'laboratorios', 'password_reset_tokens']

for tabla in tablas_conteo:
    if tabla in tablas:
        try:
            count_query = f"SELECT COUNT(*) as total FROM {tabla}"
            resultado = db_manager.ejecutar_query(count_query)
            total = resultado[0]['total'] if resultado else 0
            print(f"  {tabla:30} {total:>5} registros")
        except Exception as e:
            print(f"  {tabla:30} ❌ Error: {e}")

# Verificar foreign keys de capacitaciones
print("\n" + "=" * 80)
print("VERIFICACIÓN DE FOREIGN KEYS - CAPACITACIONES")
print("=" * 80)

if 'capacitaciones' in tablas:
    try:
        fk_query = """
            SELECT 
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'gil_laboratorios'
            AND TABLE_NAME = 'capacitaciones'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        fks = db_manager.ejecutar_query(fk_query)
        
        if fks:
            print("✅ Foreign keys encontradas:")
            for fk in fks:
                print(f"  • {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
        else:
            print("⚠️  No se encontraron foreign keys")
    except Exception as e:
        print(f"❌ Error verificando FKs: {e}")

# Verificar índices de capacitaciones
print("\n" + "=" * 80)
print("VERIFICACIÓN DE ÍNDICES - CAPACITACIONES")
print("=" * 80)

if 'capacitaciones' in tablas:
    try:
        idx_query = "SHOW INDEX FROM capacitaciones"
        indices = db_manager.ejecutar_query(idx_query)
        
        if indices:
            indices_unicos = {}
            for idx in indices:
                nombre = idx['Key_name']
                if nombre not in indices_unicos:
                    indices_unicos[nombre] = []
                indices_unicos[nombre].append(idx['Column_name'])
            
            print("✅ Índices encontrados:")
            for nombre, columnas in indices_unicos.items():
                cols = ', '.join(columnas)
                print(f"  • {nombre}: ({cols})")
        else:
            print("⚠️  No se encontraron índices")
    except Exception as e:
        print(f"❌ Error verificando índices: {e}")

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
