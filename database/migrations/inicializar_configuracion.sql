-- =========================================================
-- Script para inicializar configuraciones del sistema
-- Centro Minero SENA - Sistema GIL
-- =========================================================

USE gil_laboratorios;

-- Insertar configuraciones por defecto
INSERT INTO configuracion_sistema (clave_config, valor_config, descripcion_config, tipo_config) VALUES
-- Configuraciones Generales
('SISTEMA_NOMBRE', 'Sistema GIL - Centro Minero', 'Nombre del sistema', 'texto'),
('SISTEMA_VERSION', '1.0.0', 'Versión actual del sistema', 'texto'),
('SISTEMA_MANTENIMIENTO', 'false', 'Modo mantenimiento activado', 'booleano'),

-- Configuraciones de Sesión
('SESION_TIMEOUT', '3600', 'Tiempo de sesión en segundos (1 hora)', 'numero'),
('SESION_MAX_INTENTOS', '5', 'Máximo de intentos de login fallidos', 'numero'),
('SESION_BLOQUEO_MINUTOS', '15', 'Minutos de bloqueo tras intentos fallidos', 'numero'),

-- Configuraciones de Seguridad
('PASSWORD_MIN_LENGTH', '8', 'Longitud mínima de contraseña', 'numero'),
('PASSWORD_REQUIRE_UPPERCASE', 'true', 'Requiere mayúsculas en contraseña', 'booleano'),
('PASSWORD_REQUIRE_LOWERCASE', 'true', 'Requiere minúsculas en contraseña', 'booleano'),
('PASSWORD_REQUIRE_NUMBER', 'true', 'Requiere números en contraseña', 'booleano'),
('PASSWORD_REQUIRE_SPECIAL', 'true', 'Requiere caracteres especiales en contraseña', 'booleano'),

-- Configuraciones de Backups
('BACKUP_AUTO_ENABLED', 'true', 'Backups automáticos habilitados', 'booleano'),
('BACKUP_FREQUENCY_HOURS', '24', 'Frecuencia de backups en horas', 'numero'),
('BACKUP_RETENTION_DAYS', '30', 'Días de retención de backups', 'numero'),
('BACKUP_MAX_FILES', '10', 'Número máximo de archivos de backup', 'numero'),

-- Configuraciones de Préstamos
('PRESTAMO_DURACION_MAX_DIAS', '7', 'Duración máxima de préstamo en días', 'numero'),
('PRESTAMO_RENOVACIONES_MAX', '2', 'Número máximo de renovaciones', 'numero'),
('PRESTAMO_MULTA_DIA', '5000', 'Multa por día de retraso (COP)', 'numero'),

-- Configuraciones de Reservas
('RESERVA_ANTICIPACION_MAX_DIAS', '30', 'Días máximos de anticipación para reservas', 'numero'),
('RESERVA_DURACION_MAX_HORAS', '4', 'Duración máxima de reserva en horas', 'numero'),
('RESERVA_CANCELACION_HORAS', '24', 'Horas mínimas para cancelar reserva', 'numero'),

-- Configuraciones de Mantenimiento
('MANTENIMIENTO_ALERTA_DIAS', '7', 'Días de anticipación para alertas de mantenimiento', 'numero'),
('MANTENIMIENTO_PREVENTIVO_MESES', '6', 'Meses entre mantenimientos preventivos', 'numero'),

-- Configuraciones de Notificaciones
('NOTIFICACIONES_EMAIL_ENABLED', 'false', 'Notificaciones por email habilitadas', 'booleano'),
('NOTIFICACIONES_SMS_ENABLED', 'false', 'Notificaciones por SMS habilitadas', 'booleano'),
('NOTIFICACIONES_PRESTAMOS_VENCIDOS', 'true', 'Notificar préstamos vencidos', 'booleano'),
('NOTIFICACIONES_MANTENIMIENTO_PROXIMO', 'true', 'Notificar mantenimientos próximos', 'booleano'),

-- Configuraciones de IA
('IA_RECONOCIMIENTO_ENABLED', 'true', 'Reconocimiento de equipos por IA habilitado', 'booleano'),
('IA_CONFIDENCE_THRESHOLD', '0.85', 'Umbral de confianza para IA (0-1)', 'decimal'),
('IA_MAX_IMAGE_SIZE_MB', '5', 'Tamaño máximo de imagen en MB', 'numero'),

-- Configuraciones de Asistente de Voz
('LUCIA_ENABLED', 'true', 'Asistente de voz LUCIA habilitado', 'booleano'),
('LUCIA_LANGUAGE', 'es-CO', 'Idioma del asistente de voz', 'texto'),
('LUCIA_TIMEOUT_SECONDS', '5', 'Timeout de reconocimiento de voz en segundos', 'numero'),

-- Configuraciones de Reportes
('REPORTES_FORMATO_DEFECTO', 'PDF', 'Formato por defecto de reportes', 'texto'),
('REPORTES_LOGO_ENABLED', 'true', 'Incluir logo en reportes', 'booleano'),

-- Configuraciones de Interfaz
('UI_THEME', 'light', 'Tema de la interfaz (light/dark)', 'texto'),
('UI_ITEMS_PER_PAGE', '20', 'Elementos por página en tablas', 'numero'),
('UI_DATE_FORMAT', 'DD/MM/YYYY', 'Formato de fecha', 'texto'),
('UI_TIME_FORMAT', 'HH:mm', 'Formato de hora', 'texto')

ON DUPLICATE KEY UPDATE 
    valor_config = VALUES(valor_config),
    descripcion_config = VALUES(descripcion_config),
    tipo_config = VALUES(tipo_config);

-- Verificar configuraciones insertadas
SELECT COUNT(*) as total_configuraciones FROM configuracion_sistema;

-- Mostrar todas las configuraciones
SELECT clave_config, valor_config, descripcion_config, tipo_config 
FROM configuracion_sistema 
ORDER BY clave_config;
