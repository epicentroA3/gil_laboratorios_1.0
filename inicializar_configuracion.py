#!/usr/bin/env python3
"""
Script para inicializar configuraciones del sistema
Centro Minero SENA - Sistema GIL
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.database import DatabaseManager

def inicializar_configuraciones():
    """Insertar configuraciones por defecto en la base de datos"""
    
    print("=" * 60)
    print("INICIALIZANDO CONFIGURACIONES DEL SISTEMA")
    print("=" * 60)
    
    db = DatabaseManager()
    
    configuraciones = [
        # Configuraciones Generales
        ('SISTEMA_NOMBRE', 'Sistema GIL - Centro Minero', 'Nombre del sistema', 'string'),
        ('SISTEMA_VERSION', '1.0.0', 'Versión actual del sistema', 'string'),
        ('SISTEMA_MANTENIMIENTO', 'false', 'Modo mantenimiento activado', 'boolean'),
        
        # Configuraciones de Sesión
        ('SESION_TIMEOUT', '3600', 'Tiempo de sesión en segundos (1 hora)', 'integer'),
        ('SESION_MAX_INTENTOS', '5', 'Máximo de intentos de login fallidos', 'integer'),
        ('SESION_BLOQUEO_MINUTOS', '15', 'Minutos de bloqueo tras intentos fallidos', 'integer'),
        
        # Configuraciones de Seguridad
        ('PASSWORD_MIN_LENGTH', '8', 'Longitud mínima de contraseña', 'integer'),
        ('PASSWORD_REQUIRE_UPPERCASE', 'true', 'Requiere mayúsculas en contraseña', 'boolean'),
        ('PASSWORD_REQUIRE_LOWERCASE', 'true', 'Requiere minúsculas en contraseña', 'boolean'),
        ('PASSWORD_REQUIRE_NUMBER', 'true', 'Requiere números en contraseña', 'boolean'),
        ('PASSWORD_REQUIRE_SPECIAL', 'true', 'Requiere caracteres especiales en contraseña', 'boolean'),
        
        # Configuraciones de Backups
        ('BACKUP_AUTO_ENABLED', 'true', 'Backups automáticos habilitados', 'boolean'),
        ('BACKUP_FREQUENCY_HOURS', '24', 'Frecuencia de backups en horas', 'integer'),
        ('BACKUP_RETENTION_DAYS', '30', 'Días de retención de backups', 'integer'),
        ('BACKUP_MAX_FILES', '10', 'Número máximo de archivos de backup', 'integer'),
        
        # Configuraciones de Préstamos
        ('PRESTAMO_DURACION_MAX_DIAS', '7', 'Duración máxima de préstamo en días', 'integer'),
        ('PRESTAMO_RENOVACIONES_MAX', '2', 'Número máximo de renovaciones', 'integer'),
        ('PRESTAMO_MULTA_DIA', '5000', 'Multa por día de retraso (COP)', 'integer'),
        
        # Configuraciones de Reservas
        ('RESERVA_ANTICIPACION_MAX_DIAS', '30', 'Días máximos de anticipación para reservas', 'integer'),
        ('RESERVA_DURACION_MAX_HORAS', '4', 'Duración máxima de reserva en horas', 'integer'),
        ('RESERVA_CANCELACION_HORAS', '24', 'Horas mínimas para cancelar reserva', 'integer'),
        
        # Configuraciones de Mantenimiento
        ('MANTENIMIENTO_ALERTA_DIAS', '7', 'Días de anticipación para alertas de mantenimiento', 'integer'),
        ('MANTENIMIENTO_PREVENTIVO_MESES', '6', 'Meses entre mantenimientos preventivos', 'integer'),
        
        # Configuraciones de Notificaciones
        ('NOTIFICACIONES_EMAIL_ENABLED', 'false', 'Notificaciones por email habilitadas', 'boolean'),
        ('NOTIFICACIONES_SMS_ENABLED', 'false', 'Notificaciones por SMS habilitadas', 'boolean'),
        ('NOTIFICACIONES_PRESTAMOS_VENCIDOS', 'true', 'Notificar préstamos vencidos', 'boolean'),
        ('NOTIFICACIONES_MANTENIMIENTO_PROXIMO', 'true', 'Notificar mantenimientos próximos', 'boolean'),
        
        # Configuraciones de IA
        ('IA_RECONOCIMIENTO_ENABLED', 'true', 'Reconocimiento de equipos por IA habilitado', 'boolean'),
        ('IA_CONFIDENCE_THRESHOLD', '0.85', 'Umbral de confianza para IA (0-1)', 'string'),
        ('IA_MAX_IMAGE_SIZE_MB', '5', 'Tamaño máximo de imagen en MB', 'integer'),
        
        # Configuraciones de Asistente de Voz
        ('LUCIA_ENABLED', 'true', 'Asistente de voz LUCIA habilitado', 'boolean'),
        ('LUCIA_LANGUAGE', 'es-CO', 'Idioma del asistente de voz', 'string'),
        ('LUCIA_TIMEOUT_SECONDS', '5', 'Timeout de reconocimiento de voz en segundos', 'integer'),
        
        # Configuraciones de Reportes
        ('REPORTES_FORMATO_DEFECTO', 'PDF', 'Formato por defecto de reportes', 'string'),
        ('REPORTES_LOGO_ENABLED', 'true', 'Incluir logo en reportes', 'boolean'),
        
        # Configuraciones de Interfaz
        ('UI_THEME', 'light', 'Tema de la interfaz (light/dark)', 'string'),
        ('UI_ITEMS_PER_PAGE', '20', 'Elementos por página en tablas', 'integer'),
        ('UI_DATE_FORMAT', 'DD/MM/YYYY', 'Formato de fecha', 'string'),
        ('UI_TIME_FORMAT', 'HH:mm', 'Formato de hora', 'string')
    ]
    
    try:
        insertadas = 0
        actualizadas = 0
        
        for clave, valor, descripcion, tipo in configuraciones:
            # Verificar si existe
            query_check = "SELECT id FROM configuracion_sistema WHERE clave_config = %s"
            existe = db.obtener_uno(query_check, (clave,))
            
            if existe:
                # Actualizar
                query_update = """
                    UPDATE configuracion_sistema 
                    SET valor_config = %s, descripcion = %s, tipo_dato = %s
                    WHERE clave_config = %s
                """
                db.ejecutar_comando(query_update, (valor, descripcion, tipo, clave))
                actualizadas += 1
                print(f"  ↻ Actualizada: {clave}")
            else:
                # Insertar
                query_insert = """
                    INSERT INTO configuracion_sistema (clave_config, valor_config, descripcion, tipo_dato)
                    VALUES (%s, %s, %s, %s)
                """
                db.ejecutar_comando(query_insert, (clave, valor, descripcion, tipo))
                insertadas += 1
                print(f"  ✓ Insertada: {clave}")
        
        print("\n" + "=" * 60)
        print(f"✅ Configuraciones insertadas: {insertadas}")
        print(f"↻  Configuraciones actualizadas: {actualizadas}")
        print(f"📊 Total: {insertadas + actualizadas}")
        print("=" * 60)
        
        # Verificar total
        query_count = "SELECT COUNT(*) as total FROM configuracion_sistema"
        result = db.obtener_uno(query_count)
        print(f"\n📋 Total de configuraciones en la base de datos: {result['total']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n🚀 Iniciando script de configuración...\n")
    
    if inicializar_configuraciones():
        print("\n✅ Proceso completado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Proceso completado con errores")
        sys.exit(1)
