-- =========================================================
-- MIGRACIÓN: Actualizar tabla historial_mantenimiento
-- Fecha: 2025-12-14
-- Descripción: Agregar campos para flujo de 2 pasos (iniciar/completar)
-- =========================================================

-- Agregar campo estado del mantenimiento
ALTER TABLE historial_mantenimiento 
ADD COLUMN IF NOT EXISTS estado ENUM('en_proceso', 'completado', 'cancelado') DEFAULT 'completado' AFTER id_tipo_mantenimiento;

-- Renombrar fecha_mantenimiento a fecha_inicio (si existe)
-- Nota: En MySQL, primero verificamos si la columna existe
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'historial_mantenimiento' 
    AND COLUMN_NAME = 'fecha_mantenimiento'
);

-- Si existe fecha_mantenimiento, renombrarla a fecha_inicio
SET @sql = IF(@column_exists > 0, 
    'ALTER TABLE historial_mantenimiento CHANGE COLUMN fecha_mantenimiento fecha_inicio DATETIME NOT NULL',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar campo fecha_fin si no existe
ALTER TABLE historial_mantenimiento 
ADD COLUMN IF NOT EXISTS fecha_fin DATETIME NULL AFTER fecha_inicio;

-- Actualizar registros existentes: marcar como completados con fecha_fin = fecha_inicio
UPDATE historial_mantenimiento 
SET estado = 'completado', 
    fecha_fin = fecha_inicio 
WHERE estado IS NULL OR fecha_fin IS NULL;

-- Agregar índice para el campo estado
CREATE INDEX IF NOT EXISTS idx_estado ON historial_mantenimiento(estado);

-- =========================================================
-- VERIFICACIÓN
-- =========================================================
SELECT 
    'Migración completada' as mensaje,
    COUNT(*) as total_registros,
    SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as completados,
    SUM(CASE WHEN estado = 'en_proceso' THEN 1 ELSE 0 END) as en_proceso
FROM historial_mantenimiento;
