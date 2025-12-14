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
# ENDPOINTS DE PRÁCTICAS
# =========================================================

@practicas_bp.route('', methods=['GET'])
@require_auth_session
def listar_practicas():
    """Obtener lista de todas las prácticas con filtros opcionales"""
    try:
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
@require_permission('practicas')
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
        
        # Validar fecha
        if not fecha:
            errores['fecha'] = 'La fecha es requerida'
        
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Preparar datos
        duracion = data.get('duracion_horas')
        numero_estudiantes = data.get('numero_estudiantes')
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
@require_permission('practicas')
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
@require_permission('practicas')
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
