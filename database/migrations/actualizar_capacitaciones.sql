-- =========================================================
-- Actualización de tabla de capacitaciones
-- Programa Formativo en Tecnologías IA
-- Centro Minero SENA - Sistema GIL
-- =========================================================

USE gil_laboratorios;

-- Modificar tabla de capacitaciones para incluir nuevos campos
ALTER TABLE capacitaciones 
ADD COLUMN IF NOT EXISTS tipo_capacitacion ENUM('modulo_formativo', 'taller', 'material_didactico', 'gestion_cambio') DEFAULT 'taller' AFTER descripcion,
ADD COLUMN IF NOT EXISTS producto VARCHAR(200) AFTER tipo_capacitacion,
ADD COLUMN IF NOT EXISTS medicion VARCHAR(200) AFTER producto,
ADD COLUMN IF NOT EXISTS cantidad_meta INT AFTER medicion,
ADD COLUMN IF NOT EXISTS cantidad_actual INT DEFAULT 0 AFTER cantidad_meta,
ADD COLUMN IF NOT EXISTS actividad VARCHAR(300) AFTER cantidad_actual,
ADD COLUMN IF NOT EXISTS porcentaje_avance DECIMAL(5,2) DEFAULT 0.00 AFTER actividad,
ADD COLUMN IF NOT EXISTS recursos_asociados TEXT AFTER porcentaje_avance,
ADD COLUMN IF NOT EXISTS participantes TEXT AFTER recursos_asociados;

-- Insertar datos del programa formativo en IA
INSERT INTO capacitaciones (
    titulo, descripcion, tipo_capacitacion, producto, medicion, 
    cantidad_meta, cantidad_actual, actividad, duracion_horas, 
    fecha_inicio, fecha_fin, estado, id_instructor, porcentaje_avance
) VALUES
-- Módulo 1: Programa formativo en tecnologías IA
(
    'Módulo 1: Fundamentos de Inteligencia Artificial',
    'Introducción a conceptos básicos de IA, Machine Learning y Deep Learning aplicados al laboratorio',
    'modulo_formativo',
    'Programa formativo en tecnologías IA',
    'Número de módulos formativos',
    5,
    1,
    'Actividad 1: Diseñar programa de formación en tecnologías IA',
    40,
    '2025-01-15',
    '2025-02-15',
    'programada',
    NULL,
    20.00
),
(
    'Módulo 2: Reconocimiento de Imágenes con IA',
    'Aplicación de redes neuronales convolucionales para reconocimiento de equipos de laboratorio',
    'modulo_formativo',
    'Programa formativo en tecnologías IA',
    'Número de módulos formativos',
    5,
    1,
    'Actividad 1: Diseñar programa de formación en tecnologías IA',
    40,
    '2025-02-20',
    '2025-03-20',
    'programada',
    NULL,
    20.00
),
(
    'Módulo 3: Procesamiento de Voz con IA',
    'Implementación de asistentes virtuales y reconocimiento de comandos de voz',
    'modulo_formativo',
    'Programa formativo en tecnologías IA',
    'Número de módulos formativos',
    5,
    1,
    'Actividad 1: Diseñar programa de formación en tecnologías IA',
    40,
    '2025-03-25',
    '2025-04-25',
    'programada',
    NULL,
    20.00
),
(
    'Módulo 4: IA Predictiva para Mantenimiento',
    'Modelos predictivos para anticipar necesidades de mantenimiento de equipos',
    'modulo_formativo',
    'Programa formativo en tecnologías IA',
    'Número de módulos formativos',
    5,
    1,
    'Actividad 1: Diseñar programa de formación en tecnologías IA',
    40,
    '2025-05-01',
    '2025-06-01',
    'programada',
    NULL,
    20.00
),
(
    'Módulo 5: Integración y Despliegue de Modelos IA',
    'Implementación práctica de modelos IA en el sistema de laboratorio',
    'modulo_formativo',
    'Programa formativo en tecnologías IA',
    'Número de módulos formativos',
    5,
    1,
    'Actividad 1: Diseñar programa de formación en tecnologías IA',
    40,
    '2025-06-05',
    '2025-07-05',
    'programada',
    NULL,
    20.00
),

-- Talleres prácticos
(
    'Taller: Reconocimiento Facial para Acceso al Sistema',
    'Taller práctico sobre implementación de reconocimiento facial en el sistema GIL',
    'taller',
    'Personal capacitado en nuevas tecnologías',
    'Número de personas capacitadas',
    33,
    0,
    'Actividad 2: Realizar talleres de tecnologías de voz e imagen',
    8,
    '2025-02-10',
    '2025-02-10',
    'programada',
    NULL,
    0.00
),
(
    'Taller: Asistente de Voz LUCIA - Configuración y Uso',
    'Capacitación en el uso y configuración del asistente de voz del sistema',
    'taller',
    'Personal capacitado en nuevas tecnologías',
    'Número de personas capacitadas',
    33,
    0,
    'Actividad 2: Realizar talleres de tecnologías de voz e imagen',
    6,
    '2025-03-15',
    '2025-03-15',
    'programada',
    NULL,
    0.00
),
(
    'Taller: Reconocimiento de Equipos por Imagen',
    'Uso práctico del sistema de reconocimiento de equipos mediante fotografías',
    'taller',
    'Personal capacitado en nuevas tecnologías',
    'Número de personas capacitadas',
    33,
    0,
    'Actividad 2: Realizar talleres de tecnologías de voz e imagen',
    6,
    '2025-04-10',
    '2025-04-10',
    'programada',
    NULL,
    0.00
),

-- Material didáctico
(
    'Desarrollo de Guías de Usuario del Sistema GIL',
    'Creación de manuales y guías interactivas para usuarios del sistema',
    'material_didactico',
    'Material didáctico multimedia',
    'Número de recursos creados',
    20,
    5,
    'Actividad 3: Desarrollar material didáctico sobre el sistema',
    120,
    '2025-01-10',
    '2025-06-30',
    'activo',
    NULL,
    25.00
),
(
    'Videos Tutoriales de Funcionalidades IA',
    'Serie de videos explicativos sobre las funcionalidades de IA del sistema',
    'material_didactico',
    'Material didáctico multimedia',
    'Número de recursos creados',
    20,
    3,
    'Actividad 3: Desarrollar material didáctico sobre el sistema',
    80,
    '2025-02-01',
    '2025-06-30',
    'activo',
    NULL,
    15.00
),
(
    'Infografías de Procesos del Sistema',
    'Infografías visuales de los procesos clave del sistema de laboratorio',
    'material_didactico',
    'Material didáctico multimedia',
    'Número de recursos creados',
    20,
    2,
    'Actividad 3: Desarrollar material didáctico sobre el sistema',
    40,
    '2025-03-01',
    '2025-06-30',
    'activo',
    NULL,
    10.00
),

-- Gestión del cambio
(
    'Estrategia de Adopción Tecnológica',
    'Implementación de estrategia para promover la adopción del sistema GIL con IA',
    'gestion_cambio',
    'Estrategia de gestión del cambio',
    'Porcentaje de adopción tecnológica',
    90,
    45,
    'Actividad 4: Implementar estrategia de gestión del cambio',
    160,
    '2025-01-05',
    '2025-12-31',
    'activo',
    NULL,
    50.00
),
(
    'Programa de Embajadores Tecnológicos',
    'Formación de usuarios clave como promotores del cambio tecnológico',
    'gestion_cambio',
    'Estrategia de gestión del cambio',
    'Porcentaje de adopción tecnológica',
    90,
    30,
    'Actividad 4: Implementar estrategia de gestión del cambio',
    80,
    '2025-02-01',
    '2025-12-31',
    'activo',
    NULL,
    33.33
);

-- Verificar datos insertados
SELECT 
    tipo_capacitacion,
    COUNT(*) as total,
    SUM(cantidad_actual) as avance_actual,
    SUM(cantidad_meta) as meta_total
FROM capacitaciones
GROUP BY tipo_capacitacion;

-- Mostrar resumen por producto
SELECT 
    producto,
    medicion,
    SUM(cantidad_meta) as meta,
    SUM(cantidad_actual) as actual,
    ROUND(AVG(porcentaje_avance), 2) as avance_promedio
FROM capacitaciones
WHERE producto IS NOT NULL
GROUP BY producto, medicion;
