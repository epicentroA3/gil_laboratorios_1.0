-- =========================================================
-- Script para asegurar que solo el Administrador tenga permiso de backups
-- Centro Minero SENA - Sistema GIL
-- =========================================================

USE gil_laboratorios;

-- Verificar permisos actuales
SELECT id, nombre_rol, permisos FROM roles ORDER BY id;

-- Actualizar Administrador (id=1) - Incluir permiso de backups
UPDATE roles 
SET permisos = '{"all": true, "usuarios": true, "roles": true, "programas": true, "equipos": true, "laboratorios": true, "practicas": true, "reservas": true, "prestamos": true, "reportes": true, "mantenimiento": true, "capacitaciones": true, "reconocimiento": true, "ia_visual": true, "backups": true, "configuracion": true, "ayuda": true}'
WHERE id = 1;

-- Verificar que otros roles NO tengan permiso de backups
-- Los demás roles mantienen sus permisos actuales SIN backups
UPDATE roles 
SET permisos = '{"equipos": true, "laboratorios_ver": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 2;

UPDATE roles 
SET permisos = '{"equipos": true, "reservas": true, "mantenimiento": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 3;

UPDATE roles 
SET permisos = '{"equipos_ver": true, "reservas_propias": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 4;

UPDATE roles 
SET permisos = '{"equipos_ver": true, "laboratorios_ver": true, "reservas_ver": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 5;

-- Verificar resultado final
SELECT 
    id,
    nombre_rol,
    permisos
FROM roles
ORDER BY id;

-- Crear log de la actualización
INSERT INTO logs_sistema (modulo, nivel_log, mensaje, ip_address)
VALUES ('sistema', 'INFO', 'Permisos de backups actualizados - Solo Administrador tiene acceso', '127.0.0.1');
