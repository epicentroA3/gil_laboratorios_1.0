-- =========================================================
-- Script para actualizar permisos de roles existentes
-- Ejecutar este script para actualizar los permisos en la BD
-- =========================================================

-- Actualizar Administrador (id=1)
UPDATE roles SET permisos = '{"all": true, "usuarios": true, "roles": true, "programas": true, "equipos": true, "laboratorios": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento": true, "capacitaciones": true, "reconocimiento": true, "ia_visual": true, "backups": true, "configuracion": true, "ayuda": true}'
WHERE id = 1 OR nombre_rol = 'Administrador';

-- Actualizar Instructor (id=2)
UPDATE roles SET permisos = '{"equipos": true, "laboratorios_ver": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 2 OR nombre_rol = 'Instructor';

-- Actualizar Técnico Laboratorio (id=3)
UPDATE roles SET permisos = '{"equipos": true, "reservas": true, "mantenimiento": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 3 OR nombre_rol = 'Técnico Laboratorio';

-- Actualizar Aprendiz (id=4)
UPDATE roles SET permisos = '{"equipos_ver": true, "reservas_propias": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 4 OR nombre_rol = 'Aprendiz';

-- Actualizar Coordinador (id=5)
UPDATE roles SET permisos = '{"equipos_ver": true, "laboratorios_ver": true, "reservas_ver": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'
WHERE id = 5 OR nombre_rol = 'Coordinador';

-- Verificar los cambios
SELECT id, nombre_rol, permisos FROM roles ORDER BY id;
