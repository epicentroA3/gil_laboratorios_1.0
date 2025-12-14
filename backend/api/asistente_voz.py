# API del Asistente LUCIA
# Centro Minero SENA
# Sistema GIL - Clasificación NLU (solo texto)

import os
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session

# Importar servicios
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.services.nlu_classifier import nlu_classifier
from backend.utils.database import DatabaseManager

# Crear blueprint
asistente_voz_bp = Blueprint('asistente_voz', __name__, url_prefix='/api/voz')

# Instancia de base de datos
db = DatabaseManager()


def require_session(f):
    """Decorador para requerir sesión activa"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Sesión no activa'}), 401
        return f(*args, **kwargs)
    return decorated


@asistente_voz_bp.route('/status', methods=['GET'])
def get_status():
    """GET /api/voz/status - Estado del servicio NLU"""
    nlu_status = nlu_classifier.get_status()
    
    return jsonify({
        'success': True,
        'nlu': nlu_status,
        'ready': nlu_status['ready'],
        'message': 'Servicio NLU listo' if nlu_status['ready'] else 'Servicio NLU no disponible'
    })


@asistente_voz_bp.route('/procesar-texto', methods=['POST'])
@require_session
def procesar_texto():
    """
    POST /api/voz/procesar-texto
    Procesa texto directamente (sin audio) - útil para testing o entrada por teclado
    
    Body:
        - texto: comando de texto
    """
    start_time = time.time()
    user_id = session.get('user_id')
    
    try:
        data = request.get_json()
        
        if not data or 'texto' not in data:
            return jsonify({'success': False, 'error': 'Texto requerido'}), 400
        
        texto = data.get('texto', '').strip()
        
        if not texto:
            return jsonify({'success': False, 'error': 'Texto vacío'}), 400
        
        # Clasificar intención
        intencion, confianza, respuesta = nlu_classifier.classify(texto)
        
        # Extraer entidades
        entidades = nlu_classifier.extract_entities(texto, intencion)
        
        # Ejecutar acción
        accion_resultado = _ejecutar_accion(intencion, entidades, user_id)
        
        if accion_resultado.get('respuesta'):
            respuesta = accion_resultado['respuesta']
        
        duracion_total = int((time.time() - start_time) * 1000)
        
        # Registrar interacción
        _registrar_interaccion(
            user_id, texto, intencion, confianza,
            respuesta, accion_resultado.get('accion'), True, duracion_total
        )
        
        return jsonify({
            'success': True,
            'texto': texto,
            'intencion': intencion,
            'confianza': round(confianza, 2),
            'respuesta': respuesta,
            'accion': accion_resultado.get('accion'),
            'datos': accion_resultado.get('datos'),
            'entidades': entidades,
            'duracion_ms': duracion_total
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@asistente_voz_bp.route('/historial', methods=['GET'])
@require_session
def historial():
    """GET /api/voz/historial - Historial de interacciones del usuario"""
    user_id = session.get('user_id')
    limite = request.args.get('limite', 20, type=int)
    
    try:
        query = """
            SELECT comando_detectado, intencion_identificada, 
                   confianza_reconocimiento, respuesta_generada,
                   accion_ejecutada, exitosa, duracion_procesamiento_ms,
                   DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') as fecha
            FROM interacciones_voz
            WHERE id_usuario = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        historial = db.ejecutar_query(query, (user_id, limite))
        
        return jsonify({
            'success': True,
            'historial': historial or [],
            'total': len(historial) if historial else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@asistente_voz_bp.route('/estadisticas', methods=['GET'])
@require_session
def estadisticas():
    """GET /api/voz/estadisticas - Estadísticas de uso del asistente"""
    user_id = session.get('user_id')
    
    try:
        # Total de interacciones
        total_query = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN exitosa = 1 THEN 1 ELSE 0 END) as exitosas,
                   AVG(confianza_reconocimiento) as confianza_promedio,
                   AVG(duracion_procesamiento_ms) as duracion_promedio
            FROM interacciones_voz
            WHERE id_usuario = %s
        """
        stats = db.obtener_uno(total_query, (user_id,))
        
        # Intenciones más usadas
        intenciones_query = """
            SELECT intencion_identificada, COUNT(*) as cantidad
            FROM interacciones_voz
            WHERE id_usuario = %s AND intencion_identificada IS NOT NULL
            GROUP BY intencion_identificada
            ORDER BY cantidad DESC
            LIMIT 5
        """
        intenciones = db.ejecutar_query(intenciones_query, (user_id,))
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total_interacciones': stats['total'] if stats else 0,
                'interacciones_exitosas': stats['exitosas'] if stats else 0,
                'tasa_exito': round((stats['exitosas'] / stats['total'] * 100) if stats and stats['total'] > 0 else 0, 1),
                'confianza_promedio': round(float(stats['confianza_promedio'] or 0) * 100, 1),
                'duracion_promedio_ms': round(float(stats['duracion_promedio'] or 0), 0)
            },
            'intenciones_frecuentes': intenciones or []
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _registrar_interaccion(user_id, comando, intencion, confianza, respuesta, accion, exitosa, duracion_ms):
    """Registra una interacción de voz en la base de datos"""
    try:
        query = """
            INSERT INTO interacciones_voz 
            (id_usuario, comando_detectado, intencion_identificada, 
             confianza_reconocimiento, respuesta_generada, accion_ejecutada, 
             exitosa, duracion_procesamiento_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.ejecutar_comando(query, (
            user_id, comando, intencion, confianza,
            respuesta, accion, exitosa, duracion_ms
        ))
    except Exception as e:
        print(f"⚠️ Error registrando interacción: {e}")


def _ejecutar_accion(intencion: str, entidades: dict, user_id: int) -> dict:
    """
    Ejecuta la acción correspondiente a la intención
    
    Returns:
        dict con 'accion', 'datos', 'respuesta'
    """
    resultado = {'accion': None, 'datos': None, 'respuesta': None}
    
    # Mapeo de intenciones a URLs de redirección
    REDIRECCIONES = {
        # === NAVEGACIÓN PRINCIPAL ===
        'ir_dashboard': '/dashboard',
        'ir_buscador': '/inventario',
        'ir_usuarios': '/usuarios',
        'ir_roles': '/roles',
        'ir_programas': '/programas',
        'listar_equipos': '/equipos',
        'consultar_laboratorio': '/laboratorios',
        'ir_practicas': '/practicas',
        'ir_prestamos': '/prestamos',
        'listar_reservas': '/prestamos',
        'crear_reserva': '/prestamos',
        'cancelar_reserva': '/prestamos',
        'consultar_mantenimiento': '/mantenimiento',
        'ir_capacitaciones': '/capacitaciones',
        'reporte': '/reportes',
        
        # === IA & AUTOMATIZACIÓN ===
        'ir_reconocimiento': '/reconocimiento',
        'ir_registro_facial': '/registro-facial',
        'ir_asistente': '/asistente',
        'ir_ia_visual': '/entrenamiento-ia',
        'ir_nuevo_equipo_ia': '/registro-equipos-ia',
        'ir_gestionar_registros': '/registros-gestion',
        
        # === ADMINISTRACIÓN ===
        'ir_backup': '/backup',
        'ir_configuracion': '/configuracion',
        
        # === USUARIO ===
        'ir_perfil': '/perfil',
        'ir_ayuda': '/ayuda',
        'cerrar_sesion': '/logout',
    }
    
    try:
        # Verificar si la intención tiene una redirección directa
        if intencion in REDIRECCIONES:
            resultado = {
                'accion': 'redirect',
                'datos': {'url': REDIRECCIONES[intencion]},
                'respuesta': None  # Usar respuesta predefinida del NLU
            }
        
        # Acciones especiales que requieren consulta a BD
        elif intencion == 'consultar_equipo':
            resultado = _accion_consultar_equipo(entidades)
            
    except Exception as e:
        print(f"⚠️ Error ejecutando acción {intencion}: {e}")
    
    return resultado


def _accion_listar_reservas(user_id: int) -> dict:
    """Lista las reservas activas del usuario"""
    query = """
        SELECT p.id, p.codigo, e.nombre as equipo, 
               DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_inicio,
               DATE_FORMAT(p.fecha_devolucion_programada, '%d/%m/%Y %H:%i') as fecha_fin,
               p.estado
        FROM prestamos p
        JOIN equipos e ON p.id_equipo = e.id
        WHERE p.id_usuario_solicitante = %s 
        AND p.estado IN ('solicitado', 'aprobado', 'activo')
        ORDER BY p.fecha DESC
        LIMIT 5
    """
    reservas = db.ejecutar_query(query, (user_id,))
    
    if reservas and len(reservas) > 0:
        lista = '\n'.join([f"• {r['equipo']} - {r['estado']} ({r['fecha_inicio']})" for r in reservas])
        respuesta = f"Tienes {len(reservas)} reserva(s) activa(s):\n{lista}"
    else:
        respuesta = "No tienes reservas activas en este momento."
    
    return {
        'accion': 'mostrar_reservas',
        'datos': {'reservas': reservas or []},
        'respuesta': respuesta
    }


def _accion_listar_equipos(entidades: dict) -> dict:
    """Lista equipos disponibles"""
    query = """
        SELECT e.id, e.codigo_interno, e.nombre, e.marca, e.modelo,
               c.nombre as categoria, l.nombre as laboratorio
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
        LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
        WHERE e.estado = 'disponible'
        ORDER BY e.nombre
        LIMIT 10
    """
    equipos = db.ejecutar_query(query)
    
    if equipos and len(equipos) > 0:
        lista = '\n'.join([f"• {e['nombre']} ({e['marca']} {e['modelo']})" for e in equipos[:5]])
        respuesta = f"Hay {len(equipos)} equipos disponibles. Algunos son:\n{lista}"
        if len(equipos) > 5:
            respuesta += f"\n...y {len(equipos) - 5} más."
    else:
        respuesta = "No hay equipos disponibles en este momento."
    
    return {
        'accion': 'mostrar_equipos',
        'datos': {'equipos': equipos or []},
        'respuesta': respuesta
    }


def _accion_consultar_equipo(entidades: dict) -> dict:
    """Consulta información de un equipo específico"""
    equipo_nombre = entidades.get('equipo', '')
    
    if not equipo_nombre:
        return {
            'accion': 'solicitar_equipo',
            'datos': None,
            'respuesta': '¿Qué equipo deseas consultar? Dime el nombre del equipo.'
        }
    
    query = """
        SELECT e.id, e.codigo_interno, e.nombre, e.marca, e.modelo,
               e.estado, e.estado_fisico, c.nombre as categoria,
               l.nombre as laboratorio, e.ubicacion_especifica
        FROM equipos e
        LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
        LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
        WHERE LOWER(e.nombre) LIKE %s
        LIMIT 1
    """
    equipo = db.obtener_uno(query, (f'%{equipo_nombre}%',))
    
    if equipo:
        estado_emoji = '✅' if equipo['estado'] == 'disponible' else '🔴'
        respuesta = f"{estado_emoji} {equipo['nombre']} ({equipo['marca']} {equipo['modelo']})\n"
        respuesta += f"Estado: {equipo['estado'].upper()}\n"
        respuesta += f"Ubicación: {equipo['laboratorio']} - {equipo['ubicacion_especifica'] or 'Sin especificar'}"
        
        return {
            'accion': 'mostrar_equipo',
            'datos': {'equipo': equipo},
            'respuesta': respuesta
        }
    else:
        return {
            'accion': None,
            'datos': None,
            'respuesta': f'No encontré ningún equipo llamado "{equipo_nombre}". ¿Podrías verificar el nombre?'
        }


def _accion_consultar_laboratorios() -> dict:
    """Lista los laboratorios disponibles"""
    query = """
        SELECT id, nombre, ubicacion, capacidad, estado
        FROM laboratorios
        WHERE estado = 'activo'
        ORDER BY nombre
    """
    laboratorios = db.ejecutar_query(query)
    
    if laboratorios and len(laboratorios) > 0:
        lista = '\n'.join([f"• {l['nombre']} - {l['ubicacion']} (Cap: {l['capacidad']})" for l in laboratorios])
        respuesta = f"Laboratorios disponibles:\n{lista}"
    else:
        respuesta = "No hay laboratorios activos registrados."
    
    return {
        'accion': 'mostrar_laboratorios',
        'datos': {'laboratorios': laboratorios or []},
        'respuesta': respuesta
    }


def _accion_preparar_reserva(entidades: dict, user_id: int) -> dict:
    """Prepara una nueva reserva"""
    equipo_nombre = entidades.get('equipo')
    fecha = entidades.get('fecha')
    
    if not equipo_nombre:
        # Listar equipos disponibles para elegir
        query = """
            SELECT id, nombre, marca, modelo FROM equipos 
            WHERE estado = 'disponible' LIMIT 5
        """
        equipos = db.ejecutar_query(query)
        
        if equipos:
            lista = '\n'.join([f"• {e['nombre']}" for e in equipos])
            respuesta = f"¿Qué equipo deseas reservar? Estos están disponibles:\n{lista}"
        else:
            respuesta = "No hay equipos disponibles para reservar en este momento."
        
        return {
            'accion': 'seleccionar_equipo',
            'datos': {'equipos_disponibles': equipos or []},
            'respuesta': respuesta
        }
    
    # Buscar el equipo
    query = """
        SELECT id, nombre, estado FROM equipos 
        WHERE LOWER(nombre) LIKE %s AND estado = 'disponible'
        LIMIT 1
    """
    equipo = db.obtener_uno(query, (f'%{equipo_nombre}%',))
    
    if not equipo:
        return {
            'accion': None,
            'datos': None,
            'respuesta': f'El equipo "{equipo_nombre}" no está disponible o no existe.'
        }
    
    return {
        'accion': 'confirmar_reserva',
        'datos': {
            'equipo_id': equipo['id'],
            'equipo_nombre': equipo['nombre'],
            'fecha_sugerida': fecha
        },
        'respuesta': f'Perfecto, voy a preparar la reserva del {equipo["nombre"]}. ¿Para cuándo lo necesitas?'
    }


def _accion_listar_reservas_cancelables(user_id: int) -> dict:
    """Lista reservas que se pueden cancelar"""
    query = """
        SELECT p.id, p.codigo, e.nombre as equipo,
               DATE_FORMAT(p.fecha, '%d/%m/%Y') as fecha
        FROM prestamos p
        JOIN equipos e ON p.id_equipo = e.id
        WHERE p.id_usuario_solicitante = %s 
        AND p.estado IN ('solicitado', 'aprobado')
        ORDER BY p.fecha DESC
    """
    reservas = db.ejecutar_query(query, (user_id,))
    
    if reservas and len(reservas) > 0:
        lista = '\n'.join([f"• {r['equipo']} - {r['fecha']} (ID: {r['id']})" for r in reservas])
        respuesta = f"Estas son tus reservas que puedes cancelar:\n{lista}\n¿Cuál deseas cancelar?"
    else:
        respuesta = "No tienes reservas pendientes que puedas cancelar."
    
    return {
        'accion': 'seleccionar_reserva_cancelar',
        'datos': {'reservas': reservas or []},
        'respuesta': respuesta
    }


def _accion_consultar_mantenimiento() -> dict:
    """Consulta equipos en mantenimiento"""
    query = """
        SELECT e.nombre, hm.fecha_mantenimiento, tm.nombre as tipo,
               hm.descripcion, hm.estado
        FROM historial_mantenimiento hm
        JOIN equipos e ON hm.id_equipo = e.id
        JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
        WHERE hm.estado IN ('programado', 'en_proceso')
        ORDER BY hm.fecha_mantenimiento
        LIMIT 5
    """
    mantenimientos = db.ejecutar_query(query)
    
    if mantenimientos and len(mantenimientos) > 0:
        lista = '\n'.join([f"• {m['nombre']} - {m['tipo']} ({m['estado']})" for m in mantenimientos])
        respuesta = f"Mantenimientos pendientes:\n{lista}"
    else:
        respuesta = "No hay mantenimientos programados en este momento."
    
    return {
        'accion': 'mostrar_mantenimientos',
        'datos': {'mantenimientos': mantenimientos or []},
        'respuesta': respuesta
    }


def _accion_generar_reporte(user_id: int) -> dict:
    """Genera un resumen de actividad"""
    # Estadísticas generales
    stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM equipos WHERE estado = 'disponible') as equipos_disponibles,
            (SELECT COUNT(*) FROM prestamos WHERE estado = 'activo') as prestamos_activos,
            (SELECT COUNT(*) FROM laboratorios WHERE estado = 'activo') as laboratorios_activos
    """
    stats = db.obtener_uno(stats_query)
    
    respuesta = f"""📊 Resumen del sistema:
• Equipos disponibles: {stats['equipos_disponibles'] if stats else 0}
• Préstamos activos: {stats['prestamos_activos'] if stats else 0}
• Laboratorios activos: {stats['laboratorios_activos'] if stats else 0}"""
    
    return {
        'accion': 'mostrar_reporte',
        'datos': stats,
        'respuesta': respuesta
    }
