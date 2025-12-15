# API REST para Gestión de Prácticas de Laboratorio
# Centro Minero SENA
# CRUD completo para prácticas

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.database import DatabaseManager
from backend.utils.validators import Validator

# Blueprint para prácticas
practicas_bp = Blueprint('practicas', __name__, url_prefix='/api/practicas')

# Instancia de base de datos
db = DatabaseManager()

# =========================================================
# DECORADORES
# =========================================================

def require_auth_session(f):
    """Decorador para requerir autenticación por sesión"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated

def require_permission(permiso):
    """Decorador para requerir un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
            
            permisos = session.get('user_permisos', {})
            if not permisos.get('all') and not permisos.get(permiso):
                return jsonify({'success': False, 'message': 'No tiene permisos para esta acción'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def actualizar_estados_automaticos():
    """
    Actualiza automáticamente los estados de las prácticas basándose en fecha/hora y duración:
    - programada -> en_curso: cuando NOW() >= fecha
    - en_curso -> completada: cuando NOW() >= fecha + duracion_horas
    """
    try:
        # Marcar como completada cualquier práctica cuyo fin ya pasó,
        # incluso si por alguna razón nunca quedó en 'en_curso'.
        query_completar = """
            UPDATE practicas_laboratorio
            SET estado = 'completada'
            WHERE estado IN ('programada', 'en_curso')
            AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) <= NOW()
        """
        db.ejecutar_comando(query_completar)

        # Marcar como en_curso solo si ya inició y aún no termina
        query_iniciar = """
            UPDATE practicas_laboratorio
            SET estado = 'en_curso'
            WHERE estado = 'programada'
            AND fecha <= NOW()
            AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) > NOW()
        """
        db.ejecutar_comando(query_iniciar)
        
    except Exception as e:
        print(f"Error actualizando estados automáticos: {e}")

# =========================================================
# ENDPOINTS DE PRÁCTICAS
# =========================================================

@practicas_bp.route('', methods=['GET'])
@require_auth_session
def listar_practicas():
    """Obtener lista de todas las prácticas con filtros opcionales"""
    try:
        # Actualizar estados automáticamente antes de listar
        actualizar_estados_automaticos()
        
        busqueda = request.args.get('busqueda', '').strip()
        estado = request.args.get('estado', '').strip()
        laboratorio = request.args.get('laboratorio', '').strip()
        programa = request.args.get('programa', '').strip()
        
        query = """
            SELECT p.id, p.codigo, p.nombre, p.id_programa, p.id_laboratorio, 
                   p.id_instructor, p.fecha, p.duracion_horas, p.numero_estudiantes,
                   p.equipos_requeridos, p.materiales_requeridos, p.objetivos,
                   p.descripcion_actividades, p.observaciones, p.estado,
                   DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_formato,
                   DATE_FORMAT(p.fecha_registro, '%d/%m/%Y') as fecha_registro_formato,
                   pf.nombre_programa, pf.codigo_programa,
                   l.nombre as laboratorio_nombre, l.codigo_lab as laboratorio_codigo,
                   CONCAT(u.nombres, ' ', u.apellidos) as instructor_nombre
            FROM practicas_laboratorio p
            LEFT JOIN programas_formacion pf ON p.id_programa = pf.id
            LEFT JOIN laboratorios l ON p.id_laboratorio = l.id
            LEFT JOIN instructores i ON p.id_instructor = i.id
            LEFT JOIN usuarios u ON i.id_usuario = u.id
            WHERE 1=1
        """
        params = []
        
        if busqueda:
            query += " AND (p.codigo LIKE %s OR p.nombre LIKE %s OR pf.nombre_programa LIKE %s)"
            params.extend([f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'])
        
        if estado:
            query += " AND p.estado = %s"
            params.append(estado)
        
        if laboratorio:
            query += " AND p.id_laboratorio = %s"
            params.append(int(laboratorio))
        
        if programa:
            query += " AND p.id_programa = %s"
            params.append(int(programa))
        
        query += " ORDER BY p.fecha DESC"
        
        practicas = db.ejecutar_query(query, tuple(params) if params else None) or []
        
        return jsonify({
            'success': True, 
            'practicas': practicas,
            'total': len(practicas)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo prácticas: {str(e)}'}), 500


@practicas_bp.route('/validar', methods=['GET'])
@require_auth_session
def validar_codigo_practica():
    """GET /api/practicas/validar?codigo=XXX&excluir_id=YYY - Verificar si código existe"""
    try:
        codigo = request.args.get('codigo', '').strip()
        excluir_id = request.args.get('excluir_id', '')
        
        if not codigo:
            return jsonify({'success': True, 'existe': False}), 200
        
        if excluir_id:
            query = "SELECT id FROM practicas_laboratorio WHERE codigo = %s AND id != %s"
            resultado = db.obtener_uno(query, (codigo, int(excluir_id)))
        else:
            query = "SELECT id FROM practicas_laboratorio WHERE codigo = %s"
            resultado = db.obtener_uno(query, (codigo,))
        
        return jsonify({'success': True, 'existe': resultado is not None}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@practicas_bp.route('/<int:practica_id>', methods=['GET'])
@require_auth_session
def obtener_practica(practica_id):
    """Obtener una práctica específica por ID"""
    try:
        query = """
            SELECT p.id, p.codigo, p.nombre, p.id_programa, p.id_laboratorio, 
                   p.id_instructor, p.fecha, p.duracion_horas, p.numero_estudiantes,
                   p.equipos_requeridos, p.materiales_requeridos, p.objetivos,
                   p.descripcion_actividades, p.observaciones, p.estado,
                   DATE_FORMAT(p.fecha, '%Y-%m-%dT%H:%i') as fecha_input,
                   DATE_FORMAT(p.fecha, '%d/%m/%Y %H:%i') as fecha_formato,
                   pf.nombre_programa, pf.codigo_programa,
                   l.nombre as laboratorio_nombre, l.codigo_lab as laboratorio_codigo,
                   CONCAT(u.nombres, ' ', u.apellidos) as instructor_nombre
            FROM practicas_laboratorio p
            LEFT JOIN programas_formacion pf ON p.id_programa = pf.id
            LEFT JOIN laboratorios l ON p.id_laboratorio = l.id
            LEFT JOIN instructores i ON p.id_instructor = i.id
            LEFT JOIN usuarios u ON i.id_usuario = u.id
            WHERE p.id = %s
        """
        practica = db.obtener_uno(query, (practica_id,))
        
        if not practica:
            return jsonify({'success': False, 'message': 'Práctica no encontrada'}), 404
        
        return jsonify({'success': True, 'practica': practica}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo práctica: {str(e)}'}), 500


@practicas_bp.route('', methods=['POST'])
@require_permission('reservas')
def crear_practica():
    """Crear una nueva práctica de laboratorio"""
    try:
        data = request.get_json()
        
        # Recopilar errores
        errores = {}
        
        codigo = Validator.sanitizar_texto(data.get('codigo', ''))
        nombre = Validator.sanitizar_texto(data.get('nombre', ''))
        id_programa = data.get('id_programa')
        id_laboratorio = data.get('id_laboratorio')
        id_instructor = data.get('id_instructor')
        fecha = data.get('fecha')
        
        # Validar código
        if not codigo:
            errores['codigo'] = 'El código es requerido'
        elif not Validator.validar_longitud(codigo, 3, 30):
            errores['codigo'] = 'El código debe tener entre 3 y 30 caracteres'
        elif db.existe('practicas_laboratorio', 'codigo = %s', (codigo,)):
            errores['codigo'] = 'Ya existe una práctica con ese código'
        
        # Validar nombre
        if not nombre:
            errores['nombre'] = 'El nombre es requerido'
        elif not Validator.validar_longitud(nombre, 5, 200):
            errores['nombre'] = 'El nombre debe tener entre 5 y 200 caracteres'
        
        # Validar programa
        if not id_programa:
            errores['programa'] = 'El programa es requerido'
        
        # Validar laboratorio
        if not id_laboratorio:
            errores['laboratorio'] = 'El laboratorio es requerido'
        
        # Validar instructor
        if not id_instructor:
            errores['instructor'] = 'El instructor es requerido'
        else:
            # Si el usuario es instructor (rol 2), solo puede crear reservas para sí mismo
            user_rol = session.get('user_rol')
            if user_rol == 2:
                user_id = session.get('user_id')
                query_instructor = "SELECT id FROM instructores WHERE id_usuario = %s"
                resultado = db.ejecutar_query(query_instructor, (user_id,))
                if resultado and len(resultado) > 0:
                    instructor_id_usuario = resultado[0]['id']
                    if int(id_instructor) != instructor_id_usuario:
                        errores['instructor'] = 'Solo puede crear reservas asignándose a usted mismo como instructor'
        
        # Validar fecha
        if not fecha:
            errores['fecha'] = 'La fecha es requerida'
        
        # Validar duración (REQUERIDO)
        duracion = data.get('duracion_horas')
        if not duracion:
            errores['duracion'] = 'La duración es requerida'
        else:
            try:
                duracion_float = float(duracion)
                if duracion_float < 0.5 or duracion_float > 12:
                    errores['duracion'] = 'La duración debe estar entre 0.5 y 12 horas'
            except (ValueError, TypeError):
                errores['duracion'] = 'La duración debe ser un número válido'
        
        # Validar número de estudiantes (REQUERIDO)
        numero_estudiantes = data.get('numero_estudiantes')
        if not numero_estudiantes:
            errores['estudiantes'] = 'El número de estudiantes es requerido'
        else:
            try:
                estudiantes_int = int(numero_estudiantes)
                if estudiantes_int < 1 or estudiantes_int > 100:
                    errores['estudiantes'] = 'El número de estudiantes debe estar entre 1 y 100'
            except (ValueError, TypeError):
                errores['estudiantes'] = 'El número de estudiantes debe ser un número válido'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Preparar datos
        estado = data.get('estado', 'programada')
        
        query = """
            INSERT INTO practicas_laboratorio 
            (codigo, nombre, id_programa, id_laboratorio, id_instructor, fecha,
             duracion_horas, numero_estudiantes, equipos_requeridos, materiales_requeridos,
             objetivos, descripcion_actividades, observaciones, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            codigo, nombre, int(id_programa), int(id_laboratorio), int(id_instructor), fecha,
            float(duracion) if duracion else None,
            int(numero_estudiantes) if numero_estudiantes else None,
            data.get('equipos_requeridos', ''),
            data.get('materiales_requeridos', ''),
            data.get('objetivos', ''),
            data.get('descripcion_actividades', ''),
            data.get('observaciones', ''),
            estado
        )
        
        db.ejecutar_comando(query, params)
        
        # Obtener ID
        result = db.obtener_uno("SELECT LAST_INSERT_ID() as id")
        nuevo_id = result['id'] if result else None
        
        return jsonify({
            'success': True, 
            'message': 'Práctica creada exitosamente',
            'practica_id': nuevo_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando práctica: {str(e)}'}), 500


@practicas_bp.route('/<int:practica_id>', methods=['PUT'])
@require_permission('reservas')
def actualizar_practica(practica_id):
    """Actualizar una práctica existente"""
    try:
        data = request.get_json()
        
        # Verificar que existe
        if not db.existe('practicas_laboratorio', 'id = %s', (practica_id,)):
            return jsonify({'success': False, 'message': 'Práctica no encontrada'}), 404
        
        errores = {}
        updates = []
        params = []
        
        # Validar código si se envía
        if 'codigo' in data:
            codigo = Validator.sanitizar_texto(data['codigo'])
            if not codigo:
                errores['codigo'] = 'El código es requerido'
            elif not Validator.validar_longitud(codigo, 3, 30):
                errores['codigo'] = 'El código debe tener entre 3 y 30 caracteres'
            else:
                query_dup = "SELECT id FROM practicas_laboratorio WHERE codigo = %s AND id != %s"
                if db.obtener_uno(query_dup, (codigo, practica_id)):
                    errores['codigo'] = 'Ya existe otra práctica con ese código'
                else:
                    updates.append("codigo = %s")
                    params.append(codigo)
        
        # Validar nombre si se envía
        if 'nombre' in data:
            nombre = Validator.sanitizar_texto(data['nombre'])
            if not nombre:
                errores['nombre'] = 'El nombre es requerido'
            elif not Validator.validar_longitud(nombre, 5, 200):
                errores['nombre'] = 'El nombre debe tener entre 5 y 200 caracteres'
            else:
                updates.append("nombre = %s")
                params.append(nombre)
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Campos opcionales
        if 'id_programa' in data and data['id_programa']:
            updates.append("id_programa = %s")
            params.append(int(data['id_programa']))
        
        if 'id_laboratorio' in data and data['id_laboratorio']:
            updates.append("id_laboratorio = %s")
            params.append(int(data['id_laboratorio']))
        
        if 'id_instructor' in data and data['id_instructor']:
            # Si el usuario es instructor (rol 2), solo puede editar reservas asignadas a sí mismo
            user_rol = session.get('user_rol')
            if user_rol == 2:
                user_id = session.get('user_id')
                query_instructor = "SELECT id FROM instructores WHERE id_usuario = %s"
                resultado = db.ejecutar_query(query_instructor, (user_id,))
                if resultado and len(resultado) > 0:
                    instructor_id_usuario = resultado[0]['id']
                    # Verificar que la práctica actual pertenece al instructor
                    query_practica = "SELECT id_instructor FROM practicas_laboratorio WHERE id = %s"
                    practica_actual = db.obtener_uno(query_practica, (practica_id,))
                    if practica_actual and practica_actual['id_instructor'] != instructor_id_usuario:
                        return jsonify({'success': False, 'message': 'No tiene permisos para editar esta reserva'}), 403
                    # No permitir cambiar el instructor
                    if int(data['id_instructor']) != instructor_id_usuario:
                        errores['instructor'] = 'No puede cambiar el instructor de la reserva'
                        return jsonify({'success': False, 'errores': errores}), 400
            updates.append("id_instructor = %s")
            params.append(int(data['id_instructor']))
        
        if 'fecha' in data and data['fecha']:
            updates.append("fecha = %s")
            params.append(data['fecha'])
        
        if 'duracion_horas' in data:
            updates.append("duracion_horas = %s")
            params.append(float(data['duracion_horas']) if data['duracion_horas'] else None)
        
        if 'numero_estudiantes' in data:
            updates.append("numero_estudiantes = %s")
            params.append(int(data['numero_estudiantes']) if data['numero_estudiantes'] else None)
        
        if 'equipos_requeridos' in data:
            updates.append("equipos_requeridos = %s")
            params.append(data['equipos_requeridos'])
        
        if 'materiales_requeridos' in data:
            updates.append("materiales_requeridos = %s")
            params.append(data['materiales_requeridos'])
        
        if 'objetivos' in data:
            updates.append("objetivos = %s")
            params.append(data['objetivos'])
        
        if 'descripcion_actividades' in data:
            updates.append("descripcion_actividades = %s")
            params.append(data['descripcion_actividades'])
        
        if 'observaciones' in data:
            updates.append("observaciones = %s")
            params.append(data['observaciones'])
        
        if 'estado' in data:
            estados_validos = ['programada', 'en_curso', 'completada', 'cancelada']
            if data['estado'] in estados_validos:
                updates.append("estado = %s")
                params.append(data['estado'])
        
        if updates:
            params.append(practica_id)
            query = f"UPDATE practicas_laboratorio SET {', '.join(updates)} WHERE id = %s"
            db.ejecutar_comando(query, tuple(params))
        
        return jsonify({
            'success': True,
            'message': 'Práctica actualizada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando práctica: {str(e)}'}), 500


@practicas_bp.route('/<int:practica_id>', methods=['DELETE'])
@require_permission('reservas')
def eliminar_practica(practica_id):
    """Eliminar una práctica"""
    try:
        if not db.existe('practicas_laboratorio', 'id = %s', (practica_id,)):
            return jsonify({'success': False, 'message': 'Práctica no encontrada'}), 404
        
        db.ejecutar_comando("DELETE FROM practicas_laboratorio WHERE id = %s", (practica_id,))
        
        return jsonify({
            'success': True,
            'message': 'Práctica eliminada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error eliminando práctica: {str(e)}'}), 500


# =========================================================
# ENDPOINTS AUXILIARES
# =========================================================

@practicas_bp.route('/instructores', methods=['GET'])
@require_auth_session
def listar_instructores():
    """Obtener lista de instructores disponibles"""
    try:
        query = """
            SELECT i.id, i.especialidad, i.experiencia_anos,
                   CONCAT(u.nombres, ' ', u.apellidos) as nombre_completo,
                   u.documento
            FROM instructores i
            JOIN usuarios u ON i.id_usuario = u.id
            WHERE u.estado = 'activo'
            ORDER BY u.nombres, u.apellidos
        """
        instructores = db.ejecutar_query(query) or []
        
        return jsonify({'success': True, 'instructores': instructores}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@practicas_bp.route('/verificar-equipos', methods=['POST'])
@require_auth_session
def verificar_disponibilidad_equipos():
    """POST /api/practicas/verificar-equipos - Verificar disponibilidad de equipos para una práctica
    
    Body JSON:
    {
        "equipos_ids": [1, 5, 8, 12],
        "fecha_inicio": "2024-12-20 10:00:00",
        "duracion_horas": 3.0,
        "practica_id": 5  (opcional, para excluir en edición)
    }
    """
    try:
        data = request.get_json()
        equipos_ids = data.get('equipos_ids', [])
        fecha_inicio = data.get('fecha_inicio')
        duracion = float(data.get('duracion_horas', 1.0))
        practica_id = data.get('practica_id')
        
        if not equipos_ids or not fecha_inicio:
            return jsonify({'success': False, 'message': 'Faltan parámetros requeridos'}), 400
        
        from datetime import datetime, timedelta
        try:
            fecha_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                fecha_dt = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M')
            except:
                return jsonify({'success': False, 'message': 'Formato de fecha inválido'}), 400
        
        fecha_fin = fecha_dt + timedelta(hours=duracion)
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        equipos_disponibles = []
        equipos_no_disponibles = []
        
        for equipo_id in equipos_ids:
            equipo = db.obtener_uno(
                "SELECT id, codigo_interno, nombre, estado FROM equipos WHERE id = %s",
                (equipo_id,)
            )
            
            if not equipo:
                equipos_no_disponibles.append({
                    'id': equipo_id,
                    'nombre': 'Desconocido',
                    'codigo': 'N/A',
                    'motivo': 'Equipo no encontrado'
                })
                continue
            
            if equipo['estado'] == 'dado_baja':
                equipos_no_disponibles.append({
                    'id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'codigo': equipo['codigo_interno'],
                    'motivo': 'Equipo dado de baja'
                })
                continue
            
            if equipo['estado'] in ['mantenimiento', 'reparacion']:
                equipos_no_disponibles.append({
                    'id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'codigo': equipo['codigo_interno'],
                    'motivo': f'En {equipo["estado"]}'
                })
                continue
            
            conflicto = db.obtener_uno("""
                SELECT COUNT(*) as total FROM prestamos
                WHERE id_equipo = %s
                AND estado IN ('aprobado', 'activo')
                AND (
                    (fecha <= %s AND fecha_devolucion_programada > %s) OR
                    (fecha < %s AND fecha_devolucion_programada >= %s)
                )
            """, (equipo_id, fecha_inicio, fecha_inicio, fecha_fin_str, fecha_fin_str))
            
            if conflicto and conflicto['total'] > 0:
                equipos_no_disponibles.append({
                    'id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'codigo': equipo['codigo_interno'],
                    'motivo': 'Ya reservado en ese horario'
                })
            else:
                equipos_disponibles.append({
                    'id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'codigo': equipo['codigo_interno'],
                    'estado': equipo['estado']
                })
        
        return jsonify({
            'success': True,
            'todos_disponibles': len(equipos_no_disponibles) == 0,
            'equipos_disponibles': equipos_disponibles,
            'equipos_no_disponibles': equipos_no_disponibles,
            'total_solicitados': len(equipos_ids),
            'total_disponibles': len(equipos_disponibles)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error verificando equipos: {str(e)}'}), 500


@practicas_bp.route('/disponibilidad/laboratorio/<int:lab_id>', methods=['GET'])
@require_auth_session
def verificar_disponibilidad_laboratorio(lab_id):
    """GET /api/practicas/disponibilidad/laboratorio/{id}?fecha=YYYY-MM-DD&hora=HH:MM&duracion=3.0
    
    Verifica si un laboratorio está disponible en un horario específico
    """
    try:
        fecha = request.args.get('fecha')
        hora = request.args.get('hora')
        duracion = float(request.args.get('duracion', 1.0))
        practica_id = request.args.get('practica_id')
        
        if not fecha or not hora:
            return jsonify({'success': False, 'message': 'Fecha y hora son requeridas'}), 400
        
        from datetime import datetime, timedelta
        fecha_inicio_str = f"{fecha} {hora}:00"
        fecha_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d %H:%M:%S')
        fecha_fin = fecha_dt + timedelta(hours=duracion)
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        laboratorio = db.obtener_uno(
            "SELECT id, codigo_lab, nombre, estado, capacidad_personas FROM laboratorios WHERE id = %s",
            (lab_id,)
        )
        
        if not laboratorio:
            return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
        
        if laboratorio['estado'] in ['mantenimiento', 'fuera_servicio']:
            return jsonify({
                'success': True,
                'disponible': False,
                'motivo': f'Laboratorio en estado: {laboratorio["estado"]}',
                'laboratorio': laboratorio
            }), 200
        
        query_conflictos = """
            SELECT COUNT(*) as total FROM practicas_laboratorio
            WHERE id_laboratorio = %s
            AND estado IN ('programada', 'en_curso')
            AND (
                (fecha <= %s AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) > %s) OR
                (fecha < %s AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) >= %s)
            )
        """
        params = [lab_id, fecha_inicio_str, fecha_inicio_str, fecha_fin_str, fecha_fin_str]
        
        if practica_id:
            query_conflictos += " AND id != %s"
            params.append(int(practica_id))
        
        conflicto = db.obtener_uno(query_conflictos, tuple(params))
        
        if conflicto and conflicto['total'] > 0:
            return jsonify({
                'success': True,
                'disponible': False,
                'motivo': f'Ya hay {conflicto["total"]} práctica(s) programada(s) en ese horario',
                'laboratorio': laboratorio
            }), 200
        
        return jsonify({
            'success': True,
            'disponible': True,
            'laboratorio': laboratorio
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error verificando laboratorio: {str(e)}'}), 500


@practicas_bp.route('/sugerir-laboratorio', methods=['POST'])
@require_auth_session
def sugerir_laboratorio():
    """POST /api/practicas/sugerir-laboratorio - Algoritmo de optimización de espacios
    
    Body JSON:
    {
        "fecha": "2024-12-20",
        "hora": "10:00",
        "duracion_horas": 3.0,
        "numero_estudiantes": 25,
        "tipo_laboratorio": "quimica" (opcional)
    }
    """
    try:
        data = request.get_json()
        fecha = data.get('fecha')
        hora = data.get('hora')
        duracion = float(data.get('duracion_horas', 1.0))
        num_estudiantes = int(data.get('numero_estudiantes', 20))
        tipo_lab = data.get('tipo_laboratorio')
        
        if not fecha or not hora:
            return jsonify({'success': False, 'message': 'Fecha y hora son requeridas'}), 400
        
        from datetime import datetime, timedelta
        fecha_inicio_str = f"{fecha} {hora}:00"
        fecha_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d %H:%M:%S')
        fecha_fin = fecha_dt + timedelta(hours=duracion)
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
            SELECT l.id, l.codigo_lab, l.nombre, l.tipo, l.capacidad_personas,
                   l.estado, l.area_m2
            FROM laboratorios l
            WHERE l.estado IN ('disponible', 'ocupado')
            AND l.capacidad_personas >= %s
        """
        params = [num_estudiantes]
        
        if tipo_lab:
            query += " AND l.tipo = %s"
            params.append(tipo_lab)
        
        laboratorios = db.ejecutar_query(query, tuple(params)) or []
        
        laboratorios_disponibles = []
        laboratorios_ocupados = []
        
        for lab in laboratorios:
            conflicto = db.obtener_uno("""
                SELECT COUNT(*) as total FROM practicas_laboratorio
                WHERE id_laboratorio = %s
                AND estado IN ('programada', 'en_curso')
                AND (
                    (fecha <= %s AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) > %s) OR
                    (fecha < %s AND DATE_ADD(fecha, INTERVAL ROUND(COALESCE(duracion_horas, 1) * 60) MINUTE) >= %s)
                )
            """, (lab['id'], fecha_inicio_str, fecha_inicio_str, fecha_fin_str, fecha_fin_str))
            
            if conflicto and conflicto['total'] > 0:
                laboratorios_ocupados.append({
                    'id': lab['id'],
                    'codigo': lab['codigo_lab'],
                    'nombre': lab['nombre'],
                    'tipo': lab['tipo'],
                    'capacidad': lab['capacidad_personas'],
                    'motivo': f'{conflicto["total"]} práctica(s) programada(s)'
                })
            else:
                capacidad_extra = lab['capacidad_personas'] - num_estudiantes
                eficiencia = (num_estudiantes / lab['capacidad_personas']) * 100
                
                laboratorios_disponibles.append({
                    'id': lab['id'],
                    'codigo': lab['codigo_lab'],
                    'nombre': lab['nombre'],
                    'tipo': lab['tipo'],
                    'capacidad': lab['capacidad_personas'],
                    'capacidad_extra': capacidad_extra,
                    'eficiencia': round(eficiencia, 1),
                    'area_m2': float(lab['area_m2']) if lab['area_m2'] else None
                })
        
        laboratorios_disponibles.sort(key=lambda x: x['eficiencia'], reverse=True)
        
        return jsonify({
            'success': True,
            'laboratorios_disponibles': laboratorios_disponibles,
            'laboratorios_ocupados': laboratorios_ocupados,
            'total_disponibles': len(laboratorios_disponibles),
            'recomendacion': laboratorios_disponibles[0] if laboratorios_disponibles else None
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error sugiriendo laboratorio: {str(e)}'}), 500


@practicas_bp.route('/<int:practica_id>/crear-prestamos', methods=['POST'])
@require_permission('reservas')
def crear_prestamos_practica(practica_id):
    """POST /api/practicas/{id}/crear-prestamos - Autorizar préstamos de equipos para la práctica (sin cambiar estado)"""
    try:
        # Actualizar estados automáticamente antes de procesar
        actualizar_estados_automaticos()
        
        practica = db.obtener_uno("""
            SELECT p.*, i.id_usuario as instructor_usuario_id
            FROM practicas_laboratorio p
            JOIN instructores i ON p.id_instructor = i.id
            WHERE p.id = %s
        """, (practica_id,))
        
        if not practica:
            return jsonify({'success': False, 'message': 'Práctica no encontrada'}), 404
        
        if practica['estado'] not in ['programada', 'en_curso']:
            return jsonify({'success': False, 'message': 'Solo se pueden autorizar préstamos para prácticas programadas o en curso'}), 400
        
        import json
        try:
            equipos_ids = json.loads(practica['equipos_requeridos']) if practica['equipos_requeridos'] else []
        except:
            equipos_ids = []
        
        if not equipos_ids:
            return jsonify({'success': False, 'message': 'No hay equipos asignados a esta práctica'}), 400
        
        from datetime import datetime, timedelta
        fecha_inicio = practica['fecha']
        duracion = float(practica['duracion_horas'] or 1.0)
        
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S')
        
        fecha_fin = fecha_inicio + timedelta(hours=duracion)
        
        prestamos_creados = []
        errores = []
        
        for equipo_id in equipos_ids:
            try:
                equipo = db.obtener_uno("SELECT estado FROM equipos WHERE id = %s", (equipo_id,))
                
                if not equipo:
                    errores.append(f'Equipo {equipo_id} no encontrado')
                    continue
                
                if equipo['estado'] != 'disponible':
                    errores.append(f'Equipo {equipo_id} no está disponible (estado: {equipo["estado"]})')
                    continue
                
                codigo_prestamo = f"PRAC-{practica['codigo']}-EQ{equipo_id}"
                
                query_prestamo = """
                    INSERT INTO prestamos
                    (codigo, id_equipo, id_usuario_solicitante, id_usuario_autorizador,
                     fecha_solicitud, fecha, fecha_devolucion_programada, proposito, estado)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s)
                """
                params = (
                    codigo_prestamo,
                    equipo_id,
                    practica['instructor_usuario_id'],
                    session.get('user_id'),
                    fecha_inicio,
                    fecha_fin,
                    f"Práctica: {practica['nombre']}",
                    'activo'
                )
                
                db.ejecutar_comando(query_prestamo, params)
                db.ejecutar_comando("UPDATE equipos SET estado = 'prestado' WHERE id = %s", (equipo_id,))
                
                prestamos_creados.append(equipo_id)
                
            except Exception as e:
                errores.append(f'Error con equipo {equipo_id}: {str(e)}')
        
        mensaje = f'{len(prestamos_creados)} préstamo(s) creado(s) exitosamente'
        if errores:
            mensaje += f'. {len(errores)} error(es): {"; ".join(errores[:3])}'
        
        return jsonify({
            'success': True,
            'message': mensaje,
            'prestamos_creados': prestamos_creados,
            'errores': errores
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando préstamos: {str(e)}'}), 500


@practicas_bp.route('/<int:practica_id>/liberar-equipos', methods=['POST'])
@require_permission('reservas')
def liberar_equipos_practica(practica_id):
    """POST /api/practicas/{id}/liberar-equipos - Devolver equipos al completar práctica"""
    try:
        practica = db.obtener_uno("SELECT codigo, estado FROM practicas_laboratorio WHERE id = %s", (practica_id,))
        
        if not practica:
            return jsonify({'success': False, 'message': 'Práctica no encontrada'}), 404
        
        prestamos = db.ejecutar_query("""
            SELECT id, id_equipo FROM prestamos
            WHERE codigo LIKE %s
            AND estado = 'activo'
        """, (f"PRAC-{practica['codigo']}-%",)) or []
        
        equipos_liberados = []
        
        for prestamo in prestamos:
            db.ejecutar_comando("""
                UPDATE prestamos 
                SET estado = 'devuelto', fecha_devolucion_real = NOW()
                WHERE id = %s
            """, (prestamo['id'],))
            
            db.ejecutar_comando(
                "UPDATE equipos SET estado = 'disponible' WHERE id = %s",
                (prestamo['id_equipo'],)
            )
            
            equipos_liberados.append(prestamo['id_equipo'])
        
        return jsonify({
            'success': True,
            'message': f'{len(equipos_liberados)} equipo(s) liberado(s)',
            'equipos_liberados': equipos_liberados
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error liberando equipos: {str(e)}'}), 500


@practicas_bp.route('/estadisticas', methods=['GET'])
@require_permission('reservas')
def obtener_estadisticas():
    """GET /api/practicas/estadisticas - Estadísticas para dashboard"""
    try:
        # Actualizar estados automáticamente antes de calcular estadísticas
        actualizar_estados_automaticos()
        
        stats = {}
        
        stats['total_practicas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio")['total']
        stats['practicas_programadas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'programada'")['total']
        stats['practicas_en_curso'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'en_curso'")['total']
        stats['practicas_completadas'] = db.obtener_uno("SELECT COUNT(*) as total FROM practicas_laboratorio WHERE estado = 'completada'")['total']
        
        stats['practicas_hoy'] = db.obtener_uno("""
            SELECT COUNT(*) as total FROM practicas_laboratorio
            WHERE DATE(fecha) = CURDATE()
            AND estado IN ('programada', 'en_curso')
        """)['total']
        
        stats['practicas_semana'] = db.obtener_uno("""
            SELECT COUNT(*) as total FROM practicas_laboratorio
            WHERE YEARWEEK(fecha, 1) = YEARWEEK(CURDATE(), 1)
            AND estado IN ('programada', 'en_curso')
        """)['total']
        
        laboratorios_mas_usados = db.ejecutar_query("""
            SELECT l.nombre, COUNT(p.id) as total_practicas
            FROM practicas_laboratorio p
            JOIN laboratorios l ON p.id_laboratorio = l.id
            WHERE p.estado IN ('completada', 'en_curso')
            GROUP BY l.id, l.nombre
            ORDER BY total_practicas DESC
            LIMIT 5
        """) or []
        stats['laboratorios_mas_usados'] = laboratorios_mas_usados
        
        programas_activos = db.ejecutar_query("""
            SELECT pf.nombre_programa, COUNT(p.id) as total_practicas
            FROM practicas_laboratorio p
            JOIN programas_formacion pf ON p.id_programa = pf.id
            WHERE p.estado IN ('programada', 'en_curso')
            GROUP BY pf.id, pf.nombre_programa
            ORDER BY total_practicas DESC
        """) or []
        stats['programas_activos'] = programas_activos
        
        return jsonify({'success': True, 'estadisticas': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo estadísticas: {str(e)}'}), 500


@practicas_bp.route('/ocupacion-laboratorios', methods=['GET'])
@require_permission('reservas')
def ocupacion_laboratorios():
    """GET /api/practicas/ocupacion-laboratorios - Ocupación en tiempo real"""
    try:
        # Actualizar estados automáticamente antes de calcular ocupación
        actualizar_estados_automaticos()
        
        fecha = request.args.get('fecha', 'CURDATE()')
        
        if fecha != 'CURDATE()':
            fecha = f"'{fecha}'"
        
        query = f"""
            SELECT l.id, l.codigo_lab, l.nombre, l.tipo, l.capacidad_personas, l.estado,
                   COUNT(CASE WHEN p.estado = 'en_curso' 
                         AND p.fecha <= NOW() 
                         AND DATE_ADD(p.fecha, INTERVAL ROUND(COALESCE(p.duracion_horas, 1) * 60) MINUTE) >= NOW() 
                         THEN 1 END) as practicas_en_curso,
                   COUNT(CASE WHEN p.estado = 'programada' 
                         AND DATE(p.fecha) = {fecha}
                         THEN 1 END) as practicas_programadas_hoy,
                   MIN(CASE WHEN p.estado = 'programada' AND p.fecha > NOW() 
                       THEN p.fecha END) as proxima_practica
            FROM laboratorios l
            LEFT JOIN practicas_laboratorio p ON l.id = p.id_laboratorio
            GROUP BY l.id, l.codigo_lab, l.nombre, l.tipo, l.capacidad_personas, l.estado
            ORDER BY l.nombre
        """
        
        laboratorios = db.ejecutar_query(query) or []
        
        for lab in laboratorios:
            if lab['practicas_en_curso'] > 0:
                lab['estado_ocupacion'] = 'ocupado'
            elif lab['practicas_programadas_hoy'] > 0:
                lab['estado_ocupacion'] = 'reservado'
            else:
                lab['estado_ocupacion'] = 'disponible'
            
            if lab['proxima_practica']:
                from datetime import datetime
                if isinstance(lab['proxima_practica'], str):
                    lab['proxima_practica'] = datetime.strptime(lab['proxima_practica'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
        
        return jsonify({
            'success': True,
            'laboratorios': laboratorios,
            'total': len(laboratorios)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo ocupación: {str(e)}'}), 500
