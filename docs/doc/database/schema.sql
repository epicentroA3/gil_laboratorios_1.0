
```sql
-- =========================================================
-- GIL LABORATORIOS - ESQUEMA DE BASE DE DATOS MySQL
-- Sistema de Gestión Integral de Laboratorios SENA
-- =========================================================

-- Crear base de datos con charset UTF-8
CREATE DATABASE IF NOT EXISTS gil_laboratorios 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;
USE gil_laboratorios;

-- Establecer charset para la sesión
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- =========================================================
-- MÓDULO 1: GESTIÓN DE USUARIOS Y ROLES
-- =========================================================

-- Tabla de Roles
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    permisos TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    documento VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(15),
    id_rol INT,
    password_hash VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    estado ENUM('activo', 'inactivo', 'suspendido') DEFAULT 'activo',
    FOREIGN KEY (id_rol) REFERENCES roles(id)
);

-- =========================================================
-- MÓDULO 2: GESTIÓN DE LABORATORIOS Y ESPACIOS
-- =========================================================

-- Tabla de Laboratorios
CREATE TABLE IF NOT EXISTS laboratorios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo_lab VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('quimica', 'mineria', 'suelos', 'metalurgia', 'general') NOT NULL,
    ubicacion VARCHAR(200),
    capacidad_personas INT DEFAULT 20,
    area_m2 DECIMAL(8,2),
    responsable_id INT,
    estado ENUM('disponible', 'ocupado', 'mantenimiento', 'fuera_servicio') DEFAULT 'disponible',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsable_id) REFERENCES usuarios(id)
); 

-- =========================================================
-- MÓDULO 3: INVENTARIO INTELIGENTE
-- =========================================================

-- Tabla de Categorías de Equipos
CREATE TABLE IF NOT EXISTS categorias_equipos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    codigo VARCHAR(20) UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Equipos
CREATE TABLE IF NOT EXISTS equipos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo_interno VARCHAR(50) NOT NULL UNIQUE,
    codigo_qr VARCHAR(255) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    numero_serie VARCHAR(150),
    id_categoria INT,
    id_laboratorio INT,
    descripcion TEXT,
    especificaciones_tecnicas TEXT,
    valor_adquisicion DECIMAL(12,2),
    fecha_adquisicion DATE,
    proveedor VARCHAR(200),
    garantia_meses INT DEFAULT 12,
    vida_util_anos INT DEFAULT 5,
    imagen_url VARCHAR(500),
    imagen_hash VARCHAR(64),
    estado ENUM('disponible', 'prestado', 'mantenimiento', 'reparacion', 'dado_baja') DEFAULT 'disponible',
    estado_fisico ENUM('excelente', 'bueno', 'regular', 'malo') DEFAULT 'bueno',
    ubicacion_especifica VARCHAR(200),
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_categoria) REFERENCES categorias_equipos(id),
    FOREIGN KEY (id_laboratorio) REFERENCES laboratorios(id),
    INDEX idx_codigo_interno (codigo_interno),
    INDEX idx_estado (estado),
    INDEX idx_categoria (id_categoria),
    INDEX idx_laboratorio (id_laboratorio)
);

-- =========================================================
-- MÓDULO 4: SISTEMA DE PRÉSTAMOS Y TRAZABILIDAD
-- =========================================================

-- Tabla de Préstamos
CREATE TABLE IF NOT EXISTS prestamos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    id_equipo INT NOT NULL,
    id_usuario_solicitante INT NOT NULL,
    id_usuario_autorizador INT,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha DATETIME,
    fecha_devolucion_programada DATETIME,
    fecha_devolucion_real DATETIME NULL,
    proposito TEXT,
    observaciones TEXT,
    observaciones_devolucion TEXT,
    estado ENUM('solicitado', 'aprobado', 'rechazado', 'activo', 'devuelto', 'vencido') DEFAULT 'solicitado',
    calificacion_devolucion ENUM('excelente', 'bueno', 'regular', 'malo') NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id),
    FOREIGN KEY (id_usuario_solicitante) REFERENCES usuarios(id),
    FOREIGN KEY (id_usuario_autorizador) REFERENCES usuarios(id),
    INDEX idx_estado (estado),
    INDEX idx_fecha (fecha),
    INDEX idx_usuario_solicitante (id_usuario_solicitante)
);

-- =========================================================
-- MÓDULO 5: MANTENIMIENTO PREDICTIVO
-- =========================================================

-- Tabla de Tipos de Mantenimiento
CREATE TABLE IF NOT EXISTS tipos_mantenimiento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    frecuencia_dias INT DEFAULT 30,
    es_preventivo BOOLEAN DEFAULT true
);

-- Tabla de Historial de Mantenimiento
CREATE TABLE IF NOT EXISTS historial_mantenimiento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    id_tipo_mantenimiento INT NOT NULL,
    estado ENUM('en_proceso', 'completado', 'cancelado') DEFAULT 'en_proceso',
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NULL,
    tecnico_responsable_id INT,
    descripcion_trabajo TEXT,
    partes_reemplazadas TEXT,
    costo_mantenimiento DECIMAL(10,2) DEFAULT 0,
    tiempo_inactividad_horas DECIMAL(5,2) DEFAULT 0,
    observaciones TEXT,
    estado_post_mantenimiento ENUM('excelente', 'bueno', 'regular', 'malo') NULL,
    proxima_fecha_mantenimiento DATE NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id),
    FOREIGN KEY (id_tipo_mantenimiento) REFERENCES tipos_mantenimiento(id),
    FOREIGN KEY (tecnico_responsable_id) REFERENCES usuarios(id),
    INDEX idx_equipo_mantenimiento (id_equipo),
    INDEX idx_estado (estado),
    INDEX idx_fecha_inicio (fecha_inicio)
);

-- Tabla de Alertas de Mantenimiento
CREATE TABLE IF NOT EXISTS alertas_mantenimiento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    tipo_alerta ENUM('mantenimiento_programado', 'mantenimiento_vencido', 'falla_predicha', 'revision_urgente') NOT NULL,
    descripcion_alerta TEXT,
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_limite DATE,
    prioridad ENUM('baja', 'media', 'alta', 'critica') DEFAULT 'media',
    estado_alerta ENUM('pendiente', 'en_proceso', 'resuelta', 'cancelada') DEFAULT 'pendiente',
    asignado_a INT,
    fecha_resolucion DATETIME NULL,
    observaciones_resolucion TEXT,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id),
    FOREIGN KEY (asignado_a) REFERENCES usuarios(id),
    INDEX idx_estado_alerta (estado_alerta),
    INDEX idx_prioridad (prioridad),
    INDEX idx_fecha_limite (fecha_limite)
);

-- =========================================================
-- MÓDULO 6: GESTIÓN DE PRÁCTICAS DE LABORATORIO
-- =========================================================

-- Tabla de Programas de Formación
CREATE TABLE IF NOT EXISTS programas_formacion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo_programa VARCHAR(20) NOT NULL UNIQUE,
    nombre_programa VARCHAR(200) NOT NULL,
    tipo_programa ENUM('tecnico', 'tecnologo', 'complementaria') NOT NULL,
    descripcion TEXT,
    duracion_meses INT,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de Instructores cambiar nomber datos de intructores
CREATE TABLE IF NOT EXISTS instructores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL UNIQUE,
    especialidad VARCHAR(200),
    experiencia_anos INT,
    certificaciones TEXT,
    fecha_vinculacion DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Tabla de Prácticas de Laboratorio
CREATE TABLE IF NOT EXISTS practicas_laboratorio (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    id_programa INT NOT NULL,
    id_laboratorio INT NOT NULL,
    id_instructor INT NOT NULL,
    fecha DATETIME NOT NULL,
    duracion_horas DECIMAL(3,1),
    numero_estudiantes INT,
    equipos_requeridos TEXT,
    materiales_requeridos TEXT,
    objetivos TEXT,
    descripcion_actividades TEXT,
    observaciones TEXT,
    estado ENUM('programada', 'en_curso', 'completada', 'cancelada') DEFAULT 'programada',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_programa) REFERENCES programas_formacion(id),
    FOREIGN KEY (id_laboratorio) REFERENCES laboratorios(id),
    FOREIGN KEY (id_instructor) REFERENCES instructores(id),
    INDEX idx_fecha (fecha),
    INDEX idx_estado (estado),
    INDEX idx_laboratorio (id_laboratorio)
);

-- Tabla de Capacitaciones
CREATE TABLE IF NOT EXISTS capacitaciones (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(300) NOT NULL,
    descripcion TEXT,
    tipo_capacitacion ENUM('modulo_formativo', 'taller', 'material_didactico', 'gestion_cambio') DEFAULT 'taller',
    producto VARCHAR(200),
    medicion VARCHAR(200),
    cantidad_meta INT,
    cantidad_actual INT DEFAULT 0,
    actividad VARCHAR(300),
    porcentaje_avance DECIMAL(5,2) DEFAULT 0.00,
    recursos_asociados TEXT,
    participantes TEXT,
    duracion_horas INT,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado ENUM('programada', 'activo', 'finalizada', 'cancelada') DEFAULT 'programada',
    id_instructor INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_instructor) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabla de Encuestas
CREATE TABLE IF NOT EXISTS encuestas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    tipo ENUM('practica', 'prestamo', 'mantenimiento', 'general') NOT NULL,
    puntuacion INT CHECK (puntuacion BETWEEN 1 AND 5),
    comentarios TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- =========================================================
-- MÓDULO 7: ASISTENTE DE VOZ LUCIA
-- =========================================================

-- Tabla de Comandos de Voz
CREATE TABLE IF NOT EXISTS comandos_voz (
    id_comando INT PRIMARY KEY AUTO_INCREMENT,
    comando_texto VARCHAR(500) NOT NULL,
    intencion VARCHAR(100) NOT NULL,
    parametros TEXT,
    respuesta_esperada TEXT,
    frecuencia_uso INT DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo'
);

-- Tabla de Interacciones de Voz
CREATE TABLE IF NOT EXISTS interacciones_voz (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT,
    comando_detectado TEXT,
    intencion_identificada VARCHAR(100),
    confianza_reconocimiento DECIMAL(3,2),
    respuesta_generada TEXT,
    accion_ejecutada VARCHAR(200),
    exitosa BOOLEAN DEFAULT false,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracion_procesamiento_ms INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    INDEX idx_usuario (id_usuario),
    INDEX idx_timestamp (timestamp)
);

-- =========================================================
-- MÓDULO 8: RECONOCIMIENTO DE IMÁGENES
-- =========================================================

-- Tabla de Modelos IA
CREATE TABLE IF NOT EXISTS modelos_ia (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('reconocimiento_imagenes', 'reconocimiento_voz', 'prediccion_mantenimiento') NOT NULL,
    version VARCHAR(20),
    ruta_archivo VARCHAR(500),
    precision_modelo DECIMAL(5,4),
    fecha_entrenamiento DATE,
    fecha_deployment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'inactivo', 'entrenando') DEFAULT 'activo',
    parametros_modelo TEXT
);

-- Tabla de Reconocimientos de Imágenes
CREATE TABLE IF NOT EXISTS reconocimientos_imagen (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo_detectado INT,
    imagen_original_url VARCHAR(500),
    confianza_deteccion DECIMAL(3,2),
    coordenadas_deteccion TEXT,
    id_modelo_usado INT,
    procesado_por_usuario INT,
    fecha_reconocimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validacion_manual ENUM('correcto', 'incorrecto', 'pendiente') DEFAULT 'pendiente',
    FOREIGN KEY (id_equipo_detectado) REFERENCES equipos(id),
    FOREIGN KEY (id_modelo_usado) REFERENCES modelos_ia(id),
    FOREIGN KEY (procesado_por_usuario) REFERENCES usuarios(id)
);

-- Tabla de Imágenes de Entrenamiento para IA
-- Almacena múltiples imágenes por equipo para entrenar el modelo MobileNet
CREATE TABLE IF NOT EXISTS imagenes_entrenamiento (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    ruta_imagen VARCHAR(500) NOT NULL,
    angulo_captura VARCHAR(50) DEFAULT 'frontal',
    resolucion VARCHAR(20),
    formato VARCHAR(10) DEFAULT 'jpg',
    tamano_bytes INT,
    hash_imagen VARCHAR(64),
    calidad_imagen DECIMAL(3,2),
    estado ENUM('pendiente', 'entrenado', 'error') DEFAULT 'pendiente',
    fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id) ON DELETE CASCADE,
    INDEX idx_equipo (id_equipo),
    INDEX idx_estado (estado)
);

-- =========================================================
-- MÓDULO 9: CONFIGURACIÓN Y LOGS
-- =========================================================

-- Tabla de Configuración del Sistema
CREATE TABLE IF NOT EXISTS configuracion_sistema (
    id INT PRIMARY KEY AUTO_INCREMENT,
    clave_config VARCHAR(100) NOT NULL UNIQUE,
    valor_config TEXT,
    descripcion TEXT,
    tipo_dato ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Logs del Sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id INT PRIMARY KEY AUTO_INCREMENT,
    modulo VARCHAR(50) NOT NULL,
    nivel_log ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    mensaje TEXT NOT NULL,
    id_usuario INT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    datos_adicionales TEXT,
    timestamp_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    INDEX idx_modulo (modulo),
    INDEX idx_nivel_log (nivel_log),
    INDEX idx_timestamp (timestamp_log),
    INDEX idx_usuario_log (id_usuario)
);

-- Tabla de Logs de Cambios
CREATE TABLE IF NOT EXISTS logs_cambios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tabla_afectada VARCHAR(50) NOT NULL,
    id_registro INT NOT NULL,
    campo VARCHAR(50) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    id_usuario INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- =========================================================
-- MÓDULO 10: RECUPERACIÓN DE CONTRASEÑAS
-- =========================================================

-- Tabla de Tokens de Restablecimiento de Contraseña
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    expira_en DATETIME NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_solicitud VARCHAR(45),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expira (expira_en),
    INDEX idx_usuario (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- VISTAS DEL SISTEMA
-- =========================================================

-- Vista de Equipos Completa
DROP VIEW IF EXISTS vista_equipos_completa;
CREATE VIEW vista_equipos_completa AS
SELECT
    e.id AS id_equipo,
    e.codigo_interno,
    e.nombre AS nombre_equipo,
    e.marca,
    e.modelo,
    c.nombre AS nombre_categoria,
    l.nombre AS nombre_laboratorio,
    l.codigo_lab,
    e.estado AS estado_equipo,
    e.estado_fisico,
    e.ubicacion_especifica,
    e.fecha_registro,
    CASE
        WHEN e.estado = 'prestado' THEN
            (
                SELECT CONCAT(u.nombres, ' ', u.apellidos)
                FROM prestamos p
                JOIN usuarios u ON p.id_usuario_solicitante = u.id
                WHERE p.id_equipo = e.id
                  AND p.estado = 'activo'
                ORDER BY p.fecha_solicitud DESC
                LIMIT 1
            )
        ELSE NULL
    END AS usuario_actual
FROM equipos e
LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
LEFT JOIN laboratorios l ON e.id_laboratorio = l.id;

-- Vista de Préstamos Activos
DROP VIEW IF EXISTS vista_prestamos_activos;
CREATE VIEW vista_prestamos_activos AS
SELECT
    p.id AS id_prestamo,
    p.codigo AS codigo_prestamo,
    e.codigo_interno,
    e.nombre AS nombre_equipo,
    CONCAT(u.nombres, ' ', u.apellidos) AS solicitante,
    p.fecha AS fecha_prestamo,
    p.fecha_devolucion_programada,
    DATEDIFF(p.fecha_devolucion_programada, NOW()) AS dias_restantes,
    CASE
        WHEN p.fecha_devolucion_programada < NOW() THEN 'VENCIDO'
        WHEN DATEDIFF(p.fecha_devolucion_programada, NOW()) <= 1 THEN 'POR_VENCER'
        ELSE 'VIGENTE'
    END AS estado_temporal
FROM prestamos p
JOIN equipos e ON p.id_equipo = e.id
JOIN usuarios u ON p.id_usuario_solicitante = u.id
WHERE p.estado = 'activo';

-- Vista de Alertas Pendientes
DROP VIEW IF EXISTS vista_alertas_pendientes;
CREATE VIEW vista_alertas_pendientes AS
SELECT
    a.id AS id_alerta,
    e.codigo_interno,
    e.nombre AS nombre_equipo,
    l.nombre AS nombre_laboratorio,
    a.tipo_alerta,
    a.descripcion_alerta,
    a.fecha_limite,
    a.prioridad,
    DATEDIFF(a.fecha_limite, NOW()) AS dias_hasta_limite,
    CONCAT(u.nombres, ' ', u.apellidos) AS asignado_a
FROM alertas_mantenimiento a
JOIN equipos e ON a.id_equipo = e.id
LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
LEFT JOIN usuarios u ON a.asignado_a = u.id
WHERE a.estado_alerta = 'pendiente'
ORDER BY a.prioridad DESC, a.fecha_limite ASC;

-- =========================================================
-- DATOS INICIALES
-- =========================================================

-- Roles Iniciales con permisos completos por módulo
-- Permisos disponibles: usuarios, roles, programas, equipos, equipos_ver, laboratorios, laboratorios_ver,
-- practicas, reservas, reservas_propias, reportes, mantenimiento, mantenimiento_ver, capacitaciones,
-- capacitaciones_ver, reconocimiento, ia_visual, backups, configuracion, ayuda
INSERT IGNORE INTO roles (nombre_rol, descripcion, permisos) VALUES
('Administrador', 'Acceso completo al sistema', '{"all": true, "usuarios": true, "roles": true, "programas": true, "equipos": true, "laboratorios": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento": true, "capacitaciones": true, "reconocimiento": true, "ia_visual": true, "backups": true, "configuracion": true, "ayuda": true}'),
('Instructor', 'Gestión de prácticas y préstamos', '{"equipos": true, "laboratorios_ver": true, "practicas": true, "reservas": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones": true, "reconocimiento": true, "ayuda": true}'),
('Técnico Laboratorio', 'Mantenimiento y gestión de equipos', '{"equipos": true, "reservas": true, "mantenimiento": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'),
('Aprendiz', 'Consulta de información y solicitud de préstamos', '{"equipos_ver": true, "reservas_propias": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}'),
('Coordinador', 'Supervisión y reportes', '{"equipos_ver": true, "laboratorios_ver": true, "reservas_ver": true, "reportes": true, "mantenimiento_ver": true, "capacitaciones_ver": true, "reconocimiento": true, "ayuda": true}');

-- Categorías de Equipos
INSERT IGNORE INTO categorias_equipos (nombre, descripcion, codigo) VALUES
('Microscopios', 'Equipos de observación y análisis microscópico', 'MICRO'),
('Balanzas', 'Equipos de medición de masa y peso', 'BAL'),
('Centrifugas', 'Equipos de separación por centrifugación', 'CENT'),
('Espectrofotómetros', 'Equipos de análisis espectral', 'ESPEC'),
('pH-metros', 'Equipos de medición de pH', 'PH'),
('Estufas', 'Equipos de calentamiento y secado', 'ESTUF'),
('Equipos Minería', 'Equipos específicos para análisis minero', 'MIN'),
('Equipos Suelos', 'Equipos para análisis de suelos', 'SUELO'),
('Instrumentos Medición', 'Instrumentos generales de medición', 'MED'),
('Reactivos', 'Productos químicos y reactivos', 'REACT');

-- Tipos de Mantenimiento
INSERT IGNORE INTO tipos_mantenimiento (nombre, descripcion, frecuencia_dias, es_preventivo) VALUES
('Mantenimiento Preventivo Mensual', 'Revisión general mensual del equipo', 30, true),
('Mantenimiento Preventivo Trimestral', 'Mantenimiento detallado trimestral', 90, true),
('Calibración', 'Calibración de precisión del equipo', 180, true),
('Limpieza Profunda', 'Limpieza y desinfección completa', 15, true),
('Mantenimiento Correctivo', 'Reparación por falla o avería', 0, false),
('Revisión Anual', 'Inspección completa anual', 365, true);

-- Programas de Formación
INSERT IGNORE INTO programas_formacion (codigo_programa, nombre_programa, tipo_programa, descripcion, duracion_meses) VALUES
('TEC-MIN-001', 'Tecnología en Minería', 'tecnologo', 'Programa tecnológico en explotación minera', 30),
('TEC-QUI-001', 'Tecnología en Química', 'tecnologo', 'Programa tecnológico en análisis químico', 30),
('TEC-SUE-001', 'Tecnología en Análisis de Suelos', 'tecnico', 'Programa técnico en análisis y caracterización de suelos', 18),
('TEC-MET-001', 'Tecnología en Metalurgia', 'tecnologo', 'Programa tecnológico en procesos metalúrgicos', 30);

-- Comandos de Voz para LUCIA
INSERT IGNORE INTO comandos_voz (comando_texto, intencion, parametros, respuesta_esperada) VALUES
('Lucia buscar equipo', 'buscar_equipo', '{"tipo": "general"}', 'Iniciando búsqueda de equipos disponibles'),
('Lucia estado laboratorio', 'consultar_laboratorio', '{"info": "estado"}', 'Consultando estado actual de laboratorios'),
('Lucia préstamo equipo', 'solicitar_prestamo', '{"accion": "solicitar"}', 'Iniciando proceso de solicitud de préstamo'),
('Lucia inventario disponible', 'consultar_inventario', '{"filtro": "disponible"}', 'Mostrando inventario disponible'),
('Lucia alertas mantenimiento', 'consultar_alertas', '{"tipo": "mantenimiento"}', 'Consultando alertas de mantenimiento pendientes'),
('Lucia ayuda comandos', 'mostrar_ayuda', '{"seccion": "comandos"}', 'Mostrando comandos disponibles'),
('Lucia estado préstamos', 'consultar_prestamos', '{"estado": "activos"}', 'Consultando préstamos activos'),
('Lucia registrar devolución', 'devolver_equipo', '{"accion": "devolver"}', 'Iniciando proceso de devolución');

-- =========================================================
-- FIN DEL ESQUEMA
-- =========================================================