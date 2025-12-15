-- =========================================================
-- GIL LABORATORIOS - DATOS DE PRUEBA
-- Sistema de Gestión Integral de Laboratorios SENA
-- Ejecutar después de schema.sql
-- =========================================================

USE gil_laboratorios;

-- Establecer charset UTF-8 para la sesión
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- =========================================================
-- USUARIOS DE PRUEBA
-- =========================================================

-- Usuario Administrador
INSERT IGNORE INTO usuarios (documento, nombres, apellidos, email, telefono, id_rol, password_hash, estado) VALUES
('1098765432', 'Carlos Alberto', 'Rodríguez Pérez', 'carlos.rodriguez@sena.edu.co', '3101234567', 1, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1087654321', 'María Fernanda', 'González López', 'maria.gonzalez@sena.edu.co', '3112345678', 1, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo');

-- Instructores
INSERT IGNORE INTO usuarios (documento, nombres, apellidos, email, telefono, id_rol, password_hash, estado) VALUES
('1076543210', 'Juan Pablo', 'Martínez Ruiz', 'juan.martinez@sena.edu.co', '3123456789', 2, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1065432109', 'Ana María', 'Sánchez Torres', 'ana.sanchez@sena.edu.co', '3134567890', 2, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1054321098', 'Pedro Luis', 'Ramírez Castro', 'pedro.ramirez@sena.edu.co', '3145678901', 2, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo');

-- Técnicos de Laboratorio
INSERT IGNORE INTO usuarios (documento, nombres, apellidos, email, telefono, id_rol, password_hash, estado) VALUES
('1043210987', 'Laura Patricia', 'Díaz Mendoza', 'laura.diaz@sena.edu.co', '3156789012', 3, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1032109876', 'Diego Alejandro', 'Hernández Vargas', 'diego.hernandez@sena.edu.co', '3167890123', 3, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo');

-- Aprendices
INSERT IGNORE INTO usuarios (documento, nombres, apellidos, email, telefono, id_rol, password_hash, estado) VALUES
('1021098765', 'Sofía Valentina', 'López García', 'sofia.lopez@sena.edu.co', '3178901234', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1010987654', 'Andrés Felipe', 'García Muñoz', 'andres.garcia@sena.edu.co', '3189012345', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1009876543', 'Valentina', 'Moreno Jiménez', 'valentina.moreno@sena.edu.co', '3190123456', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1008765432', 'Santiago', 'Torres Rojas', 'santiago.torres@sena.edu.co', '3201234567', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1007654321', 'Camila Andrea', 'Vargas Pineda', 'camila.vargas@sena.edu.co', '3212345678', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1006543210', 'Daniel Esteban', 'Castro Silva', 'daniel.castro@sena.edu.co', '3223456789', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1005432109', 'Isabella', 'Reyes Ortiz', 'isabella.reyes@sena.edu.co', '3234567890', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1004321098', 'Mateo', 'Gutiérrez Parra', 'mateo.gutierrez@sena.edu.co', '3245678901', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1003210987', 'Mariana', 'Pineda Arias', 'mariana.pineda@sena.edu.co', '3256789012', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo'),
('1002109876', 'Sebastián', 'Arias Londoño', 'sebastian.arias@sena.edu.co', '3267890123', 4, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo');

-- Coordinador
INSERT IGNORE INTO usuarios (documento, nombres, apellidos, email, telefono, id_rol, password_hash, estado) VALUES
('1001098765', 'Roberto Carlos', 'Mendoza Ríos', 'roberto.mendoza@sena.edu.co', '3278901234', 5, '$2b$12$kDdDQlyzhIp8gPssX4dpDeUUw4VF8t5JKy1Oif9F9Am9I/vCfTn9O', 'activo');

-- =========================================================
-- LABORATORIOS
-- =========================================================

INSERT IGNORE INTO laboratorios (codigo_lab, nombre, tipo, ubicacion, capacidad_personas, area_m2, responsable_id, estado) VALUES
('LAB-QUI-001', 'Laboratorio de Química Analítica', 'quimica', 'Bloque A - Piso 2 - Aula 201', 25, 80.50, 1, 'disponible'),
('LAB-QUI-002', 'Laboratorio de Química Orgánica', 'quimica', 'Bloque A - Piso 2 - Aula 202', 20, 65.00, 1, 'disponible'),
('LAB-MIN-001', 'Laboratorio de Procesamiento de Minerales', 'mineria', 'Bloque B - Piso 1 - Aula 101', 30, 120.00, 2, 'disponible'),
('LAB-MIN-002', 'Laboratorio de Caracterización Mineralógica', 'mineria', 'Bloque B - Piso 1 - Aula 102', 20, 75.00, 2, 'disponible'),
('LAB-SUE-001', 'Laboratorio de Análisis de Suelos', 'suelos', 'Bloque C - Piso 1 - Aula 103', 25, 90.00, 3, 'disponible'),
('LAB-MET-001', 'Laboratorio de Metalurgia Extractiva', 'metalurgia', 'Bloque D - Piso 1 - Aula 104', 20, 100.00, 4, 'disponible'),
('LAB-GEN-001', 'Laboratorio Multipropósito', 'general', 'Bloque E - Piso 1 - Aula 105', 35, 150.00, 1, 'disponible');

-- =========================================================
-- INSTRUCTORES (vinculados a usuarios)
-- =========================================================

INSERT IGNORE INTO instructores (id_usuario, especialidad, experiencia_anos, certificaciones, fecha_vinculacion) VALUES
(3, 'Química Analítica y Control de Calidad', 8, 'Certificación ISO 17025, Especialización en Análisis Instrumental', '2017-02-15'),
(4, 'Procesamiento de Minerales', 12, 'Maestría en Ingeniería de Minas, Certificación en Flotación', '2013-03-20'),
(5, 'Análisis de Suelos y Aguas', 6, 'Especialización en Gestión Ambiental, Certificación en Muestreo', '2019-01-10');

-- =========================================================
-- EQUIPOS DE LABORATORIO
-- =========================================================

-- Microscopios
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('MICRO-001', 'QR-MICRO-001', 'Microscopio Óptico Binocular', 'Olympus', 'CX23', 'OLY-CX23-2024-001', 1, 1, 'Microscopio óptico para análisis de muestras', '{"aumento_max": "1000x", "oculares": "10x", "objetivos": "4x,10x,40x,100x"}', 3500000.00, '2024-01-15', 'Equipos Científicos S.A.S', 24, 10, 'disponible', 'excelente', 'Mesa de trabajo 1'),
('MICRO-002', 'QR-MICRO-002', 'Microscopio Óptico Binocular', 'Olympus', 'CX23', 'OLY-CX23-2024-002', 1, 1, 'Microscopio óptico para análisis de muestras', '{"aumento_max": "1000x", "oculares": "10x", "objetivos": "4x,10x,40x,100x"}', 3500000.00, '2024-01-15', 'Equipos Científicos S.A.S', 24, 10, 'disponible', 'excelente', 'Mesa de trabajo 2'),
('MICRO-003', 'QR-MICRO-003', 'Microscopio Estereoscópico', 'Nikon', 'SMZ745', 'NIK-SMZ-2023-001', 1, 4, 'Microscopio para observación de minerales', '{"aumento": "0.67x-5x", "distancia_trabajo": "115mm"}', 8500000.00, '2023-06-20', 'Nikon Colombia', 36, 15, 'disponible', 'bueno', 'Estación mineralógica'),
('MICRO-004', 'QR-MICRO-004', 'Microscopio Petrográfico', 'Leica', 'DM750P', 'LEI-DM750-2022-001', 1, 4, 'Microscopio polarizado para petrografía', '{"polarizadores": "rotatorios", "platina": "circular graduada"}', 25000000.00, '2022-03-10', 'Leica Microsystems', 36, 20, 'disponible', 'excelente', 'Sala de petrografía');

-- Balanzas
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('BAL-001', 'QR-BAL-001', 'Balanza Analítica de Precisión', 'Mettler Toledo', 'ME204E', 'MT-ME204-2024-001', 2, 1, 'Balanza para pesaje de precisión', '{"capacidad": "220g", "legibilidad": "0.1mg", "repetibilidad": "0.1mg"}', 12000000.00, '2024-02-01', 'Mettler Toledo Colombia', 24, 15, 'disponible', 'excelente', 'Mesa de balanzas'),
('BAL-002', 'QR-BAL-002', 'Balanza Analítica de Precisión', 'Mettler Toledo', 'ME204E', 'MT-ME204-2024-002', 2, 1, 'Balanza para pesaje de precisión', '{"capacidad": "220g", "legibilidad": "0.1mg", "repetibilidad": "0.1mg"}', 12000000.00, '2024-02-01', 'Mettler Toledo Colombia', 24, 15, 'disponible', 'excelente', 'Mesa de balanzas'),
('BAL-003', 'QR-BAL-003', 'Balanza de Precisión', 'Ohaus', 'Pioneer PX224', 'OH-PX224-2023-001', 2, 5, 'Balanza para análisis de suelos', '{"capacidad": "220g", "legibilidad": "0.1mg"}', 4500000.00, '2023-08-15', 'Ohaus Colombia', 24, 10, 'disponible', 'bueno', 'Área de preparación');

-- Centrifugas
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('CENT-001', 'QR-CENT-001', 'Centrífuga de Laboratorio', 'Hettich', 'EBA 21', 'HET-EBA21-2024-001', 3, 1, 'Centrífuga para separación de muestras', '{"rpm_max": "6000", "rcf_max": "3461xg", "capacidad": "6x15ml"}', 8000000.00, '2024-03-01', 'Hettich Instrumentos', 24, 12, 'disponible', 'excelente', 'Área de centrifugación'),
('CENT-002', 'QR-CENT-002', 'Centrífuga Refrigerada', 'Eppendorf', '5430R', 'EPP-5430R-2023-001', 3, 2, 'Centrífuga con control de temperatura', '{"rpm_max": "17500", "temperatura": "-10 a 40°C", "capacidad": "30x1.5ml"}', 35000000.00, '2023-05-20', 'Eppendorf Colombia', 36, 15, 'disponible', 'excelente', 'Cuarto frío');

-- Espectrofotómetros
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('ESPEC-001', 'QR-ESPEC-001', 'Espectrofotómetro UV-Vis', 'Thermo Scientific', 'Genesys 150', 'TS-GEN150-2024-001', 4, 1, 'Espectrofotómetro para análisis químico', '{"rango": "190-1100nm", "ancho_banda": "2nm", "precision": "±0.002A"}', 28000000.00, '2024-01-20', 'Thermo Fisher Scientific', 24, 15, 'disponible', 'excelente', 'Área de espectroscopía'),
('ESPEC-002', 'QR-ESPEC-002', 'Espectrofotómetro de Absorción Atómica', 'Agilent', '240FS AA', 'AGI-240FS-2022-001', 4, 1, 'AA para análisis de metales', '{"atomizador": "llama", "elementos": "67", "precision": "< 1% RSD"}', 120000000.00, '2022-06-15', 'Agilent Technologies', 36, 20, 'disponible', 'bueno', 'Sala de absorción atómica');

-- pH-metros
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('PH-001', 'QR-PH-001', 'pH-metro de Mesa', 'Hanna Instruments', 'HI5221', 'HAN-HI5221-2024-001', 5, 1, 'Medidor de pH de alta precisión', '{"rango_pH": "-2 a 20", "resolucion": "0.001", "precision": "±0.002"}', 3800000.00, '2024-02-15', 'Hanna Instruments', 24, 8, 'disponible', 'excelente', 'Mesa de análisis'),
('PH-002', 'QR-PH-002', 'pH-metro de Mesa', 'Hanna Instruments', 'HI5221', 'HAN-HI5221-2024-002', 5, 5, 'Medidor de pH para análisis de suelos', '{"rango_pH": "-2 a 20", "resolucion": "0.001", "precision": "±0.002"}', 3800000.00, '2024-02-15', 'Hanna Instruments', 24, 8, 'disponible', 'excelente', 'Área de pH'),
('PH-003', 'QR-PH-003', 'pH-metro Portátil', 'Hanna Instruments', 'HI98190', 'HAN-HI98190-2023-001', 5, 7, 'Medidor de pH portátil', '{"rango_pH": "0 a 14", "resolucion": "0.01", "IP67": true}', 2500000.00, '2023-09-10', 'Hanna Instruments', 24, 5, 'prestado', 'bueno', 'Almacén portátiles');

-- Estufas
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('ESTUF-001', 'QR-ESTUF-001', 'Estufa de Secado', 'Binder', 'ED 115', 'BIN-ED115-2023-001', 6, 5, 'Estufa para secado de muestras de suelo', '{"volumen": "115L", "temperatura_max": "300°C", "uniformidad": "±3°C"}', 15000000.00, '2023-04-01', 'Binder GmbH', 24, 15, 'disponible', 'excelente', 'Área de secado'),
('ESTUF-002', 'QR-ESTUF-002', 'Mufla de Alta Temperatura', 'Nabertherm', 'L9/11', 'NAB-L911-2022-001', 6, 6, 'Mufla para calcinación', '{"volumen": "9L", "temperatura_max": "1100°C", "rampa": "programable"}', 22000000.00, '2022-08-20', 'Nabertherm', 24, 20, 'disponible', 'bueno', 'Área de calcinación');

-- Equipos Minería
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('MIN-001', 'QR-MIN-001', 'Trituradora de Mandíbulas', 'Retsch', 'BB 50', 'RET-BB50-2023-001', 7, 3, 'Trituradora para preparación de muestras', '{"abertura": "40x40mm", "granulometria_final": "<0.5mm", "potencia": "750W"}', 45000000.00, '2023-02-15', 'Retsch GmbH', 24, 20, 'disponible', 'excelente', 'Área de trituración'),
('MIN-002', 'QR-MIN-002', 'Molino de Bolas', 'Retsch', 'PM 100', 'RET-PM100-2022-001', 7, 3, 'Molino planetario para molienda fina', '{"velocidad_max": "650rpm", "capacidad": "500ml", "finura": "<1µm"}', 38000000.00, '2022-07-10', 'Retsch GmbH', 24, 15, 'disponible', 'bueno', 'Área de molienda'),
('MIN-003', 'QR-MIN-003', 'Celda de Flotación Denver', 'Metso', 'D-12', 'MET-D12-2021-001', 7, 3, 'Celda de flotación para pruebas batch', '{"volumen": "2.5L", "rpm": "1200", "aireacion": "controlada"}', 28000000.00, '2021-11-05', 'Metso Outotec', 24, 20, 'disponible', 'bueno', 'Área de flotación');

-- Equipos Suelos
INSERT IGNORE INTO equipos (codigo_interno, codigo_qr, nombre, marca, modelo, numero_serie, id_categoria, id_laboratorio, descripcion, especificaciones_tecnicas, valor_adquisicion, fecha_adquisicion, proveedor, garantia_meses, vida_util_anos, estado, estado_fisico, ubicacion_especifica) VALUES
('SUELO-001', 'QR-SUELO-001', 'Agitador de Tamices', 'Retsch', 'AS 200', 'RET-AS200-2023-001', 8, 5, 'Agitador para análisis granulométrico', '{"amplitud": "3mm", "tamices": "8", "tiempo": "programable"}', 18000000.00, '2023-03-20', 'Retsch GmbH', 24, 15, 'disponible', 'excelente', 'Área de granulometría'),
('SUELO-002', 'QR-SUELO-002', 'Hidrómetro de Bouyoucos', 'Fisher Scientific', 'ASTM 152H', 'FS-152H-2024-001', 8, 5, 'Hidrómetro para análisis de textura', '{"rango": "0-60g/L", "precision": "±0.5"}', 850000.00, '2024-01-10', 'Fisher Scientific', 12, 10, 'disponible', 'excelente', 'Área de sedimentación');

-- =========================================================
-- PRÉSTAMOS DE PRUEBA
-- =========================================================

INSERT IGNORE INTO prestamos (codigo, id_equipo, id_usuario_solicitante, id_usuario_autorizador, fecha, fecha_devolucion_programada, proposito, estado) VALUES
('PREST-2024-001', 17, 9, 3, '2024-12-01 08:00:00', '2024-12-01 17:00:00', 'Medición de pH en campo para proyecto de análisis de aguas', 'activo'),
('PREST-2024-002', 1, 10, 3, '2024-12-10 09:00:00', '2024-12-10 12:00:00', 'Práctica de microscopía para identificación de microorganismos', 'solicitado'),
('PREST-2024-003', 5, 11, 6, '2024-11-25 08:00:00', '2024-11-25 16:00:00', 'Pesaje de muestras para análisis gravimétrico', 'devuelto'),
('PREST-2024-004', 8, 12, 6, '2024-11-28 10:00:00', '2024-11-28 14:00:00', 'Separación de fases en muestras de laboratorio', 'devuelto'),
('PREST-2024-005', 11, 13, 3, '2024-12-05 08:00:00', '2024-12-05 17:00:00', 'Análisis de concentración de soluciones', 'aprobado');

-- =========================================================
-- HISTORIAL DE MANTENIMIENTO
-- =========================================================

INSERT IGNORE INTO historial_mantenimiento (id_equipo, id_tipo_mantenimiento, fecha_mantenimiento, tecnico_responsable_id, descripcion_trabajo, costo_mantenimiento, tiempo_inactividad_horas, estado_post_mantenimiento, proxima_fecha_mantenimiento) VALUES
(1, 1, '2024-11-01 09:00:00', 6, 'Limpieza de lentes, verificación de iluminación y ajuste de platina', 150000.00, 2.0, 'excelente', '2024-12-01'),
(2, 1, '2024-11-01 11:00:00', 6, 'Limpieza de lentes, verificación de iluminación y ajuste de platina', 150000.00, 2.0, 'excelente', '2024-12-01'),
(5, 3, '2024-10-15 08:00:00', 7, 'Calibración con pesas patrón certificadas, ajuste de sensibilidad', 350000.00, 4.0, 'excelente', '2025-04-15'),
(6, 3, '2024-10-15 14:00:00', 7, 'Calibración con pesas patrón certificadas, ajuste de sensibilidad', 350000.00, 4.0, 'excelente', '2025-04-15'),
(11, 3, '2024-09-20 09:00:00', 7, 'Calibración de longitud de onda, verificación de absorbancia', 500000.00, 6.0, 'excelente', '2025-03-20'),
(12, 1, '2024-11-15 08:00:00', 6, 'Limpieza de quemador, verificación de gases, ajuste de nebulizador', 800000.00, 8.0, 'bueno', '2024-12-15'),
(19, 4, '2024-11-20 09:00:00', 6, 'Limpieza profunda de cámara, verificación de sellos y calibración de temperatura', 400000.00, 4.0, 'excelente', '2024-12-05');

-- =========================================================
-- ALERTAS DE MANTENIMIENTO
-- =========================================================

INSERT IGNORE INTO alertas_mantenimiento (id_equipo, tipo_alerta, descripcion_alerta, fecha_limite, prioridad, estado_alerta, asignado_a) VALUES
(1, 'mantenimiento_programado', 'Mantenimiento preventivo mensual programado para microscopio', '2024-12-15', 'media', 'pendiente', 6),
(2, 'mantenimiento_programado', 'Mantenimiento preventivo mensual programado para microscopio', '2024-12-15', 'media', 'pendiente', 6),
(12, 'mantenimiento_programado', 'Limpieza mensual de quemador y nebulizador del AA', '2024-12-20', 'alta', 'pendiente', 7),
(3, 'revision_urgente', 'Se detectó desalineación en el sistema óptico durante última práctica', '2024-12-10', 'critica', 'en_proceso', 6),
(21, 'mantenimiento_vencido', 'Calibración de temperatura vencida hace 15 días', '2024-11-25', 'alta', 'pendiente', 7);

-- =========================================================
-- PRÁCTICAS DE LABORATORIO
-- =========================================================

INSERT IGNORE INTO practicas_laboratorio (codigo, nombre, id_programa, id_laboratorio, id_instructor, fecha, duracion_horas, numero_estudiantes, equipos_requeridos, materiales_requeridos, objetivos, estado) VALUES
('PRAC-QUI-001', 'Análisis Volumétrico: Titulaciones Ácido-Base', 1, 1, 1, '2024-12-15 08:00:00', 4.0, 20, '[1,2,13,14]', 'Buretas, erlenmeyers, indicadores, soluciones patrón', 'Determinar la concentración de soluciones mediante titulación', 'programada'),
('PRAC-QUI-002', 'Espectrofotometría UV-Vis', 2, 1, 1, '2024-12-16 08:00:00', 3.0, 15, '[11]', 'Celdas de cuarzo, soluciones estándar, micropipetas', 'Aplicar la ley de Beer-Lambert para cuantificación', 'programada'),
('PRAC-MIN-001', 'Preparación de Muestras Minerales', 2, 3, 2, '2024-12-17 08:00:00', 5.0, 18, '[19,20]', 'Muestras de roca, bolsas para muestras, etiquetas', 'Realizar trituración y molienda de muestras minerales', 'programada'),
('PRAC-MIN-002', 'Flotación de Sulfuros', 2, 3, 2, '2024-12-18 14:00:00', 4.0, 12, '[21]', 'Reactivos de flotación, colectores, espumantes', 'Separar minerales de cobre por flotación', 'programada'),
('PRAC-SUE-001', 'Análisis Granulométrico de Suelos', 3, 5, 3, '2024-12-19 08:00:00', 4.0, 22, '[22,23,7]', 'Tamices ASTM, cilindros de sedimentación, dispersante', 'Determinar la distribución de tamaño de partículas', 'programada'),
('PRAC-SUE-002', 'Determinación de pH y Conductividad Eléctrica', 3, 5, 3, '2024-12-20 08:00:00', 3.0, 20, '[15,16]', 'Electrodos, soluciones buffer, agua destilada', 'Medir propiedades electroquímicas del suelo', 'programada');

-- =========================================================
-- CAPACITACIONES
-- =========================================================

INSERT IGNORE INTO capacitaciones (titulo, descripcion, tipo_capacitacion, producto, medicion, cantidad_meta, cantidad_actual, actividad, porcentaje_avance, duracion_horas, fecha_inicio, fecha_fin, estado, id_instructor) VALUES
('Módulo Formativo: Inteligencia Artificial Aplicada', 'Capacitación en uso de herramientas de IA para gestión de laboratorios', 'modulo_formativo', 'Instructores capacitados en IA', 'Número de instructores', 15, 12, 'Talleres teórico-prácticos sobre IA', 80.00, 40, '2024-08-01', '2024-08-31', 'completada', 3),
('Taller: Reconocimiento de Imágenes con MobileNet', 'Taller práctico sobre implementación de reconocimiento de equipos', 'taller', 'Sistema de reconocimiento implementado', 'Equipos registrados', 50, 28, 'Entrenamiento del modelo MobileNet', 56.00, 16, '2024-09-01', '2024-09-15', 'completada', 4),
('Material Didáctico: Guías de Uso del Sistema', 'Creación de material didáctico para usuarios del sistema', 'material_didactico', 'Guías digitales publicadas', 'Número de guías', 10, 7, 'Diseño y redacción de guías', 70.00, 24, '2024-09-10', '2024-10-10', 'en_curso', 3),
('Gestión del Cambio: Adopción del Sistema GIL', 'Programa de gestión del cambio para adopción del nuevo sistema', 'gestion_cambio', 'Personal capacitado', 'Porcentaje de adopción', 100, 85, 'Sesiones de sensibilización y capacitación', 85.00, 32, '2024-08-15', '2024-11-15', 'en_curso', 5),
('Módulo Formativo: Mantenimiento Predictivo', 'Capacitación en técnicas de mantenimiento predictivo con ML', 'modulo_formativo', 'Técnicos certificados', 'Número de técnicos', 8, 6, 'Curso de machine learning aplicado', 75.00, 48, '2024-10-01', '2024-11-30', 'en_curso', 4),
('Taller: Comandos de Voz con LUCIA', 'Taller sobre uso efectivo del asistente de voz', 'taller', 'Usuarios entrenados', 'Número de usuarios', 30, 30, 'Sesiones prácticas con LUCIA', 100.00, 8, '2024-09-20', '2024-09-25', 'completada', 3),
('Material Didáctico: Videos Tutoriales', 'Producción de videos tutoriales para el sistema', 'material_didactico', 'Videos publicados', 'Número de videos', 15, 9, 'Grabación y edición de tutoriales', 60.00, 40, '2024-10-15', '2024-12-15', 'en_curso', 5),
('Gestión del Cambio: Cultura de Innovación', 'Programa para fomentar cultura de innovación tecnológica', 'gestion_cambio', 'Eventos realizados', 'Número de eventos', 6, 4, 'Charlas y talleres motivacionales', 66.67, 20, '2024-09-01', '2024-12-31', 'en_curso', 3);

-- =========================================================
-- ENCUESTAS DE SATISFACCIÓN
-- =========================================================

INSERT IGNORE INTO encuestas (id_usuario, tipo, puntuacion, comentarios) VALUES
(9, 'prestamo', 5, 'El asistente Lucia me prestó el equipo en 10 segundos, ¡increíble!'),
(10, 'practica', 4, 'Muy útil, pero a veces Lucia no entiende mi acento boyacense.'),
(11, 'mantenimiento', 5, 'Me avisaron que el microscopio necesitaba calibración antes de que fallara.'),
(12, 'general', 4, 'El sistema es rápido, pero falta más información en el dashboard.'),
(13, 'prestamo', 3, 'El código QR no funcionó, tuve que usar el buscador manual.'),
(14, 'practica', 5, 'La programación de prácticas fue muy fluida, sin conflictos.'),
(15, 'general', 5, 'Se nota que el sistema aprende, cada vez reconoce mejor los equipos.'),
(16, 'mantenimiento', 4, 'Buenas alertas, pero deberían llegar por email también.'),
(17, 'prestamo', 5, 'Devolver el equipo con voz es súper cómodo, especialmente con guantes.'),
(18, 'general', 4, 'Me gustaría poder reportar fallos directamente desde el sistema.');

-- =========================================================
-- MODELOS DE IA
-- =========================================================

INSERT IGNORE INTO modelos_ia (nombre, tipo, version, ruta_archivo, precision_modelo, fecha_entrenamiento, estado, parametros_modelo) VALUES
('MobileNetV2-Equipos', 'reconocimiento_imagenes', '2.1.0', '/models/mobilenet_equipos_v2.h5', 0.9234, '2024-10-15', 'activo', '{"input_shape": [224, 224, 3], "classes": 50, "optimizer": "adam"}'),
('Whisper-LUCIA', 'reconocimiento_voz', '1.5.0', '/models/whisper_lucia_v1.pt', 0.8876, '2024-09-20', 'activo', '{"language": "es", "model_size": "medium", "beam_size": 5}'),
('LSTM-Mantenimiento', 'prediccion_mantenimiento', '1.2.0', '/models/lstm_maint_v1.h5', 0.8542, '2024-08-10', 'activo', '{"sequence_length": 30, "features": 15, "hidden_units": 128}');

-- =========================================================
-- INTERACCIONES DE VOZ (ejemplo)
-- =========================================================

INSERT IGNORE INTO interacciones_voz (id_usuario, comando_detectado, intencion_identificada, confianza_reconocimiento, respuesta_generada, accion_ejecutada, exitosa, duracion_procesamiento_ms) VALUES
(9, 'Lucia buscar microscopio disponible', 'buscar_equipo', 0.95, 'Encontré 3 microscopios disponibles. ¿Deseas ver los detalles?', 'query_equipos', true, 245),
(10, 'Lucia estado del laboratorio de química', 'consultar_laboratorio', 0.88, 'El laboratorio de Química Analítica está disponible con capacidad para 25 personas.', 'query_laboratorios', true, 312),
(11, 'Lucia préstamo balanza', 'solicitar_prestamo', 0.92, 'Hay 2 balanzas disponibles. ¿Cuál deseas solicitar?', 'iniciar_prestamo', true, 198),
(12, 'Lucia alertas pendientes', 'consultar_alertas', 0.97, 'Tienes 3 alertas de mantenimiento pendientes. La más urgente es el microscopio estereoscópico.', 'query_alertas', true, 156);

-- =========================================================
-- RECONOCIMIENTOS DE IMAGEN (ejemplo)
-- =========================================================

INSERT IGNORE INTO reconocimientos_imagen (id_equipo_detectado, imagen_original_url, confianza_deteccion, coordenadas_deteccion, id_modelo_usado, procesado_por_usuario, validacion_manual) VALUES
(1, '/uploads/reconocimiento/img_2024120901.jpg', 0.94, '{"x": 120, "y": 85, "width": 340, "height": 280}', 1, 6, 'correcto'),
(5, '/uploads/reconocimiento/img_2024120902.jpg', 0.89, '{"x": 200, "y": 150, "width": 180, "height": 220}', 1, 6, 'correcto'),
(11, '/uploads/reconocimiento/img_2024120903.jpg', 0.78, '{"x": 50, "y": 30, "width": 400, "height": 350}', 1, 7, 'pendiente');

-- =========================================================
-- CONFIGURACIÓN DEL SISTEMA
-- =========================================================

INSERT IGNORE INTO configuracion_sistema (clave_config, valor_config, descripcion, tipo_dato) VALUES
('nombre_sistema', 'GIL Laboratorios SENA', 'Nombre del sistema', 'string'),
('version', '1.0.0', 'Versión actual del sistema', 'string'),
('timezone', 'America/Bogota', 'Zona horaria del sistema', 'string'),
('idioma_default', 'es', 'Idioma por defecto', 'string'),
('max_prestamo_horas', '8', 'Máximo de horas por préstamo', 'integer'),
('dias_anticipacion_alerta', '7', 'Días de anticipación para alertas de mantenimiento', 'integer'),
('umbral_confianza_voz', '0.75', 'Umbral mínimo de confianza para comandos de voz', 'string'),
('umbral_confianza_imagen', '0.80', 'Umbral mínimo de confianza para reconocimiento de imágenes', 'string'),
('habilitar_notificaciones_email', 'true', 'Habilitar notificaciones por email', 'boolean'),
('habilitar_lucia', 'true', 'Habilitar asistente de voz LUCIA', 'boolean'),
('tema_interfaz', 'claro', 'Tema de la interfaz (claro/oscuro)', 'string'),
('backup_automatico', 'true', 'Habilitar backup automático diario', 'boolean');

-- =========================================================
-- LOGS DE EJEMPLO
-- =========================================================

INSERT IGNORE INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address) VALUES
('autenticacion', 'INFO', 'Usuario carlos.rodriguez@sena.edu.co inició sesión exitosamente', 1, '192.168.1.100'),
('prestamos', 'INFO', 'Préstamo PREST-2024-001 creado por usuario ID 9', 9, '192.168.1.105'),
('mantenimiento', 'WARNING', 'Alerta de mantenimiento vencido para equipo ESTUF-002', NULL, NULL),
('reconocimiento_voz', 'INFO', 'Comando de voz procesado exitosamente: buscar_equipo', 9, '192.168.1.105'),
('reconocimiento_imagen', 'INFO', 'Equipo MICRO-001 identificado con 94% de confianza', 6, '192.168.1.110'),
('sistema', 'INFO', 'Backup automático completado exitosamente', NULL, NULL);

-- =========================================================
-- TIPOS DE MANTENIMIENTO
-- =========================================================

INSERT IGNORE INTO tipos_mantenimiento (nombre, descripcion, frecuencia_dias, es_preventivo) VALUES
('Preventivo General', 'Mantenimiento preventivo rutinario para asegurar el buen funcionamiento del equipo', 30, true),
('Correctivo', 'Mantenimiento correctivo para reparar fallas o averías', 0, false),
('Calibración', 'Calibración y ajuste de equipos de medición', 90, true),
('Limpieza Profunda', 'Limpieza exhaustiva de componentes internos y externos', 15, true),
('Revisión Técnica', 'Inspección técnica completa del equipo', 60, true),
('Reparación Mayor', 'Reparación de componentes críticos o reemplazo de piezas importantes', 0, false),
('Actualización de Software', 'Actualización de firmware o software del equipo', 180, true),
('Verificación de Seguridad', 'Verificación de sistemas de seguridad y protección', 45, true);

-- =========================================================
-- FIN DE DATOS DE PRUEBA
-- =========================================================
