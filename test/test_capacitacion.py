#!/usr/bin/env python3
"""
Script de prueba para verificar la creación de capacitaciones
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.database import DatabaseManager

def test_insert():
    """Probar inserción directa"""
    db = DatabaseManager()
    
    try:
        # Datos de prueba
        titulo = "Prueba de Capacitación"
        descripcion = "Esta es una prueba"
        tipo_capacitacion = "taller"
        estado = "programada"
        producto = "Producto de prueba"
        medicion = "Número de pruebas"
        cantidad_meta = 10
        cantidad_actual = 0
        actividad = "Actividad de prueba"
        porcentaje_avance = 0.0
        duracion_horas = 8
        fecha_inicio = "2025-01-20"
        fecha_fin = "2025-01-21"
        
        query = """
            INSERT INTO capacitaciones (
                titulo, descripcion, tipo_capacitacion, producto, medicion,
                cantidad_meta, cantidad_actual, actividad, porcentaje_avance,
                duracion_horas, fecha_inicio, fecha_fin, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        print("Intentando insertar capacitación de prueba...")
        db.ejecutar_comando(query, (
            titulo, descripcion, tipo_capacitacion, producto, medicion,
            cantidad_meta, cantidad_actual, actividad, porcentaje_avance,
            duracion_horas, fecha_inicio, fecha_fin, estado
        ))
        
        print("✅ Inserción exitosa!")
        
        # Verificar
        query_check = "SELECT COUNT(*) as total FROM capacitaciones"
        result = db.ejecutar_query(query_check)
        print(f"Total de capacitaciones en BD: {result[0]['total']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_insert()
