# 🔧 Componentes del Sistema GIL

## Módulos Principales

### 1. Módulo de Autenticación y Seguridad (auth)
**Responsabilidad**: Gestión de usuarios, roles y permisos

**Componentes**:
- `auth.py` - Autenticación JWT y sesiones
- `roles.py` - Gestión de roles y permisos
- `middleware.py` - Validación de acceso
- `password_reset.py` - Recuperación de contraseñas

**Dependencias**: bcrypt, PyJWT, Flask-Session

### 2. Módulo de Gestión de Equipos (equipos)
**Responsabilidad**: CRUD completo de equipos de laboratorio

**Componentes**:
- `equipos.py` - Operaciones básicas de equipos
- `categorias.py` - Gestión de categorías
- `inventario.py` - Control de stock y estados
- `qr_generator.py` - Generación de códigos QR

**Dependencias**: qrcode, Pillow, reportlab

### 3. Módulo de Préstamos (prestamos)
**Responsabilidad**: Sistema completo de préstamos

**Componentes**:
- `prestamos.py` - Solicitud y gestión
- `aprobaciones.py` - Flujo de aprobación
- `devoluciones.py` - Registro de devoluciones
- `alertas.py` - Notificaciones de vencimiento

**Dependencias**: Flask-Mail, schedule

### 4. Módulo de Laboratorios (laboratorios)
**Responsabilidad**: Gestión de espacios físicos

**Componentes**:
- `laboratorios.py` - CRUD de laboratorios
- `espacios.py` - Gestión de ubicaciones
- `reservas.py` - Calendario de uso

**Dependencias**: FullCalendar (JS), dateutil

### 5. Módulo de Prácticas (practicas)
**Responsabilidad**: Gestión académica de prácticas

**Componentes**:
- `practicas.py` - Programación de prácticas
- `programas.py` - Programas de formación
- `instructores.py` - Gestión de instructores
- `materiales.py` - Listas de materiales

**Dependencias**: Pandas, openpyxl

### 6. Módulo de Mantenimiento (mantenimiento)
**Responsabilidad**: Sistema predictivo y preventivo

**Componentes**:
- `mantenimiento.py` - Registro histórico
- `predictivo.py` - Modelos predictivos
- `alertas_mtto.py` - Sistema de alertas
- `calendario_mtto.py` - Programación

**Dependencias**: scikit-learn, numpy

### 7. Módulo de Inteligencia Artificial (ia)
**Responsabilidad**: Funcionalidades avanzadas de IA

**Componentes**:
- `reconocimiento.py` - Clasificación de imágenes
- `voz.py` - Asistente LUCIA
- `modelos.py` - Gestión de modelos IA
- `entrenamiento.py` - Entrenamiento de modelos

**Dependencias**: TensorFlow, OpenCV, SpeechRecognition

### 8. Módulo de Reportes (reportes)
**Responsabilidad**: Generación de informes

**Componentes**:
- `reportes.py` - Generación básica
- `dashboard.py` - Estadísticas en tiempo real
- `export.py` - Exportación PDF/Excel
- `graficos.py` - Visualización de datos

**Dependencias**: ReportLab, matplotlib, plotly

### 9. Módulo de Configuración (config)
**Responsabilidad**: Configuración del sistema

**Componentes**:
- `config.py` - Configuración central
- `settings.py` - Ajustes por entorno
- `constants.py` - Constantes del sistema
- `env_loader.py` - Carga de variables

### 10. Módulo de Utilidades (utils)
**Responsabilidad**: Funciones auxiliares

**Componentes**:
- `validators.py` - Validación de datos
- `formatters.py` - Formateo
- `helpers.py` - Funciones helper
- `loggers.py` - Sistema de logging

## Interacciones entre Componentes
