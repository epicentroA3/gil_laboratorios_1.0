-- =========================================================
-- GIL LABORATORIOS - TRIGGERS Y PROCEDIMIENTOS
-- Sistema de Gestión Integral de Laboratorios SENA
-- Ejecutar después de schema.sql y data.sql
-- =========================================================

USE gil_laboratorios;

DELIMITER //

-- =========================================================
-- TRIGGER: Actualizar estado de equipo al crear préstamo
-- =========================================================
DROP TRIGGER IF EXISTS tr_prestamo_actualizar_equipo//
CREATE TRIGGER tr_prestamo_actualizar_equipo
AFTER INSERT ON prestamos
FOR EACH ROW
BEGIN
    IF NEW.estado = 'activo' OR NEW.estado = 'aprobado' THEN
        UPDATE equipos SET estado = 'prestado' WHERE id = NEW.id_equipo;
    END IF;
END//

-- =========================================================
-- TRIGGER: Restaurar estado de equipo al devolver
-- =========================================================
DROP TRIGGER IF EXISTS tr_devolucion_restaurar_equipo//
CREATE TRIGGER tr_devolucion_restaurar_equipo
AFTER UPDATE ON prestamos
FOR EACH ROW
BEGIN
    IF NEW.estado = 'devuelto' AND OLD.estado != 'devuelto' THEN
        UPDATE equipos SET estado = 'disponible' WHERE id = NEW.id_equipo;
    END IF;
END//

-- =========================================================
-- TRIGGER: Registrar log al crear usuario
-- =========================================================
DROP TRIGGER IF EXISTS tr_log_crear_usuario//
CREATE TRIGGER tr_log_crear_usuario
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario)
    VALUES ('usuarios', 'INFO', CONCAT('Usuario creado: ', NEW.documento, ' - ', NEW.nombres, ' ', NEW.apellidos), NEW.id);
END//

-- =========================================================
-- TRIGGER: Registrar log al modificar equipo
-- =========================================================
DROP TRIGGER IF EXISTS tr_log_modificar_equipo//
CREATE TRIGGER tr_log_modificar_equipo
AFTER UPDATE ON equipos
FOR EACH ROW
BEGIN
    IF OLD.estado != NEW.estado THEN
        INSERT INTO logs_sistema (modulo, nivel_log, mensaje)
        VALUES ('equipos', 'INFO', CONCAT('Equipo ', NEW.codigo_interno, ' cambió estado: ', OLD.estado, ' -> ', NEW.estado));
    END IF;
END//

-- =========================================================
-- TRIGGER: Crear alerta automática de mantenimiento
-- =========================================================
DROP TRIGGER IF EXISTS tr_crear_alerta_mantenimiento//
CREATE TRIGGER tr_crear_alerta_mantenimiento
AFTER INSERT ON historial_mantenimiento
FOR EACH ROW
BEGIN
    -- Si hay próxima fecha de mantenimiento, crear alerta
    IF NEW.proxima_fecha_mantenimiento IS NOT NULL THEN
        INSERT INTO alertas_mantenimiento (id_equipo, tipo_alerta, descripcion_alerta, fecha_limite, prioridad, estado_alerta, asignado_a)
        VALUES (
            NEW.id_equipo,
            'mantenimiento_programado',
            CONCAT('Próximo mantenimiento programado para equipo'),
            NEW.proxima_fecha_mantenimiento,
            'media',
            'pendiente',
            NEW.tecnico_responsable_id
        );
    END IF;
END//

-- =========================================================
-- TRIGGER: Actualizar último acceso de usuario
-- =========================================================
DROP TRIGGER IF EXISTS tr_actualizar_ultimo_acceso//
CREATE TRIGGER tr_actualizar_ultimo_acceso
BEFORE UPDATE ON usuarios
FOR EACH ROW
BEGIN
    IF NEW.ultimo_acceso != OLD.ultimo_acceso OR (NEW.ultimo_acceso IS NOT NULL AND OLD.ultimo_acceso IS NULL) THEN
        SET NEW.ultimo_acceso = CURRENT_TIMESTAMP;
    END IF;
END//

-- =========================================================
-- PROCEDIMIENTO: Obtener estadísticas del dashboard
-- =========================================================
DROP PROCEDURE IF EXISTS sp_obtener_estadisticas_dashboard//
CREATE PROCEDURE sp_obtener_estadisticas_dashboard()
BEGIN
    SELECT 
        (SELECT COUNT(*) FROM equipos WHERE estado = 'disponible') AS equipos_disponibles,
        (SELECT COUNT(*) FROM equipos WHERE estado = 'prestado') AS equipos_prestados,
        (SELECT COUNT(*) FROM equipos WHERE estado = 'mantenimiento') AS equipos_mantenimiento,
        (SELECT COUNT(*) FROM prestamos WHERE estado = 'activo') AS prestamos_activos,
        (SELECT COUNT(*) FROM alertas_mantenimiento WHERE estado_alerta = 'pendiente') AS alertas_pendientes,
        (SELECT COUNT(*) FROM practicas_laboratorio WHERE fecha >= CURDATE() AND estado = 'programada') AS practicas_programadas,
        (SELECT COUNT(*) FROM usuarios WHERE estado = 'activo') AS usuarios_activos,
        (SELECT COUNT(*) FROM laboratorios WHERE estado = 'disponible') AS laboratorios_disponibles;
END//

-- =========================================================
-- PROCEDIMIENTO: Buscar equipos disponibles por categoría
-- =========================================================
DROP PROCEDURE IF EXISTS sp_buscar_equipos_disponibles//
CREATE PROCEDURE sp_buscar_equipos_disponibles(
    IN p_categoria_id INT,
    IN p_laboratorio_id INT
)
BEGIN
    SELECT 
        e.id,
        e.codigo_interno,
        e.nombre,
        e.marca,
        e.modelo,
        c.nombre AS categoria,
        l.nombre AS laboratorio,
        e.estado_fisico,
        e.ubicacion_especifica
    FROM equipos e
    LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
    LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
    WHERE e.estado = 'disponible'
        AND (p_categoria_id IS NULL OR e.id_categoria = p_categoria_id)
        AND (p_laboratorio_id IS NULL OR e.id_laboratorio = p_laboratorio_id)
    ORDER BY e.nombre;
END//

-- =========================================================
-- PROCEDIMIENTO: Registrar préstamo completo
-- =========================================================
DROP PROCEDURE IF EXISTS sp_registrar_prestamo//
CREATE PROCEDURE sp_registrar_prestamo(
    IN p_equipo_id INT,
    IN p_usuario_solicitante INT,
    IN p_usuario_autorizador INT,
    IN p_proposito VARCHAR(255),
    IN p_horas_prestamo INT,
    OUT p_resultado INT,
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_estado_equipo VARCHAR(20);
    DECLARE v_codigo_prestamo VARCHAR(50);
    
    -- Verificar estado del equipo
    SELECT estado INTO v_estado_equipo FROM equipos WHERE id = p_equipo_id;
    
    IF v_estado_equipo IS NULL THEN
        SET p_resultado = 0;
        SET p_mensaje = 'Equipo no encontrado';
    ELSEIF v_estado_equipo != 'disponible' THEN
        SET p_resultado = 0;
        SET p_mensaje = CONCAT('Equipo no disponible. Estado actual: ', v_estado_equipo);
    ELSE
        -- Generar código de préstamo
        SET v_codigo_prestamo = CONCAT('PREST-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(FLOOR(RAND() * 10000), 4, '0'));
        
        -- Crear préstamo
        INSERT INTO prestamos (codigo, id_equipo, id_usuario_solicitante, id_usuario_autorizador, fecha, fecha_devolucion_programada, proposito, estado)
        VALUES (
            v_codigo_prestamo,
            p_equipo_id,
            p_usuario_solicitante,
            p_usuario_autorizador,
            NOW(),
            DATE_ADD(NOW(), INTERVAL p_horas_prestamo HOUR),
            p_proposito,
            'activo'
        );
        
        SET p_resultado = 1;
        SET p_mensaje = CONCAT('Préstamo registrado exitosamente. Código: ', v_codigo_prestamo);
    END IF;
END//

-- =========================================================
-- PROCEDIMIENTO: Procesar devolución de equipo
-- =========================================================
DROP PROCEDURE IF EXISTS sp_procesar_devolucion//
CREATE PROCEDURE sp_procesar_devolucion(
    IN p_prestamo_id INT,
    IN p_observaciones TEXT,
    IN p_estado_devolucion VARCHAR(20),
    OUT p_resultado INT,
    OUT p_mensaje VARCHAR(255)
)
BEGIN
    DECLARE v_estado_prestamo VARCHAR(20);
    
    -- Verificar estado del préstamo
    SELECT estado INTO v_estado_prestamo FROM prestamos WHERE id = p_prestamo_id;
    
    IF v_estado_prestamo IS NULL THEN
        SET p_resultado = 0;
        SET p_mensaje = 'Préstamo no encontrado';
    ELSEIF v_estado_prestamo = 'devuelto' THEN
        SET p_resultado = 0;
        SET p_mensaje = 'Este préstamo ya fue devuelto';
    ELSE
        -- Actualizar préstamo
        UPDATE prestamos 
        SET estado = 'devuelto',
            fecha_devolucion_real = NOW(),
            observaciones = p_observaciones,
            estado_devolucion = p_estado_devolucion
        WHERE id = p_prestamo_id;
        
        SET p_resultado = 1;
        SET p_mensaje = 'Devolución procesada exitosamente';
    END IF;
END//

-- =========================================================
-- PROCEDIMIENTO: Obtener alertas de mantenimiento vencidas
-- =========================================================
DROP PROCEDURE IF EXISTS sp_alertas_vencidas//
CREATE PROCEDURE sp_alertas_vencidas()
BEGIN
    SELECT 
        a.id,
        e.codigo_interno,
        e.nombre AS equipo,
        a.tipo_alerta,
        a.descripcion_alerta,
        a.fecha_limite,
        a.prioridad,
        DATEDIFF(CURDATE(), a.fecha_limite) AS dias_vencido,
        CONCAT(u.nombres, ' ', u.apellidos) AS tecnico_asignado
    FROM alertas_mantenimiento a
    JOIN equipos e ON a.id_equipo = e.id
    LEFT JOIN usuarios u ON a.asignado_a = u.id
    WHERE a.estado_alerta = 'pendiente'
        AND a.fecha_limite < CURDATE()
    ORDER BY a.fecha_limite ASC;
END//

-- =========================================================
-- FUNCIÓN: Calcular días hasta próximo mantenimiento
-- =========================================================
DROP FUNCTION IF EXISTS fn_dias_proximo_mantenimiento//
CREATE FUNCTION fn_dias_proximo_mantenimiento(p_equipo_id INT) 
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_proxima_fecha DATE;
    DECLARE v_dias INT;
    
    SELECT MIN(fecha_limite) INTO v_proxima_fecha
    FROM alertas_mantenimiento
    WHERE id_equipo = p_equipo_id
        AND estado_alerta = 'pendiente'
        AND fecha_limite >= CURDATE();
    
    IF v_proxima_fecha IS NULL THEN
        SET v_dias = -1;
    ELSE
        SET v_dias = DATEDIFF(v_proxima_fecha, CURDATE());
    END IF;
    
    RETURN v_dias;
END//

-- =========================================================
-- FUNCIÓN: Verificar disponibilidad de laboratorio
-- =========================================================
DROP FUNCTION IF EXISTS fn_laboratorio_disponible//
CREATE FUNCTION fn_laboratorio_disponible(p_laboratorio_id INT, p_fecha DATETIME, p_duracion_horas INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE v_conflictos INT;
    DECLARE v_fecha_fin DATETIME;
    
    SET v_fecha_fin = DATE_ADD(p_fecha, INTERVAL p_duracion_horas HOUR);
    
    SELECT COUNT(*) INTO v_conflictos
    FROM practicas_laboratorio
    WHERE id_laboratorio = p_laboratorio_id
        AND estado IN ('programada', 'en_progreso')
        AND (
            (fecha <= p_fecha AND DATE_ADD(fecha, INTERVAL duracion_horas HOUR) > p_fecha)
            OR (fecha < v_fecha_fin AND DATE_ADD(fecha, INTERVAL duracion_horas HOUR) >= v_fecha_fin)
            OR (fecha >= p_fecha AND DATE_ADD(fecha, INTERVAL duracion_horas HOUR) <= v_fecha_fin)
        );
    
    RETURN v_conflictos = 0;
END//

DELIMITER ;

-- =========================================================
-- EVENTOS PROGRAMADOS
-- =========================================================

-- Habilitar el programador de eventos
SET GLOBAL event_scheduler = ON;

-- Evento: Marcar alertas vencidas
DROP EVENT IF EXISTS ev_marcar_alertas_vencidas;
CREATE EVENT ev_marcar_alertas_vencidas
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
    UPDATE alertas_mantenimiento
    SET tipo_alerta = 'mantenimiento_vencido',
        prioridad = 'critica'
    WHERE estado_alerta = 'pendiente'
        AND fecha_limite < CURDATE()
        AND tipo_alerta != 'mantenimiento_vencido';

-- Evento: Limpiar logs antiguos (más de 90 días)
DROP EVENT IF EXISTS ev_limpiar_logs_antiguos;
CREATE EVENT ev_limpiar_logs_antiguos
ON SCHEDULE EVERY 1 WEEK
STARTS CURRENT_DATE + INTERVAL 7 DAY
DO
    DELETE FROM logs_sistema WHERE fecha < DATE_SUB(CURDATE(), INTERVAL 90 DAY);

-- =========================================================
-- FIN DE TRIGGERS Y PROCEDIMIENTOS
-- =========================================================
