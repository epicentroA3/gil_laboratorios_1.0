#!/usr/bin/env python3
"""
Script para inicializar capacitaciones del programa formativo en IA
Centro Minero SENA - Sistema GIL
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.database import DatabaseManager

def inicializar_capacitaciones():
    """Ejecutar script SQL de actualización de capacitaciones"""
    
    print("=" * 60)
    print("INICIALIZANDO PROGRAMA FORMATIVO EN IA")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        # Leer el archivo SQL
        sql_file = os.path.join(os.path.dirname(__file__), 'database', 'migrations', 'actualizar_capacitaciones.sql')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir en comandos individuales
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        print(f"\n📝 Ejecutando {len(commands)} comandos SQL...\n")
        
        for i, command in enumerate(commands, 1):
            if command.upper().startswith('USE'):
                continue
            
            try:
                if command.upper().startswith('SELECT'):
                    result = db.ejecutar_query(command)
                    if result:
                        print(f"  ✓ Comando {i}: {len(result)} resultados")
                        for row in result:
                            print(f"    {row}")
                else:
                    db.ejecutar_comando(command)
                    print(f"  ✓ Comando {i}: Ejecutado")
            except Exception as e:
                if 'Duplicate column name' in str(e) or 'already exists' in str(e):
                    print(f"  ↻ Comando {i}: Ya existe (omitido)")
                else:
                    print(f"  ⚠ Comando {i}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ PROGRAMA FORMATIVO INICIALIZADO")
        print("=" * 60)
        
        # Mostrar resumen
        query_resumen = """
            SELECT 
                tipo_capacitacion as tipo,
                COUNT(*) as total,
                SUM(cantidad_actual) as avance,
                SUM(cantidad_meta) as meta
            FROM capacitaciones
            GROUP BY tipo_capacitacion
        """
        
        resumen = db.ejecutar_query(query_resumen)
        
        print("\n📊 RESUMEN POR TIPO:")
        for row in resumen:
            print(f"  - {row['tipo']}: {row['total']} capacitaciones ({row['avance']}/{row['meta']})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n🚀 Iniciando script de capacitaciones...\n")
    
    if inicializar_capacitaciones():
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso completado con errores")
        sys.exit(1)
