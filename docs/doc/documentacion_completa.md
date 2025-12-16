Documentación Técnica del Sistema GIL (Gestión Inteligente de Laboratorios)
Centro Minero de Sogamoso - SENA
🔹 1. Documentación General del Proyecto
📌 Nombre del Proyecto
Sistema de Gestión Inteligente de Laboratorios (GIL) v1.0

🎯 Objetivo General del Sistema
Desarrollar una plataforma integral de gestión de laboratorios que optimice los procesos de control de inventario, préstamos de equipos, mantenimiento predictivo, prácticas académicas y reconocimiento visual, incorporando inteligencia artificial para la automatización y mejora de la experiencia de usuario.

📐 Alcance del Sistema
Gestión de Usuarios y Roles: Sistema de autenticación con 6 niveles de acceso.

Gestión de Equipos e Inventario: Control completo de equipos de laboratorio con categorización y estados.

Sistema de Préstamos: Solicitud, aprobación y seguimiento de préstamos de equipos.

Mantenimiento Predictivo: Alertas y programación de mantenimiento con IA.

Prácticas de Laboratorio: Programación y gestión de prácticas académicas.

Reconocimiento de Imágenes (IA): Identificación de equipos mediante MobileNet.

Asistente de Voz (LUCIA): Interacción por comandos de voz para operaciones comunes.

Reportes y Estadísticas: Dashboards y exportación de datos (PDF/Excel).

Backup y Seguridad: Copias de seguridad automatizadas y logs de auditoría.

🛠️ Tecnologías Utilizadas
Tecnología	Versión	Propósito
Python	3.8+	Lenguaje principal del backend
Flask	2.3+	Framework web y API REST
MySQL	8.0+	Base de datos relacional
JWT (JSON Web Tokens)	-	Autenticación API
bcrypt	-	Hash de contraseñas
Flask-CORS	-	Habilitar CORS para API
Flask-Mail	-	Envío de notificaciones por email
OpenCV / TensorFlow	-	Reconocimiento de imágenes (IA)
MobileNet V2	-	Modelo de clasificación de imágenes
ReportLab	-	Generación de reportes PDF
openpyxl	-	Exportación a Excel
🏗️ Tipo de Arquitectura
Arquitectura REST API con separación clara entre:

Backend API: Flask con blueprints modulares

Frontend: Plantillas HTML/Jinja2 con JavaScript

Base de Datos: MySQL con conexión por pool

Servicios IA: Módulos independientes para reconocimiento y predicción

📁 Estructura General del Proyecto Flask
text
gil_laboratorios_1.0/
├── app.py                          # Punto de entrada principal
├── config/
│   ├── config.py                   # Configuración centralizada
│   ├── api_config.py              # Configuración específica de API
│   └── database_config.py         # Configuración de base de datos
├── backend/
│   ├── api/
│   │   ├── blueprints.py          # Registro de endpoints API
│   │   ├── auth.py               # Autenticación y JWT
│   │   ├── equipos.py            # Gestión de equipos
│   │   ├── prestamos.py          # Gestión de préstamos
│   │   ├── usuarios.py           # Gestión de usuarios
│   │   ├── roles.py              # Gestión de roles
│   │   ├── laboratorios.py       # Gestión de laboratorios
│   │   ├── practicas.py          # Gestión de prácticas
│   │   ├── mantenimiento.py      # Mantenimiento preventivo
│   │   ├── mantenimiento_predictivo.py  # IA predictiva
│   │   ├── reconocimiento_ia.py  # Reconocimiento de imágenes
│   │   ├── asistente_voz.py      # Asistente LUCIA
│   │   └── backups.py            # Copias de seguridad
│   ├── models/                    # Modelos de datos
│   ├── services/                  # Servicios de negocio
│   └── utils/                     # Utilidades
├── frontend/
│   ├── templates/                 # Plantillas HTML
│   └── static/                    # CSS, JS, imágenes
├── uploads/                       # Archivos subidos
├── logs/                         # Logs del sistema
└── .env                         # Variables de entorno
🔹 2. Seguridad y Autenticación
🔐 Tipo de Autenticación Utilizada
Autenticación Dual:

Sesiones Web: Para la interfaz web tradicional (Flask session)

JWT (JSON Web Tokens): Para API REST con expiración configurable

📋 Encabezados HTTP Requeridos (API)
http
# Para autenticación web (sesiones)
Cookie: session=<session_token>

# Para API REST (JWT)
Authorization: Bearer <jwt_token>
Content-Type: application/json
👥 Manejo de Roles y Permisos
Nivel	Rol	Descripción	Acceso API
6	Administrador	Acceso completo al sistema	/api/*
5	Coordinador	Supervisión y reportes	/api/reportes, /api/consultas
4	Instructor	Gestión de prácticas y préstamos	/api/practicas, /api/prestamos
3	Técnico Laboratorio	Mantenimiento y equipos	/api/equipos, /api/mantenimiento
2	Aprendiz	Consulta y préstamos propios	/api/prestamos (solo propios)
1	Usuario Básico	Solo lectura	/api/consultas
🛡️ Buenas Prácticas de Seguridad
Hash de contraseñas: bcrypt con salt

Validación de entrada: Sanitización en backend y frontend

CORS configurado: Orígenes específicos permitidos

Headers de seguridad: Protección contra XSS, Clickjacking

Logs de auditoría: Registro de todas las operaciones críticas

Tokens expirables: JWT con expiración configurable (default: 24h)

Rate limiting: En endpoints críticos (en implementación)

🔹 3. Convenciones de la API
🌐 URL Base
text
# Desarrollo
http://localhost:5000

# Producción
https://<dominio>
📌 Versionado
Versión actual: v1.0

Formato: Incluido en la URL base ()

Compatibilidad: Cambios breaking requieren nueva versión

📊 Formato de Intercambio de Datos
Request/Response: JSON (UTF-8)

Formato fechas: ISO 8601 (YYYY-MM-DDTHH:MM:SS)

Codificación: UTF-8

📊 Códigos de Estado HTTP
Código	Descripción	Uso
200	OK	Operación exitosa
201	Created	Recurso creado
400	Bad Request	Datos inválidos
401	Unauthorized	No autenticado
403	Forbidden	Sin permisos
404	Not Found	Recurso no existe
409	Conflict	Conflicto (ej: duplicado)
422	Unprocessable Entity	Validación fallida
500	Internal Server Error	Error del servidor
🏗️ Estructura de Respuestas
json
{
  "success": true|false,
  "message": "Mensaje descriptivo",
  "data": {} | [] | null,
  "errors": [],  // Solo cuando success=false
  "metadata": {  // Paginación, totales, etc.
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
❌ Manejo de Errores
json
// Error de validación
{
  "success": false,
  "message": "Error de validación",
  "errors": [
    {
      "field": "email",
      "message": "Formato de email inválido"
    }
  ]
}

// Error de autenticación
{
  "success": false,
  "message": "Token expirado o inválido",
  "code": "AUTH_EXPIRED"
}
🔹 4. Documentación Detallada de Endpoints
📍 Módulo de Autenticación (/auth)
POST /auth/login
Descripción: Autenticación de usuario con credenciales

Método: POST

Headers:

http
Content-Type: application/json
Body:

json
{
  "user_id": "123456789",
  "password": "P@ssw0rd123!"
}
Validaciones:

Documento: 6-20 dígitos

Contraseña: 8+ caracteres, mayúscula, minúscula, número, carácter especial

Response exitoso (200):

json
{
  "success": true,
  "message": "Login exitoso",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "documento": "123456789",
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "rol": "Administrador",
    "nivel_acceso": 5
  }
}
Response error (401):

json
{
  "success": false,
  "message": "Contraseña incorrecta"
}
Códigos HTTP: 200, 400, 401, 500

GET /auth/verify
Descripción: Verifica validez del token JWT

Método: GET

Headers:

http
Authorization: Bearer <token>
Response exitoso (200):

json
{
  "success": true,
  "user": {
    "id": 1,
    "documento": "123456789",
    "nombre": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "rol": "Administrador",
    "nivel_acceso": 5
  }
}
Códigos HTTP: 200, 401, 500

POST /auth/register
Descripción: Registro de nuevo usuario (estado inactivo)

Método: POST

Headers:

http
Content-Type: application/json
Body:

json
{
  "documento": "123456789",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@ejemplo.com",
  "password": "P@ssw0rd123!",
  "telefono": "3001234567"
}
Validaciones:

Documento único

Email único y válido

Teléfono opcional (7-15 dígitos)

Contraseña segura (8+ caracteres, mayúscula, minúscula, número, especial)

Response exitoso (201):

json
{
  "success": true,
  "message": "Registro exitoso. Su cuenta será activada por un administrador",
  "user_id": 1
}
Response error (409):

json
{
  "success": false,
  "message": "El documento ya está registrado"
}
Códigos HTTP: 201, 400, 409, 500

📍 Módulo de Equipos (/equipos)
GET /equipos
Descripción: Lista equipos con filtros opcionales

Método: GET

Headers:

http
Authorization: Bearer <token>
Query Parameters:

estado (opcional): disponible, prestado, mantenimiento, reparacion, dado_baja

laboratorio (opcional): ID del laboratorio

categoria (opcional): ID de categoría

q (opcional): Búsqueda por nombre o código

limit (opcional): Límite de resultados (default: 100)

Response exitoso (200):

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo_interno": "EQP-001",
      "nombre": "Microscopio Digital",
      "marca": "Olympus",
      "modelo": "CX23",
      "estado": "disponible",
      "estado_fisico": "bueno",
      "categoria_nombre": "Microscopios",
      "laboratorio_nombre": "Laboratorio de Química"
    }
  ],
  "total": 1,
  "metadata": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
Códigos HTTP: 200, 401, 403, 500

GET /equipos/{id}
Descripción: Obtiene detalle completo de un equipo

Método: GET

Path Parameters:

id (requerido): ID del equipo

Headers:

http
Authorization: Bearer <token>
Response exitoso (200):

json
{
  "success": true,
  "data": {
    "id": 1,
    "codigo_interno": "EQP-001",
    "codigo_qr": "QR_CODE_123",
    "nombre": "Microscopio Digital",
    "marca": "Olympus",
    "modelo": "CX23",
    "numero_serie": "SN123456",
    "descripcion": "Microscopio binocular para laboratorio",
    "especificaciones_tecnicas": "Aumento 40x-1000x, LED integrado",
    "valor_adquisicion": 2500000.00,
    "fecha_adquisicion": "2023-05-15",
    "proveedor": "Distribuidora Científica S.A.",
    "garantia_meses": 24,
    "vida_util_anos": 10,
    "imagen_url": "/uploads/equipos/microscopio.jpg",
    "estado": "disponible",
    "estado_fisico": "bueno",
    "ubicacion_especifica": "Estante A-12",
    "observaciones": "Calibrado en mayo 2024",
    "id_categoria": 1,
    "id_laboratorio": 1,
    "fecha_registro": "2023-05-20 10:30:00",
    "categoria_nombre": "Microscopios",
    "laboratorio_nombre": "Laboratorio de Química"
  }
}
Códigos HTTP: 200, 401, 403, 404, 500

GET /equipos/disponibles
Descripción: Lista equipos disponibles para préstamo

Método: GET

Headers:

http
Authorization: Bearer <token>
Response exitoso (200):

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo_interno": "EQP-001",
      "nombre": "Microscopio Digital",
      "marca": "Olympus",
      "modelo": "CX23",
      "estado_fisico": "bueno",
      "ubicacion_especifica": "Estante A-12",
      "categoria": "Microscopios",
      "laboratorio": "Laboratorio de Química"
    }
  ],
  "total": 1
}
Códigos HTTP: 200, 401, 403, 500

📍 Módulo de Préstamos (/prestamos)
GET /prestamos
Descripción: Lista préstamos con filtro por estado

Método: GET

Headers:

http
Authorization: Bearer <token>
Query Parameters:

estado (opcional): solicitado, aprobado, rechazado, activo, devuelto, vencido

usuario (opcional): ID del usuario (solo administradores)

Response exitoso (200):

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo": "PREST-ABC123",
      "fecha": "2024-01-15 09:30:00",
      "fecha_devolucion_programada": "2024-01-22 17:00:00",
      "fecha_devolucion_real": null,
      "estado": "activo",
      "proposito": "Práctica de microbiología",
      "equipo_nombre": "Microscopio Digital",
      "equipo_codigo": "EQP-001",
      "solicitante": "Juan Pérez"
    }
  ],
  "total": 1
}
Códigos HTTP: 200, 401, 403, 500

POST /prestamos
Descripción: Crea una nueva solicitud de préstamo

Método: POST

Headers:

http
Authorization: Bearer <token>
Content-Type: application/json
Body:

json
{
  "id_equipo": 1,
  "proposito": "Práctica de microbiología",
  "fecha_devolucion_programada": "2024-01-22T17:00:00"
}
Validaciones:

Equipo debe existir y estar disponible

Fecha de devolución debe ser futura

Usuario debe tener nivel suficiente para préstamos

Response exitoso (201):

json
{
  "success": true,
  "message": "Préstamo solicitado exitosamente",
  "data": {
    "id": 1,
    "codigo": "PREST-ABC123"
  }
}
Response error (400):

json
{
  "success": false,
  "message": "Equipo no disponible"
}
Códigos HTTP: 201, 400, 401, 403, 500

POST /prestamos/{id}/aprobar
Descripción: Aprueba un préstamo solicitado

Método: POST

Path Parameters:

id (requerido): ID del préstamo

Headers:

http
Authorization: Bearer <token>
Content-Type: application/json
Body:

json
{
  "observaciones": "Aprobado para uso académico"
}
Validaciones:

Requiere nivel 3+ (Instructor o superior)

Préstamo debe estar en estado "solicitado"

Response exitoso (200):

json
{
  "success": true,
  "message": "Préstamo aprobado"
}
Códigos HTTP: 200, 400, 401, 403, 404, 500

POST /prestamos/{id}/devolver
Descripción: Registra devolución de equipo

Método: POST

Path Parameters:

id (requerido): ID del préstamo

Headers:

http
Authorization: Bearer <token>
Content-Type: application/json
Body:

json
{
  "observaciones": "Equipo devuelto en buen estado",
  "calificacion": "bueno"
}
Validaciones:

Préstamo debe estar en estado "activo"

Calificación opcional: excelente, bueno, regular, malo

Response exitoso (200):

json
{
  "success": true,
  "message": "Devolución registrada"
}
Códigos HTTP: 200, 400, 401, 403, 404, 500

📍 Módulo de Usuarios (/usuarios)
GET /usuarios
Descripción: Lista usuarios (solo administradores)

Método: GET

Headers:

http
Authorization: Bearer <token>
Query Parameters:

estado (opcional): activo, inactivo, suspendido

rol (opcional): ID del rol

Validaciones:

Requiere nivel 3+ (Técnico o superior)

Response exitoso (200):

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "documento": "123456789",
      "nombres": "Juan",
      "apellidos": "Pérez",
      "email": "juan@ejemplo.com",
      "telefono": "3001234567",
      "estado": "activo",
      "nombre_rol": "Administrador"
    }
  ],
  "total": 1
}
Códigos HTTP: 200, 401, 403, 500

📍 Módulo de Estadísticas (/estadisticas)
GET /estadisticas/dashboard
Descripción: Estadísticas para dashboard

Método: GET

Headers:

http
Authorization: Bearer <token>
Response exitoso (200):

json
{
  "success": true,
  "data": {
    "equipos_estado": {
      "disponible": 45,
      "prestado": 12,
      "mantenimiento": 3,
      "reparacion": 2,
      "dado_baja": 1
    },
    "prestamos_activos": 12,
    "usuarios_activos": 85,
    "alertas_pendientes": 5
  }
}
Códigos HTTP: 200, 401, 500

📍 Módulo de Laboratorios (/laboratorios)
GET /laboratorios
Descripción: Lista laboratorios

Método: GET

Headers:

http
Authorization: Bearer <token>
Query Parameters:

tipo (opcional): quimica, mineria, suelos, metalurgia, general

estado (opcional): disponible, ocupado, mantenimiento, fuera_servicio

Response exitoso (200):

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo_lab": "LAB-QUIM-01",
      "nombre": "Laboratorio de Química",
      "tipo": "quimica",
      "ubicacion": "Edificio C, Piso 2",
      "capacidad_personas": 25,
      "estado": "disponible",
      "responsable": "María González"
    }
  ],
  "total": 1
}
Códigos HTTP: 200, 401, 500

📍 Health Check (/health)
GET /health
Descripción: Verifica estado del API y base de datos

Método: GET

Response exitoso (200):

json
{
  "success": true,
  "status": "ok",
  "database": "ok",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
Códigos HTTP: 200, 503 (si base de datos no responde)

🔹 5. Modelos de Datos
📊 Entidades Principales
1. Usuarios (usuarios)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
documento	VARCHAR(20)	Número de documento	UNIQUE, NOT NULL
nombres	VARCHAR(100)	Nombres del usuario	NOT NULL
apellidos	VARCHAR(100)	Apellidos del usuario	NOT NULL
email	VARCHAR(150)	Correo electrónico	UNIQUE
telefono	VARCHAR(15)	Teléfono de contacto	
id_rol	INT	Rol del usuario	FK a roles.id
password_hash	VARCHAR(255)	Hash de contraseña	
fecha_registro	TIMESTAMP	Fecha de registro	DEFAULT CURRENT_TIMESTAMP
ultimo_acceso	TIMESTAMP	Último acceso	
estado	ENUM	Estado del usuario	'activo', 'inactivo', 'suspendido'
2. Roles (roles)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
nombre_rol	VARCHAR(50)	Nombre del rol	UNIQUE, NOT NULL
descripcion	TEXT	Descripción del rol	
permisos	TEXT	Permisos en formato JSON	
fecha_creacion	TIMESTAMP	Fecha de creación	DEFAULT CURRENT_TIMESTAMP
estado	ENUM	Estado del rol	'activo', 'inactivo'
3. Equipos (equipos)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
codigo_interno	VARCHAR(50)	Código interno único	UNIQUE, NOT NULL
codigo_qr	VARCHAR(255)	Código QR para escaneo	UNIQUE
nombre	VARCHAR(200)	Nombre del equipo	NOT NULL
marca	VARCHAR(100)	Marca del equipo	
modelo	VARCHAR(100)	Modelo del equipo	
numero_serie	VARCHAR(150)	Número de serie	
id_categoria	INT	Categoría del equipo	FK a categorias_equipos.id
id_laboratorio	INT	Laboratorio asignado	FK a laboratorios.id
descripcion	TEXT	Descripción general	
especificaciones_tecnicas	TEXT	Especificaciones técnicas	
valor_adquisicion	DECIMAL(12,2)	Valor de adquisición	
fecha_adquisicion	DATE	Fecha de adquisición	
proveedor	VARCHAR(200)	Proveedor del equipo	
garantia_meses	INT	Meses de garantía	DEFAULT 12
vida_util_anos	INT	Vida útil en años	DEFAULT 5
imagen_url	VARCHAR(500)	URL de la imagen	
imagen_hash	VARCHAR(64)	Hash para reconocimiento	
estado	ENUM	Estado operativo	'disponible', 'prestado', 'mantenimiento', 'reparacion', 'dado_baja'
estado_fisico	ENUM	Estado físico	'excelente', 'bueno', 'regular', 'malo'
ubicacion_especifica	VARCHAR(200)	Ubicación específica	
observaciones	TEXT	Observaciones adicionales	
fecha_registro	TIMESTAMP	Fecha de registro	DEFAULT CURRENT_TIMESTAMP
fecha_actualizacion	TIMESTAMP	Última actualización	DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
4. Préstamos (prestamos)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
codigo	VARCHAR(30)	Código único del préstamo	UNIQUE, NOT NULL
id_equipo	INT	Equipo prestado	FK a equipos.id, NOT NULL
id_usuario_solicitante	INT	Usuario solicitante	FK a usuarios.id, NOT NULL
id_usuario_autorizador	INT	Usuario que autorizó	FK a usuarios.id
fecha_solicitud	TIMESTAMP	Fecha de solicitud	DEFAULT CURRENT_TIMESTAMP
fecha	DATETIME	Fecha del préstamo	
fecha_devolucion_programada	DATETIME	Fecha programada para devolución	
fecha_devolucion_real	DATETIME	Fecha real de devolución	
proposito	TEXT	Propósito del préstamo	
observaciones	TEXT	Observaciones del préstamo	
observaciones_devolucion	TEXT	Observaciones de devolución	
estado	ENUM	Estado del préstamo	'solicitado', 'aprobado', 'rechazado', 'activo', 'devuelto', 'vencido'
calificacion_devolucion	ENUM	Calificación de devolución	'excelente', 'bueno', 'regular', 'malo'
5. Laboratorios (laboratorios)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
codigo_lab	VARCHAR(20)	Código del laboratorio	UNIQUE, NOT NULL
nombre	VARCHAR(100)	Nombre del laboratorio	NOT NULL
tipo	ENUM	Tipo de laboratorio	'quimica', 'mineria', 'suelos', 'metalurgia', 'general'
ubicacion	VARCHAR(200)	Ubicación física	
capacidad_personas	INT	Capacidad máxima	DEFAULT 20
area_m2	DECIMAL(8,2)	Área en metros cuadrados	
responsable_id	INT	Responsable del laboratorio	FK a usuarios.id
estado	ENUM	Estado del laboratorio	'disponible', 'ocupado', 'mantenimiento', 'fuera_servicio'
fecha_creacion	TIMESTAMP	Fecha de creación	DEFAULT CURRENT_TIMESTAMP
6. Categorías de Equipos (categorias_equipos)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
nombre	VARCHAR(100)	Nombre de la categoría	NOT NULL
descripcion	TEXT	Descripción	
codigo	VARCHAR(20)	Código único	UNIQUE
fecha_creacion	TIMESTAMP	Fecha de creación	DEFAULT CURRENT_TIMESTAMP
7. Mantenimiento (historial_mantenimiento)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
id_equipo	INT	Equipo mantenido	FK a equipos.id, NOT NULL
id_tipo_mantenimiento	INT	Tipo de mantenimiento	FK a tipos_mantenimiento.id, NOT NULL
fecha_inicio	DATETIME	Fecha de inicio	NOT NULL
fecha_fin	DATETIME	Fecha de finalización	
tecnico_responsable_id	INT	Técnico responsable	FK a usuarios.id
descripcion_trabajo	TEXT	Descripción del trabajo realizado	
partes_reemplazadas	TEXT	Partes reemplazadas	
costo_mantenimiento	DECIMAL(10,2)	Costo del mantenimiento	
tiempo_inactividad_horas	DECIMAL(5,2)	Tiempo de inactividad	
observaciones	TEXT	Observaciones	
estado_post_mantenimiento	ENUM	Estado después del mantenimiento	'excelente', 'bueno', 'regular', 'malo'
proxima_fecha_mantenimiento	DATE	Próximo mantenimiento programado	
fecha_registro	TIMESTAMP	Fecha de registro	DEFAULT CURRENT_TIMESTAMP
8. Prácticas de Laboratorio (practicas_laboratorio)
Campo	Tipo	Descripción	Restricciones
id	INT	ID único	PK, AUTO_INCREMENT
codigo	VARCHAR(30)	Código único	UNIQUE, NOT NULL
nombre	VARCHAR(200)	Nombre de la práctica	NOT NULL
id_programa	INT	Programa de formación	FK a programas_formacion.id, NOT NULL
id_laboratorio	INT	Laboratorio asignado	FK a laboratorios.id, NOT NULL
id_instructor	INT	Instructor responsable	FK a instructores.id, NOT NULL
fecha	DATETIME	Fecha y hora	NOT NULL
duracion_horas	DECIMAL(3,1)	Duración en horas	
numero_estudiantes	INT	Número de estudiantes	
equipos_requeridos	TEXT	Equipos requeridos (JSON array)	
materiales_requeridos	TEXT	Materiales requeridos	
objetivos	TEXT	Objetivos de la práctica	
descripcion_actividades	TEXT	Descripción de actividades	
observaciones	TEXT	Observaciones	
estado	ENUM	Estado de la práctica	'programada', 'en_curso', 'completada', 'cancelada'
fecha_registro	TIMESTAMP	Fecha de registro	DEFAULT CURRENT_TIMESTAMP
🔗 Relaciones entre Entidades




























🔹 6. Documentación Swagger / OpenAPI
📄 Especificación OpenAPI 3.0 (YAML)
yaml
openapi: 3.0.3
info:
  title: Sistema GIL - API REST
  description: API para Gestión Inteligente de Laboratorios - Centro Minero SENA
  version: 1.0.0
  contact:
    name: Centro Minero de Sogamoso - SENA
    url: https://centrominero.sena.edu.co
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:5000
    description: Servidor de desarrollo
  - url: https://api.centrominero.edu.co
    description: Servidor de producción

tags:
  - name: Autenticación
    description: Endpoints para login, registro y gestión de tokens
  - name: Equipos
    description: Gestión de equipos de laboratorio
  - name: Préstamos
    description: Gestión de préstamos de equipos
  - name: Usuarios
    description: Gestión de usuarios del sistema
  - name: Estadísticas
    description: Datos estadísticos para dashboards
  - name: Laboratorios
    description: Gestión de laboratorios
  - name: Salud
    description: Health checks y estado del sistema

paths:
  /auth/login:
    post:
      tags:
        - Autenticación
      summary: Autenticación de usuario
      description: Autentica un usuario con credenciales y retorna token JWT
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: Login exitoso
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '400':
          description: Datos inválidos
        '401':
          description: Credenciales incorrectas
        '500':
          description: Error interno del servidor

  /equipos:
    get:
      tags:
        - Equipos
      summary: Lista equipos
      description: Retorna lista de equipos con filtros opcionales
      security:
        - BearerAuth: []
      parameters:
        - in: query
          name: estado
          schema:
            type: string
            enum: [disponible, prestado, mantenimiento, reparacion, dado_baja]
          description: Filtro por estado del equipo
        - in: query
          name: laboratorio
          schema:
            type: integer
          description: Filtro por ID de laboratorio
        - in: query
          name: categoria
          schema:
            type: integer
          description: Filtro por ID de categoría
        - in: query
          name: q
          schema:
            type: string
          description: Búsqueda por nombre o código
      responses:
        '200':
          description: Lista de equipos
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EquiposListResponse'
        '401':
          description: No autenticado
        '403':
          description: Sin permisos
        '500':
          description: Error interno

  /equipos/{id}:
    get:
      tags:
        - Equipos
      summary: Obtiene detalle de equipo
      description: Retorna información completa de un equipo específico
      security:
        - BearerAuth: []
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: integer
          description: ID del equipo
      responses:
        '200':
          description: Detalle del equipo
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/EquipoDetailResponse'
        '401':
          description: No autenticado
        '403':
          description: Sin permisos
        '404':
          description: Equipo no encontrado
        '500':
          description: Error interno

  /prestamos:
    get:
      tags:
        - Préstamos
      summary: Lista préstamos
      description: Retorna lista de préstamos con filtros
      security:
        - BearerAuth: []
      parameters:
        - in: query
          name: estado
          schema:
            type: string
            enum: [solicitado, aprobado, rechazado, activo, devuelto, vencido]
          description: Filtro por estado del préstamo
      responses:
        '200':
          description: Lista de préstamos
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PrestamosListResponse'
        '401':
          description: No autenticado
        '403':
          description: Sin permisos
        '500':
          description: Error interno

    post:
      tags:
        - Préstamos
      summary: Crea nueva solicitud de préstamo
      description: Crea una solicitud de préstamo para un equipo disponible
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PrestamoCreateRequest'
      responses:
        '201':
          description: Préstamo creado exitosamente
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PrestamoCreateResponse'
        '400':
          description: Datos inválidos o equipo no disponible
        '401':
          description: No autenticado
        '403':
          description: Sin permisos
        '500':
          description: Error interno

  /prestamos/{id}/aprobar:
    post:
      tags:
        - Préstamos
      summary: Aprueba un préstamo
      description: Aprueba una solicitud de préstamo pendiente
      security:
        - BearerAuth: []
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: integer
          description: ID del préstamo
      responses:
        '200':
          description: Préstamo aprobado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StandardResponse'
        '400':
          description: Préstamo no puede ser aprobado
        '401':
          description: No autenticado
        '403':
          description: Sin permisos (nivel insuficiente)
        '404':
          description: Préstamo no encontrado
        '500':
          description: Error interno

  /health:
    get:
      tags:
        - Salud
      summary: Health check
      description: Verifica estado del API y base de datos
      responses:
        '200':
          description: Sistema operativo
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '503':
          description: Servicio no disponible (BD caída)

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    LoginRequest:
      type: object
      required:
        - user_id
        - password
      properties:
        user_id:
          type: string
          description: ID de usuario o documento
          example: "123456789"
        password:
          type: string
          description: Contraseña del usuario
          example: "P@ssw0rd123!"
    
    LoginResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        message:
          type: string
          example: "Login exitoso"
        access_token:
          type: string
          description: Token JWT para autenticación
        user:
          $ref: '#/components/schemas/UserProfile'
    
    UserProfile:
      type: object
      properties:
        id:
          type: integer
          example: 1
        documento:
          type: string
          example: "123456789"
        nombre:
          type: string
          example: "Juan Pérez"
        email:
          type: string
          example: "juan@ejemplo.com"
        rol:
          type: string
          example: "Administrador"
        nivel_acceso:
          type: integer
          example: 5
    
    EquiposListResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        data:
          type: array
          items:
            $ref: '#/components/schemas/EquipoBasic'
        total:
          type: integer
          example: 1
    
    EquipoBasic:
      type: object
      properties:
        id:
          type: integer
          example: 1
        codigo_interno:
          type: string
          example: "EQP-001"
        nombre:
          type: string
          example: "Microscopio Digital"
        marca:
          type: string
          example: "Olympus"
        modelo:
          type: string
          example: "CX23"
        estado:
          type: string
          example: "disponible"
        categoria_nombre:
          type: string
          example: "Microscopios"
        laboratorio_nombre:
          type: string
          example: "Laboratorio de Química"
    
    EquipoDetailResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        data:
          $ref: '#/components/schemas/EquipoFull'
    
    EquipoFull:
      type: object
      properties:
        id:
          type: integer
          example: 1
        codigo_interno:
          type: string
          example: "EQP-001"
        codigo_qr:
          type: string
          example: "QR_CODE_123"
        nombre:
          type: string
          example: "Microscopio Digital"
        marca:
          type: string
          example: "Olympus"
        modelo:
          type: string
          example: "CX23"
        numero_serie:
          type: string
          example: "SN123456"
        descripcion:
          type: string
          example: "Microscopio binocular para laboratorio"
        especificaciones_tecnicas:
          type: string
          example: "Aumento 40x-1000x, LED integrado"
        valor_adquisicion:
          type: number
          format: float
          example: 2500000.00
        fecha_adquisicion:
          type: string
          format: date
          example: "2023-05-15"
        proveedor:
          type: string
          example: "Distribuidora Científica S.A."
        garantia_meses:
          type: integer
          example: 24
        vida_util_anos:
          type: integer
          example: 10
        imagen_url:
          type: string
          example: "/uploads/equipos/microscopio.jpg"
        estado:
          type: string
          example: "disponible"
        estado_fisico:
          type: string
          example: "bueno"
        ubicacion_especifica:
          type: string
          example: "Estante A-12"
        observaciones:
          type: string
          example: "Calibrado en mayo 2024"
        id_categoria:
          type: integer
          example: 1
        id_laboratorio:
          type: integer
          example: 1
        fecha_registro:
          type: string
          format: date-time
          example: "2023-05-20T10:30:00Z"
        categoria_nombre:
          type: string
          example: "Microscopios"
        laboratorio_nombre:
          type: string
          example: "Laboratorio de Química"
    
    PrestamosListResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        data:
          type: array
          items:
            $ref: '#/components/schemas/PrestamoBasic'
        total:
          type: integer
          example: 1
    
    PrestamoBasic:
      type: object
      properties:
        id:
          type: integer
          example: 1
        codigo:
          type: string
          example: "PREST-ABC123"
        fecha:
          type: string
          format: date-time
          example: "2024-01-15T09:30:00Z"
        fecha_devolucion_programada:
          type: string
          format: date-time
          example: "2024-01-22T17:00:00Z"
        fecha_devolucion_real:
          type: string
          format: date-time
          nullable: true
        estado:
          type: string
          example: "activo"
        proposito:
          type: string
          example: "Práctica de microbiología"
        equipo_nombre:
          type: string
          example: "Microscopio Digital"
        equipo_codigo:
          type: string
          example: "EQP-001"
        solicitante:
          type: string
          example: "Juan Pérez"
    
    PrestamoCreateRequest:
      type: object
      required:
        - id_equipo
        - proposito
        - fecha_devolucion_programada
      properties:
        id_equipo:
          type: integer
          example: 1
        proposito:
          type: string
          example: "Práctica de microbiología"
        fecha_devolucion_programada:
          type: string
          format: date-time
          example: "2024-01-22T17:00:00Z"
    
    PrestamoCreateResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        message:
          type: string
          example: "Préstamo solicitado exitosamente"
        data:
          type: object
          properties:
            id:
              type: integer
              example: 1
            codigo:
              type: string
              example: "PREST-ABC123"
    
    StandardResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        message:
          type: string
          example: "Operación exitosa"
    
    HealthResponse:
      type: object
      properties:
        success:
          type: boolean
          example: true
        status:
          type: string
          example: "ok"
        database:
          type: string
          example: "ok"
        version:
          type: string
          example: "1.0.0"
        timestamp:
          type: string
          format: date-time
🔹 7. Buenas Prácticas
🚨 Manejo de Errores
Validación en capas:

Frontend: Validación inmediata con JavaScript

Backend: Validación exhaustiva con regex y reglas de negocio

Base de datos: Constraints y triggers

Logs estructurados:

Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL

Contexto: Usuario, IP, acción, resultado

Almacenamiento: Base de datos + archivos rotativos

Respuestas informativas:

Mensajes claros para usuarios finales

Códigos de error para desarrolladores

Sugerencias cuando sea apropiado

🔒 Seguridad
Autenticación:

bcrypt para hash de contraseñas

JWT con expiración corta (24h)

Refresh tokens para sesiones prolongadas

Autorización:

Sistema de roles jerárquico (niveles 1-6)

Permisos granulares por módulo

Validación en cada endpoint

Protección de datos:

Sanitización de entrada/salida

Prepared statements para SQL

Encriptación de datos sensibles en tránsito

⚡ Rendimiento
Base de datos:

Pool de conexiones MySQL

Índices en campos de búsqueda frecuente

Vistas materializadas para consultas complejas

Caché:

Redis para sesiones y datos frecuentes

Cache headers en respuestas estáticas

Invalidación inteligente de caché

Optimización:

Paginación en listados grandes

Lazy loading de relaciones

Compresión de respuestas JSON

📈 Escalabilidad
Arquitectura:

Separación clara frontend/backend

Microservicios para funcionalidades IA

API gateway para gestión de rutas

Despliegue:

Contenedores Docker para consistencia

Orquestación con Docker Compose/Kubernetes

Load balancing para alta disponibilidad

Monitoreo:

Métricas de rendimiento en tiempo real

Alertas automáticas para errores críticos

Dashboard de salud del sistema


📋 Conclusión
Esta documentación técnica proporciona una visión completa del Sistema de Gestión Inteligente de Laboratorios (GIL) desarrollado para el Centro Minero de Sogamoso - SENA. El sistema implementa las mejores prácticas de desarrollo web moderno, seguridad, y arquitectura escalable, cumpliendo con los estándares académicos y profesionales requeridos.

🔧 Características Destacadas:
✅ API REST completa con autenticación JWT

✅ Base de datos MySQL con esquema normalizado

✅ Sistema de roles y permisos granular

✅ Integración IA para reconocimiento de imágenes

✅ Asistente de voz LUCIA para interacción natural

✅ Sistema de notificaciones por email

✅ Backup automático de base de datos

✅ Reportes exportables en PDF y Excel

✅ Documentación completa con OpenAPI/Swagger

🎓 Valor para SENA:
Evidencia de aprendizaje: Implementación completa de múltiples tecnologías

Portafolio profesional: Sistema listo para producción

Base para investigación: Plataforma para proyectos de IA

Herramienta educativa: Sistema real para prácticas de aprendices

Esta documentación está lista para:

✅ Entrega académica SENA

✅ Uso por desarrolladores para extensión del sistema

✅ Publicación en Swagger UI para pruebas de API

✅ Conversión directa a Word o PDF para presentaciones formales

