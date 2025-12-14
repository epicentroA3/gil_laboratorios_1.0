"""
Configuración y Gestión de Base de Datos MySQL
Sistema GIL - Centro Minero de Sogamoso - SENA
"""
import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# Importar configuración centralizada
try:
    from config.config import Config
except ImportError:
    from .config import Config


class DatabaseManager:
    """Maneja todas las operaciones de base de datos MySQL"""

    _pool = None  # Pool de conexiones compartido

    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        database: str = None,
        use_pool: bool = True
    ):
        # Usar valores del .env a través de Config, o los proporcionados
        self.host = host or Config.DB_HOST
        self.user = user or Config.DB_USER
        self.password = password or Config.DB_PASSWORD
        self.database = database or Config.DB_NAME
        self.charset = Config.DB_CHARSET
        self.use_pool = use_pool
        self.connection = None

    @classmethod
    def get_pool(cls):
        """Obtiene o crea el pool de conexiones"""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name=Config.DB_POOL_NAME,
                    pool_size=Config.DB_POOL_SIZE,
                    pool_reset_session=Config.DB_POOL_RESET_SESSION,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset=Config.DB_CHARSET
                )
                print(f"✅ Pool de conexiones '{Config.DB_POOL_NAME}' creado")
            except Error as e:
                print(f"❌ Error creando pool de conexiones: {e}")
                cls._pool = None
        return cls._pool

    @contextmanager
    def get_connection(self):
        """Context manager para obtener una conexión del pool"""
        connection = None
        try:
            if self.use_pool:
                pool = self.get_pool()
                if pool:
                    connection = pool.get_connection()
            else:
                connection = mysql.connector.connect(
                    host=self.host,
                    port=Config.DB_PORT,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset=self.charset
                )
            yield connection
        finally:
            if connection and connection.is_connected():
                connection.close()

    def conectar(self):
        """Establece conexión con MySQL"""
        try:
            # Primero conectar sin especificar base de datos
            self.connection = mysql.connector.connect(
                host=self.host,
                port=Config.DB_PORT,
                user=self.user,
                password=self.password,
                charset=self.charset
            )

            if self.connection.is_connected():
                print(f"✅ Conexión exitosa a MySQL Server ({self.host}:{Config.DB_PORT})")
                self.crear_base_datos()
                return True

        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return False

    def crear_base_datos(self):
        """Crea la base de datos y todas las tablas necesarias"""
        try:
            cursor = self.connection.cursor()

            # Crear base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")

            print(f"✅ Base de datos '{self.database}' creada/conectada")

            # Crear todas las tablas
            self.crear_tablas(cursor)
            self.crear_vistas(cursor)
            self.insertar_datos_iniciales(cursor)

            self.connection.commit()
            cursor.close()

            # Reconectar con la base de datos específica
            self.connection.close()
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )

        except Error as e:
            print(f"❌ Error creando base de datos: {e}")

    

    def crear_tablas(self, cursor):
        """Crea todas las tablas del sistema"""

        # Taabla de Roles

        cursor.execute(
            """
            CREATE TABLE roles (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre_rol VARCHAR(50) NOT NULL UNIQUE,
            descripcion TEXT,
            permisos TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo'
            )
            """
        )

        # Tabla de Usuarios
        cursor.execute(
            """
           CREATE TABLE usuarios (
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
            )

        """
        )

        # MODULO 2: GESTIÓN DE LABORATORIOS Y ESPACIOS

        # Tabla de laboratorios
        cursor.execute(
            """
            CREATE TABLE laboratorios (
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

        """
        )

        # MODULO 3: INVENTARIO INTELIGENTE

        cursor.execute(
            """
            CREATE TABLE categorias_equipos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                codigo VARCHAR(20) UNIQUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

        """
        )

        cursor.execute(
            """
            CREATE TABLE equipos (
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
                imagen_hash VARCHAR(64), -- Para reconocimiento de imágenes
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

        """
        )

        # MÓDULO 4: SISTEMA DE PRÉSTAMOS Y TRAZABILIDAD

        cursor.execute(
            """
            CREATE TABLE prestamos (
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

        """
        )

        # MÓDULO 5: MANTENIMIENTO PREDICTIVO

        # Tabla de Tipos de Mantenimiento
        cursor.execute(
            """
            CREATE TABLE tipos_mantenimiento (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                frecuencia_dias INT DEFAULT 30,
                es_preventivo BOOLEAN DEFAULT true
            );

        """
        )

        # Tabla de Historial de Mantenimiento
        cursor.execute(
            """
            CREATE TABLE historial_mantenimiento (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_equipo INT NOT NULL,
                id_tipo_mantenimiento INT NOT NULL,
                fecha_mantenimiento DATETIME NOT NULL,
                tecnico_responsable_id INT,
                descripcion_trabajo TEXT,
                partes_reemplazadas TEXT,
                costo_mantenimiento DECIMAL(10,2),
                tiempo_inactividad_horas DECIMAL(5,2),
                observaciones TEXT,
                estado_post_mantenimiento ENUM('excelente', 'bueno', 'regular', 'malo'),
                proxima_fecha_mantenimiento DATE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_equipo) REFERENCES equipos(id),
                FOREIGN KEY (id_tipo_mantenimiento) REFERENCES tipos_mantenimiento(id),
                FOREIGN KEY (tecnico_responsable_id) REFERENCES usuarios(id),
                INDEX idx_equipo_mantenimiento (id_equipo),
                INDEX idx_fecha_mantenimiento (fecha_mantenimiento)
            );


        """
        )

        # Tabla de Alertas de Mantenimiento
        cursor.execute(
            """
            CREATE TABLE alertas_mantenimiento (
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

        """
        )

        # MÓDULO 6: GESTIÓN DE PRÁCTICAS DE LABORATORIO

        # Tabla de Programas de Formación
        cursor.execute(
            """
            CREATE TABLE programas_formacion (
                id INT PRIMARY KEY AUTO_INCREMENT,
                codigo_programa VARCHAR(20) NOT NULL UNIQUE,
                nombre_programa VARCHAR(200) NOT NULL,
                tipo_programa ENUM('tecnico', 'tecnologo', 'complementaria') NOT NULL,
                descripcion TEXT,
                duracion_meses INT,
                estado ENUM('activo', 'inactivo') DEFAULT 'activo'
            );

        """
        )

        # Tabla de Instructores
        cursor.execute(
            """
            CREATE TABLE instructores (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_usuario INT NOT NULL UNIQUE,
                especialidad VARCHAR(200),
                experiencia_anos INT,
                certificaciones TEXT,
                fecha_vinculacion DATE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            );
        """
        )

        # Tabla de Prácticas de Laboratorio
        cursor.execute(
            """
            CREATE TABLE practicas_laboratorio (
                id INT PRIMARY KEY AUTO_INCREMENT,
                codigo VARCHAR(30) NOT NULL UNIQUE,
                nombre VARCHAR(200) NOT NULL,
                id_programa INT NOT NULL,
                id_laboratorio INT NOT NULL,
                id_instructor INT NOT NULL,
                fecha DATETIME NOT NULL,
                duracion_horas DECIMAL(3,1),
                numero_estudiantes INT,
                equipos_requeridos TEXT, -- Array de IDs de equipos necesarios
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
        """
        )

        # Tabla de capacitaciones
        cursor.execute(
            """
            CREATE TABLE capacitaciones (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_usuario INT NOT NULL,
                tema VARCHAR(200) NOT NULL,
                fecha DATE NOT NULL,
                duracion_horas INT NOT NULL,
                calificacion INT CHECK (calificacion BETWEEN 0 AND 100),
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            );
        """
        )

        # Tabla de Encuestas
        cursor.execute(
            """
            CREATE TABLE encuestas (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_usuario INT NOT NULL,
                tipo ENUM('practica', 'prestamo', 'mantenimiento', 'general') NOT NULL,
                puntuacion INT CHECK (puntuacion BETWEEN 1 AND 5),
                comentarios TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            );
        """
        )

        # MÓDULO 7: ASISTENTE DE VOZ LUCIA

        # Tabla de Comando de voz
        cursor.execute(
            """
            CREATE TABLE comandos_voz (
            id_comando INT PRIMARY KEY AUTO_INCREMENT,
            comando_texto VARCHAR(500) NOT NULL,
            intencion VARCHAR(100) NOT NULL,
            parametros TEXT,
            respuesta_esperada TEXT,
            frecuencia_uso INT DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado ENUM('activo', 'inactivo') DEFAULT 'activo'
            );
        """
        )

        # Tabla de Interacciones de Voz
        cursor.execute(
            """
            CREATE TABLE interacciones_voz (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_usuario INT,
                comando_detectado TEXT,
                intencion_identificada VARCHAR(100),
                confianza_reconocimiento DECIMAL(3,2), -- 0.00 a 1.00
                respuesta_generada TEXT,
                accion_ejecutada VARCHAR(200),
                exitosa BOOLEAN DEFAULT false,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duracion_procesamiento_ms INT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
                INDEX idx_usuario (id_usuario),
                INDEX idx_timestamp (timestamp)
            );
        """
        )

        # MÓDULO 8: RECONOCIMIENTO DE IMÁGENES

        # Tabla de Modelos IA
        cursor.execute(
            """
            CREATE TABLE modelos_ia (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100) NOT NULL,
                tipo ENUM('reconocimiento_imagenes', 'reconocimiento_voz',      'prediccion_mantenimiento') NOT NULL,
                version VARCHAR(20),
                ruta_archivo VARCHAR(500),
                precision DECIMAL(5,4), -- Precisión del modelo (0.0000 a 1.0000)
                fecha_entrenamiento DATE,
                fecha_deployment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado ENUM('activo', 'inactivo', 'entrenando') DEFAULT 'activo',
                parametros_modelo TEXT
            );

        """
        )
        # Tabla de Reconocimientos de Imágenes
        cursor.execute(
            """
            CREATE TABLE reconocimientos_imagen (
                id INT PRIMARY KEY AUTO_INCREMENT,
                id_equipo_detectado INT,
                imagen_original_url VARCHAR(500),
                confianza_deteccion DECIMAL(3,2), -- 0.00 a 1.00
                coordenadas_deteccion TEXT, -- Coordenadas del bounding box
                id_modelo_usado INT,
                procesado_por_usuario INT,
                fecha_reconocimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validacion_manual ENUM('correcto', 'incorrecto', 'pendiente') DEFAULT 'pendiente',
                FOREIGN KEY (id_equipo_detectado) REFERENCES equipos(id),
                FOREIGN KEY (id_modelo_usado) REFERENCES modelos_ia(id),
                FOREIGN KEY (procesado_por_usuario) REFERENCES usuarios(id) 
            );
        """
        )

        # MÓDULO 9: CONFIGURACIÓN Y LOGS

        # Tabla de Configuración del Sistema
        cursor.execute(
            """
            CREATE TABLE configuracion_sistema (
                id INT PRIMARY KEY AUTO_INCREMENT,
                clave_config VARCHAR(100) NOT NULL UNIQUE,
                valor_config TEXT,
                descripcion TEXT,
                tipo_dato ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """
        )

        # Tabla de Logs del Sistema

        cursor.execute(
            """
            CREATE TABLE logs_sistema (
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
        """
        )

        # Tabla de Logs de Cambios
        cursor.execute(
            """
            CREATE TABLE logs_cambios (
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
        """
        )

        print("✅ Todas las tablas creadas exitosamente")

    # =========================================================

    def crear_vistas(self, cursor):

        cursor.execute("DROP VIEW IF EXISTS vista_equipos_completa")
        cursor.execute("DROP VIEW IF EXISTS vista_prestamos_activos")
        cursor.execute("DROP VIEW IF EXISTS vista_alertas_pendientes")
        cursor.execute(
            """
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
        """
        )

        cursor.execute(
        """
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
        """
    )
        cursor.execute(
        """
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
        """
    )

    def insertar_datos_iniciales(self, cursor):
        """Inserta datos de ejemplo en el sistema"""

        # =========================================================
        # ROLES INICIALES
        # =========================================================
        roles = [
            ("Administrador", "Acceso completo al sistema", '{"all": true}'),
            (
                "Instructor",
                "Gestión de prácticas y préstamos",
                '{"practicas": true, "prestamos": true, "consultas": true}',
            ),
            (
                "Técnico Laboratorio",
                "Mantenimiento y gestión de equipos",
                '{"equipos": true, "mantenimiento": true, "inventario": true}',
            ),
            (
                "Aprendiz",
                "Consulta de información y solicitud de préstamos",
                '{"consultas": true, "solicitar_prestamos": true}',
            ),
            (
                "Coordinador",
                "Supervisión y reportes",
                '{"reportes": true, "supervision": true, "consultas": true}',
            ),
        ]
        for rol in roles:
            cursor.execute(
                """
                INSERT IGNORE INTO roles (nombre_rol, descripcion, permisos)
                VALUES (%s, %s, %s)
                """,
                rol,
            )
        # =========================================================
        # CATEGORÍAS DE EQUIPOS
        # =========================================================
        categorias = [
            ("Microscopios", "Equipos de observación y análisis microscópico", "MICRO"),
            ("Balanzas", "Equipos de medición de masa y peso", "BAL"),
            ("Centrifugas", "Equipos de separación por centrifugación", "CENT"),
            ("Espectrofotómetros", "Equipos de análisis espectral", "ESPEC"),
            ("pH-metros", "Equipos de medición de pH", "PH"),
            ("Estufas", "Equipos de calentamiento y secado", "ESTUF"),
            ("Equipos Minería", "Equipos específicos para análisis minero", "MIN"),
            ("Equipos Suelos", "Equipos para análisis de suelos", "SUELO"),
            ("Instrumentos Medición", "Instrumentos generales de medición", "MED"),
            ("Reactivos", "Productos químicos y reactivos", "REACT"),
        ]
        for categoria in categorias:
            cursor.execute(
                """
                INSERT IGNORE INTO categorias_equipos (nombre, descripcion, codigo)
                VALUES (%s, %s, %s)
                """,
                categoria,
            )
        # =========================================================
        # TIPOS DE MANTENIMIENTO
        # =========================================================
        tipos_mantenimiento = [
            (
                "Mantenimiento Preventivo Mensual",
                "Revisión general mensual del equipo",
                30,
                True,
            ),
            (
                "Mantenimiento Preventivo Trimestral",
                "Mantenimiento detallado trimestral",
                90,
                True,
            ),
            ("Calibración", "Calibración de precisión del equipo", 180, True),
            ("Limpieza Profunda", "Limpieza y desinfección completa", 15, True),
            ("Mantenimiento Correctivo", "Reparación por falla o avería", 0, False),
            ("Revisión Anual", "Inspección completa anual", 365, True),
        ]
        for tipo in tipos_mantenimiento:
            cursor.execute(
                """
                INSERT IGNORE INTO tipos_mantenimiento (nombre, descripcion, frecuencia_dias, es_preventivo)
                VALUES (%s, %s, %s, %s)
                """,
                tipo,
            )
        # =========================================================
        # PROGRAMAS DE FORMACIÓN
        # =========================================================
        programas = [
            (
                "TEC-MIN-001",
                "Tecnología en Minería",
                "tecnologo",
                "Programa tecnológico en explotación minera",
                30,
            ),
            (
                "TEC-QUI-001",
                "Tecnología en Química",
                "tecnologo",
                "Programa tecnológico en análisis químico",
                30,
            ),
            (
                "TEC-SUE-001",
                "Tecnología en Análisis de Suelos",
                "tecnico",
                "Programa técnico en análisis y caracterización de suelos",
                18,
            ),
            (
                "TEC-MET-001",
                "Tecnología en Metalurgia",
                "tecnologo",
                "Programa tecnológico en procesos metalúrgicos",
                30,
            ),
        ]
        for programa in programas:
            cursor.execute(
                """
                INSERT IGNORE INTO programas_formacion (codigo_programa, nombre_programa, tipo_programa, descripcion, duracion_meses)
                VALUES (%s, %s, %s, %s, %s)
                """,
                programa,
            )
        # =========================================================
        # COMANDOS DE VOZ PARA LUCIA
        # =========================================================
        comandos_voz = [
            (
                "Lucia buscar equipo",
                "buscar_equipo",
                '{"tipo": "general"}',
                "Iniciando búsqueda de equipos disponibles",
            ),
            (
                "Lucia estado laboratorio",
                "consultar_laboratorio",
                '{"info": "estado"}',
                "Consultando estado actual de laboratorios",
            ),
            (
                "Lucia préstamo equipo",
                "solicitar_prestamo",
                '{"accion": "solicitar"}',
                "Iniciando proceso de solicitud de préstamo",
            ),
            (
                "Lucia inventario disponible",
                "consultar_inventario",
                '{"filtro": "disponible"}',
                "Mostrando inventario disponible",
            ),
            (
                "Lucia alertas mantenimiento",
                "consultar_alertas",
                '{"tipo": "mantenimiento"}',
                "Consultando alertas de mantenimiento pendientes",
            ),
            (
                "Lucia ayuda comandos",
                "mostrar_ayuda",
                '{"seccion": "comandos"}',
                "Mostrando comandos disponibles",
            ),
            (
                "Lucia estado préstamos",
                "consultar_prestamos",
                '{"estado": "activos"}',
                "Consultando préstamos activos",
            ),
            (
                "Lucia registrar devolución",
                "devolver_equipo",
                '{"accion": "devolver"}',
                "Iniciando proceso de devolución",
            ),
        ]
        for comando in comandos_voz:
            cursor.execute(
                """
                INSERT IGNORE INTO comandos_voz (comando_texto, intencion, parametros, respuesta_esperada)
                VALUES (%s, %s, %s, %s)
                """,
                comando,
            )
        # =========================================================
        # CAPACITACIONES DE PRUEBA
        # =========================================================
        capacitaciones = [
            (2, "Uso del asistente de voz Lucia", "2025-08-10", 4, 95),
            (3, "Reconocimiento de imágenes con MobileNet", "2025-08-12", 6, 88),
            (4, "Mantenimiento predictivo con ML", "2025-08-15", 5, 91),
            (5, "Gestión de prácticas con IA", "2025-09-05", 3, 85),
            (6, "Uso de dashboards en tiempo real", "2025-09-10", 2, 90),
            (7, "Seguridad y privacidad en IA", "2025-09-12", 4, 93),
            (8, "Resolución de conflictos con IA", "2025-09-20", 3, 87),
            (9, "Etiquetado de datos para entrenamiento", "2025-10-01", 5, 89),
            (10, "Evaluación de modelos de IA", "2025-10-05", 4, 92),
            (11, "Gestión del cambio tecnológico", "2025-10-10", 3, 86),
        ]
        for cap in capacitaciones:
            cursor.execute(
                """
                INSERT IGNORE INTO capacitaciones (id_usuario, tema, fecha, duracion_horas, calificacion)
                VALUES (%s, %s, %s, %s, %s)
                """,
                cap,
            )
        # =========================================================
        # ENCUESTAS DE PRUEBA
        # =========================================================
        encuestas = [
            (
                12,
                "prestamo",
                5,
                "El asistente Lucia me prestó el equipo en 10 segundos, ¡increíble!",
            ),
            (
                13,
                "practica",
                4,
                "Muy útil, pero a veces Lucia no entiende mi acento boyacense.",
            ),
            (
                14,
                "mantenimiento",
                5,
                "Me avisaron que el microscopio necesitaba calibración antes de que fallara.",
            ),
            (
                15,
                "general",
                4,
                "El sistema es rápido, pero falta más información en el dashboard.",
            ),
            (
                16,
                "prestamo",
                3,
                "El código QR no funcionó, tuve que usar el buscador manual.",
            ),
            (
                17,
                "practica",
                5,
                "La programación de prácticas fue muy fluida, sin conflictos.",
            ),
            (
                18,
                "general",
                5,
                "Se nota que el sistema aprende, cada vez reconoce mejor los equipos.",
            ),
            (
                19,
                "mantenimiento",
                4,
                "Buenas alertas, pero deberían llegar por email también.",
            ),
            (
                20,
                "prestamo",
                5,
                "Devolver el equipo con voz es súper cómodo, especialmente con guantes.",
            ),
            (
                21,
                "general",
                4,
                "Me gustaría poder reportar fallos directamente desde el sistema.",
            ),
        ]
        for encuesta in encuestas:
            cursor.execute(
                """
                INSERT IGNORE INTO encuestas (id_usuario, tipo, puntuacion, comentarios)
                VALUES (%s, %s, %s, %s)
                """,
                encuesta,
            )
        print("✅ Datos iniciales insertados")

    def ejecutar_consulta(self, query: str, params: tuple = None) -> List[tuple]:
        """Ejecuta una consulta SELECT y retorna resultados"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            resultados = cursor.fetchall()
            cursor.close()
            return resultados

        except Error as e:
            print(f"❌ Error ejecutando consulta: {e}")
            return []

    def ejecutar_comando(self, query: str, params: tuple = None) -> bool:
        """Ejecuta un comando INSERT, UPDATE o DELETE"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            cursor.close()
            return True

        except Error as e:
            print(f"❌ Error ejecutando comando: {e}")
            return False

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Conexión a MySQL cerrada")
