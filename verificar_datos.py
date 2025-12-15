"""
Script para verificar datos en la base de datos y diagnosticar problemas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.utils.database import DatabaseManager

def verificar_datos():
    db = DatabaseManager()
    
    try:
        print("="*60)
        print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
        print("="*60)
        
        # 1. Verificar tabla practicas_laboratorio
        print("\n1️⃣ Verificando tabla practicas_laboratorio...")
        count = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio")
        print(f"   📊 Total de registros: {count['total']}")
        
        if count['total'] > 0:
            # Mostrar algunos registros
            practicas = db.ejecutar_query("""
                SELECT id, codigo, nombre, estado, fecha 
                FROM practicas_laboratorio 
                LIMIT 5
            """)
            print("\n   📋 Primeros 5 registros:")
            for p in practicas:
                print(f"      - ID: {p['id']}, Código: {p['codigo']}, Estado: {p['estado']}")
        else:
            print("   ⚠️  No hay datos en la tabla practicas_laboratorio")
        
        # 2. Verificar estados
        print("\n2️⃣ Verificando distribución de estados...")
        estados = db.ejecutar_query("""
            SELECT estado, COUNT(*) as total 
            FROM practicas_laboratorio 
            GROUP BY estado
        """)
        for e in estados:
            print(f"   - {e['estado']}: {e['total']}")
        
        # 3. Verificar laboratorios
        print("\n3️⃣ Verificando tabla laboratorios...")
        labs = db.obtener_uno("SELECT COUNT(*) as total FROM laboratorios")
        print(f"   📊 Total de laboratorios: {labs['total']}")
        
        # 4. Verificar roles y permisos
        print("\n4️⃣ Verificando roles y permisos...")
        roles = db.ejecutar_query("SELECT id, nombre_rol, permisos FROM roles WHERE id IN (1, 2)")
        for r in roles:
            print(f"   - {r['nombre_rol']} (ID: {r['id']}): {r['permisos']}")
        
        # 5. Probar consulta de estadísticas
        print("\n5️⃣ Probando consulta de estadísticas...")
        try:
            total = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio")
            programadas = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'programada'")
            en_curso = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'en_curso'")
            completadas = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'completada'")
            
            print(f"   ✅ Total: {total['total']}")
            print(f"   ✅ Programadas: {programadas['total']}")
            print(f"   ✅ En curso: {en_curso['total']}")
            print(f"   ✅ Completadas: {completadas['total']}")
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
        
        # 6. Verificar laboratorios más usados
        print("\n6️⃣ Probando consulta de laboratorios más usados...")
        try:
            labs_usados = db.ejecutar_query("""
                SELECT l.nombre, COUNT(p.id) as total_practicas
                FROM practicas_laboratorio p
                JOIN laboratorios l ON p.id_laboratorio = l.id
                WHERE p.estado IN ('completada', 'en_curso')
                GROUP BY l.id, l.nombre
                ORDER BY total_practicas DESC
                LIMIT 5
            """)
            if labs_usados:
                for lab in labs_usados:
                    print(f"   - {lab['nombre']}: {lab['total_practicas']} reservas")
            else:
                print("   ⚠️  No hay datos de laboratorios usados")
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
        
        print("\n" + "="*60)
        print("✅ Diagnóstico completado")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_datos()
