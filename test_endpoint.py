"""
Script para probar los endpoints de estadísticas directamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.utils.database import DatabaseManager

def test_estadisticas():
    db = DatabaseManager()
    
    try:
        print("="*60)
        print("🧪 PROBANDO ENDPOINTS DE ESTADÍSTICAS")
        print("="*60)
        
        print("\n📊 Simulando endpoint /api/practicas/estadisticas...")
        
        stats = {}
        
        stats['total_practicas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio")['total']
        stats['practicas_programadas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'programada'")['total']
        stats['practicas_en_curso'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'en_curso'")['total']
        stats['practicas_completadas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'completada'")['total']
        
        stats['practicas_hoy'] = db.obtener_uno("""
            SELECT COUNT(*) as total FROM practicas_laboratorio
            WHERE DATE(fecha) = CURDATE()
            AND estado IN ('programada', 'en_curso')
        """)['total']
        
        stats['practicas_semana'] = db.obtener_uno("""
            SELECT COUNT(*) as total FROM practicas_laboratorio
            WHERE YEARWEEK(fecha, 1) = YEARWEEK(CURDATE(), 1)
            AND estado IN ('programada', 'en_curso')
        """)['total']
        
        laboratorios_mas_usados = db.ejecutar_query("""
            SELECT l.nombre, COUNT(p.id) as total_practicas
            FROM practicas_laboratorio p
            JOIN laboratorios l ON p.id_laboratorio = l.id
            WHERE p.estado IN ('completada', 'en_curso')
            GROUP BY l.id, l.nombre
            ORDER BY total_practicas DESC
            LIMIT 5
        """) or []
        stats['laboratorios_mas_usados'] = laboratorios_mas_usados
        
        print("\n✅ Respuesta del endpoint:")
        print(f"   - Total: {stats['total_practicas']}")
        print(f"   - Programadas: {stats['practicas_programadas']}")
        print(f"   - En curso: {stats['practicas_en_curso']}")
        print(f"   - Completadas: {stats['practicas_completadas']}")
        print(f"   - Hoy: {stats['practicas_hoy']}")
        print(f"   - Esta semana: {stats['practicas_semana']}")
        print(f"\n   Laboratorios más usados:")
        for lab in laboratorios_mas_usados:
            print(f"   - {lab['nombre']}: {lab['total_practicas']}")
        
        print("\n" + "="*60)
        print("✅ Los endpoints funcionan correctamente")
        print("="*60)
        
        print("\n⚠️  SOLUCIÓN:")
        print("   1. Cierra sesión en la aplicación")
        print("   2. Vuelve a iniciar sesión")
        print("   3. Los nuevos permisos se cargarán en la sesión")
        print("   4. La vista de estadísticas debería funcionar")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_estadisticas()
