"""
Módulo de Base de Datos - Sistema GIL
Centro Minero de Sogamoso - SENA

Archivos SQL disponibles:
- schema.sql: Estructura de tablas, vistas e índices
- data.sql: Datos de prueba
- triggers.sql: Triggers, procedimientos almacenados y eventos
"""

# Instrucciones de inicialización de la base de datos
INIT_INSTRUCTIONS = """
Para inicializar la base de datos MySQL, ejecutar en orden:

1. Crear estructura:
   mysql -u root -p < database/schema.sql

2. Insertar datos de prueba:
   mysql -u root -p gil_laboratorios < database/data.sql

3. Crear triggers y procedimientos:
   mysql -u root -p gil_laboratorios < database/triggers.sql

O ejecutar todo desde Python:
   from config import DatabaseManager
   db = DatabaseManager()
   db.conectar()
"""
