# API REST para Gestión de Programas de Formación
# Centro Minero SENA
# CRUD completo para programas

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.utils.database import DatabaseManager
from backend.utils.validators import Validator

# Blueprint para programas
programas_bp = Blueprint('programas', __name__, url_prefix='/api/programas')

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
# ENDPOINTS DE PROGRAMAS
# =========================================================

@programas_bp.route('', methods=['GET'])
@require_auth_session
def listar_programas():
    """Obtener lista de todos los programas con filtros opcionales"""
    try:
        # Parámetros de filtro
        busqueda = request.args.get('busqueda', '').strip()
        tipo = request.args.get('tipo', '').strip()
        estado = request.args.get('estado', '').strip()
        
        # Construir query con filtros
        query = """
            SELECT id, codigo_programa, nombre_programa, tipo_programa,
                   descripcion, duracion_meses, estado
            FROM programas_formacion
            WHERE 1=1
        """
        params = []
        
        if busqueda:
            query += " AND (codigo_programa LIKE %s OR nombre_programa LIKE %s OR descripcion LIKE %s)"
            params.extend([f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'])
        
        if tipo:
            query += " AND tipo_programa = %s"
            params.append(tipo)
        
        if estado:
            query += " AND estado = %s"
            params.append(estado)
        
        query += " ORDER BY nombre_programa"
        
        programas = db.ejecutar_query(query, tuple(params) if params else None) or []
        
        return jsonify({
            'success': True, 
            'programas': programas,
            'total': len(programas)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo programas: {str(e)}'}), 500

@programas_bp.route('/validar', methods=['GET'])
@require_auth_session
def validar_codigo_programa():
    """GET /api/programas/validar?codigo=XXX&excluir_id=YYY - Verificar si código existe"""
    try:
        codigo = request.args.get('codigo', '').strip()
        excluir_id = request.args.get('excluir_id', '')
        
        if not codigo:
            return jsonify({'success': True, 'existe': False}), 200
        
        if excluir_id:
            query = "SELECT id FROM programas_formacion WHERE codigo_programa = %s AND id != %s"
            resultado = db.obtener_uno(query, (codigo, int(excluir_id)))
        else:
            query = "SELECT id FROM programas_formacion WHERE codigo_programa = %s"
            resultado = db.obtener_uno(query, (codigo,))
        
        return jsonify({'success': True, 'existe': resultado is not None}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@programas_bp.route('/<int:programa_id>', methods=['GET'])
@require_auth_session
def obtener_programa(programa_id):
    """Obtener un programa específico por ID"""
    try:
        query = """
            SELECT id, codigo_programa, nombre_programa, tipo_programa,
                   descripcion, duracion_meses, estado
            FROM programas_formacion
            WHERE id = %s
        """
        programa = db.obtener_uno(query, (programa_id,))
        
        if not programa:
            return jsonify({'success': False, 'message': 'Programa no encontrado'}), 404
        
        return jsonify({'success': True, 'programa': programa}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo programa: {str(e)}'}), 500

@programas_bp.route('', methods=['POST'])
@require_permission('programas')
def crear_programa():
    """Crear un nuevo programa de formación"""
    try:
        data = request.get_json()
        
        codigo = data.get('codigo_programa', '').strip()
        nombre = data.get('nombre_programa', '').strip()
        tipo = data.get('tipo_programa', '').strip()
        descripcion = data.get('descripcion', '').strip()
        duracion = data.get('duracion_meses')
        estado = data.get('estado', 'activo')
        
        # Validaciones
        if not codigo:
            return jsonify({'success': False, 'message': 'El código del programa es requerido'}), 400
        if not nombre:
            return jsonify({'success': False, 'message': 'El nombre del programa es requerido'}), 400
        if not tipo or tipo not in ['tecnico', 'tecnologo', 'complementaria']:
            return jsonify({'success': False, 'message': 'El tipo de programa es inválido'}), 400
        
        # Verificar código duplicado
        query_check = "SELECT id FROM programas_formacion WHERE codigo_programa = %s"
        existe = db.obtener_uno(query_check, (codigo,))
        if existe:
            return jsonify({'success': False, 'message': 'Ya existe un programa con ese código'}), 400
        
        # Insertar programa
        query = """
            INSERT INTO programas_formacion 
            (codigo_programa, nombre_programa, tipo_programa, descripcion, duracion_meses, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.ejecutar_comando(query, (codigo, nombre, tipo, descripcion, duracion, estado))
        
        # Obtener ID del programa creado
        query_id = "SELECT LAST_INSERT_ID() as id"
        result = db.obtener_uno(query_id)
        nuevo_id = result['id'] if result else None
        
        return jsonify({
            'success': True, 
            'message': 'Programa creado exitosamente',
            'programa_id': nuevo_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando programa: {str(e)}'}), 500

@programas_bp.route('/<int:programa_id>', methods=['PUT'])
@require_permission('programas')
def actualizar_programa(programa_id):
    """Actualizar un programa existente"""
    try:
        data = request.get_json()
        
        # Verificar que el programa existe
        query_check = "SELECT id FROM programas_formacion WHERE id = %s"
        existe = db.obtener_uno(query_check, (programa_id,))
        if not existe:
            return jsonify({'success': False, 'message': 'Programa no encontrado'}), 404
        
        codigo = data.get('codigo_programa', '').strip()
        nombre = data.get('nombre_programa', '').strip()
        tipo = data.get('tipo_programa', '').strip()
        descripcion = data.get('descripcion', '').strip()
        duracion = data.get('duracion_meses')
        estado = data.get('estado')
        
        # Verificar código duplicado (si se está cambiando)
        if codigo:
            query_dup = "SELECT id FROM programas_formacion WHERE codigo_programa = %s AND id != %s"
            duplicado = db.obtener_uno(query_dup, (codigo, programa_id))
            if duplicado:
                return jsonify({'success': False, 'message': 'Ya existe otro programa con ese código'}), 400
        
        # Construir query de actualización
        updates = []
        params = []
        
        if codigo:
            updates.append("codigo_programa = %s")
            params.append(codigo)
        
        if nombre:
            updates.append("nombre_programa = %s")
            params.append(nombre)
        
        if tipo:
            if tipo not in ['tecnico', 'tecnologo', 'complementaria']:
                return jsonify({'success': False, 'message': 'Tipo de programa inválido'}), 400
            updates.append("tipo_programa = %s")
            params.append(tipo)
        
        if descripcion is not None:
            updates.append("descripcion = %s")
            params.append(descripcion)
        
        if duracion is not None:
            updates.append("duracion_meses = %s")
            params.append(duracion)
        
        if estado:
            updates.append("estado = %s")
            params.append(estado)
        
        if not updates:
            return jsonify({'success': False, 'message': 'No hay datos para actualizar'}), 400
        
        params.append(programa_id)
        query = f"UPDATE programas_formacion SET {', '.join(updates)} WHERE id = %s"
        db.ejecutar_comando(query, tuple(params))
        
        return jsonify({'success': True, 'message': 'Programa actualizado exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando programa: {str(e)}'}), 500

@programas_bp.route('/tipos', methods=['GET'])
@require_auth_session
def obtener_tipos():
    """Obtener tipos de programas disponibles"""
    tipos = [
        {'value': 'tecnico', 'label': 'Técnico'},
        {'value': 'tecnologo', 'label': 'Tecnólogo'},
        {'value': 'complementaria', 'label': 'Complementaria'}
    ]
    return jsonify({'success': True, 'tipos': tipos}), 200

@programas_bp.route('/estadisticas', methods=['GET'])
@require_auth_session
def obtener_estadisticas():
    """Obtener estadísticas de programas"""
    try:
        stats = {
            'total': 0,
            'activos': 0,
            'inactivos': 0,
            'por_tipo': {}
        }
        
        # Total y por estado
        query_total = "SELECT estado, COUNT(*) as total FROM programas_formacion GROUP BY estado"
        resultados = db.ejecutar_query(query_total) or []
        for r in resultados:
            stats['total'] += r['total']
            if r['estado'] == 'activo':
                stats['activos'] = r['total']
            else:
                stats['inactivos'] = r['total']
        
        # Por tipo
        query_tipo = "SELECT tipo_programa, COUNT(*) as total FROM programas_formacion GROUP BY tipo_programa"
        resultados_tipo = db.ejecutar_query(query_tipo) or []
        for r in resultados_tipo:
            stats['por_tipo'][r['tipo_programa']] = r['total']
        
        return jsonify({'success': True, 'estadisticas': stats}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo estadísticas: {str(e)}'}), 500
