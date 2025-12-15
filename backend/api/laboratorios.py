# API de Gestión de Laboratorios
# Centro Minero SENA

from flask import Blueprint, request, jsonify, session
from ..utils.database import DatabaseManager
from ..utils.validators import Validator

laboratorios_bp = Blueprint('laboratorios', __name__, url_prefix='/api/laboratorios')
db = DatabaseManager()

def require_auth_session(f):
    """Decorador simple para verificar sesión"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
        return f(*args, **kwargs)
    return decorated


@laboratorios_bp.route('', methods=['GET'])
@require_auth_session
def listar_laboratorios():
    """GET /api/laboratorios - Listar todos los laboratorios"""
    try:
        query = """
            SELECT l.id, l.codigo_lab, l.nombre, l.tipo, l.ubicacion,
                   l.capacidad_personas, l.area_m2, l.responsable_id, l.estado,
                   DATE_FORMAT(l.fecha_creacion, '%d/%m/%Y') as fecha_creacion,
                   CONCAT(u.nombres, ' ', u.apellidos) as responsable_nombre
            FROM laboratorios l
            LEFT JOIN usuarios u ON l.responsable_id = u.id
            ORDER BY l.nombre
        """
        laboratorios = db.ejecutar_query(query) or []
        
        # Formatear para el frontend
        labs_formateados = []
        for lab in laboratorios:
            labs_formateados.append({
                'id': lab['id'],
                'codigo': lab['codigo_lab'],
                'codigo_lab': lab['codigo_lab'],
                'nombre': lab['nombre'],
                'tipo': lab['tipo'],
                'ubicacion': lab['ubicacion'],
                'capacidad_personas': lab['capacidad_personas'],
                'capacidad_estudiantes': lab['capacidad_personas'],
                'area_m2': float(lab['area_m2']) if lab['area_m2'] else None,
                'responsable_id': lab['responsable_id'],
                'responsable_nombre': lab['responsable_nombre'],
                'estado': lab['estado'],
                'fecha_creacion': lab['fecha_creacion'],
                'total_equipos': 0,
                'total_items': 0,
                'items_criticos': 0
            })
        
        return jsonify({'success': True, 'laboratorios': labs_formateados}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error listando laboratorios: {str(e)}'}), 500


@laboratorios_bp.route('/<int:lab_id>', methods=['GET'])
@require_auth_session
def obtener_laboratorio(lab_id):
    """GET /api/laboratorios/{id} - Obtener laboratorio específico"""
    try:
        query = """
            SELECT l.id, l.codigo_lab, l.nombre, l.tipo, l.ubicacion,
                   l.capacidad_personas, l.area_m2, l.responsable_id, l.estado,
                   DATE_FORMAT(l.fecha_creacion, '%d/%m/%Y') as fecha_creacion,
                   CONCAT(u.nombres, ' ', u.apellidos) as responsable_nombre
            FROM laboratorios l
            LEFT JOIN usuarios u ON l.responsable_id = u.id
            WHERE l.id = %s
        """
        lab = db.obtener_uno(query, (lab_id,))
        
        if not lab:
            return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
        
        laboratorio = {
            'id': lab['id'],
            'codigo': lab['codigo_lab'],
            'codigo_lab': lab['codigo_lab'],
            'nombre': lab['nombre'],
            'tipo': lab['tipo'],
            'ubicacion': lab['ubicacion'],
            'capacidad_personas': lab['capacidad_personas'],
            'capacidad_estudiantes': lab['capacidad_personas'],
            'area_m2': float(lab['area_m2']) if lab['area_m2'] else None,
            'responsable_id': lab['responsable_id'],
            'responsable': lab['responsable_nombre'],
            'estado': lab['estado'],
            'fecha_creacion': lab['fecha_creacion']
        }
        
        return jsonify({'success': True, 'laboratorio': laboratorio}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo laboratorio: {str(e)}'}), 500


@laboratorios_bp.route('', methods=['POST'])
@require_auth_session
def crear_laboratorio():
    """POST /api/laboratorios - Crear nuevo laboratorio"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        # Obtener y sanitizar campos
        codigo = Validator.sanitizar_texto(data.get('codigo', '') or data.get('codigo_lab', ''))
        nombre = Validator.sanitizar_texto(data.get('nombre', ''))
        tipo = data.get('tipo', '').strip()
        
        # Recopilar todos los errores
        errores = {}
        tipos_validos = ['quimica', 'mineria', 'suelos', 'metalurgia', 'general']
        estados_validos = ['disponible', 'ocupado', 'mantenimiento', 'fuera_servicio']
        
        # Validar código
        if not codigo:
            errores['codigo'] = 'El código es requerido'
        elif not Validator.validar_longitud(codigo, 3, 20):
            errores['codigo'] = 'El código debe tener entre 3 y 20 caracteres'
        elif db.existe('laboratorios', 'codigo_lab = %s', (codigo,)):
            errores['codigo'] = 'Ya existe un laboratorio con ese código'
        
        # Validar nombre
        if not nombre:
            errores['nombre'] = 'El nombre es requerido'
        elif not Validator.validar_longitud(nombre, 3, 100):
            errores['nombre'] = 'El nombre debe tener entre 3 y 100 caracteres'
        
        # Validar tipo
        if not tipo:
            errores['tipo'] = 'El tipo es requerido'
        elif not Validator.validar_enum(tipo, tipos_validos):
            errores['tipo'] = f'Tipo inválido. Debe ser: {", ".join(tipos_validos)}'
        
        # Validar capacidad
        capacidad = data.get('capacidad_personas') or data.get('capacidad_estudiantes') or 20
        try:
            capacidad = int(capacidad)
            if capacidad < 1 or capacidad > 100:
                errores['capacidad'] = 'La capacidad debe estar entre 1 y 100'
        except (ValueError, TypeError):
            capacidad = 20
        
        # Si hay errores, devolverlos todos
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        # Validar estado
        estado = data.get('estado', 'disponible')
        if not Validator.validar_enum(estado, estados_validos):
            estado = 'disponible'
        
        # Preparar datos
        datos_lab = {
            'codigo_lab': codigo,
            'nombre': nombre,
            'tipo': tipo,
            'ubicacion': Validator.sanitizar_texto(data.get('ubicacion', '')) or None,
            'capacidad_personas': capacidad,
            'area_m2': float(data.get('area_m2')) if data.get('area_m2') else None,
            'responsable_id': int(data.get('responsable_id')) if data.get('responsable_id') else None,
            'estado': estado
        }
        
        nuevo_id = db.insertar('laboratorios', datos_lab)
        
        if nuevo_id:
            return jsonify({
                'success': True,
                'message': 'Laboratorio creado exitosamente',
                'laboratorio_id': nuevo_id
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Error al crear laboratorio'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando laboratorio: {str(e)}'}), 500


@laboratorios_bp.route('/<int:lab_id>', methods=['PUT'])
@require_auth_session
def actualizar_laboratorio(lab_id):
    """PUT /api/laboratorios/{id} - Actualizar laboratorio"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No hay datos para actualizar'}), 400
        
        if not db.existe('laboratorios', 'id = %s', (lab_id,)):
            return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
        
        datos_actualizar = {}
        errores = {}
        tipos_validos = ['quimica', 'mineria', 'suelos', 'metalurgia', 'general']
        estados_validos = ['disponible', 'ocupado', 'mantenimiento', 'fuera_servicio']
        
        # Código
        if 'codigo' in data or 'codigo_lab' in data:
            codigo = Validator.sanitizar_texto(data.get('codigo', '') or data.get('codigo_lab', ''))
            if codigo:
                if not Validator.validar_longitud(codigo, 3, 20):
                    errores['codigo'] = 'El código debe tener entre 3 y 20 caracteres'
                else:
                    query_check = "SELECT id FROM laboratorios WHERE codigo_lab = %s AND id != %s"
                    existe = db.obtener_uno(query_check, (codigo, lab_id))
                    if existe:
                        errores['codigo'] = 'Ya existe otro laboratorio con ese código'
                    else:
                        datos_actualizar['codigo_lab'] = codigo
        
        # Nombre
        if 'nombre' in data and data['nombre']:
            nombre = Validator.sanitizar_texto(data['nombre'])
            if not Validator.validar_longitud(nombre, 3, 100):
                errores['nombre'] = 'El nombre debe tener entre 3 y 100 caracteres'
            else:
                datos_actualizar['nombre'] = nombre
        
        # Tipo
        if 'tipo' in data and data['tipo']:
            if Validator.validar_enum(data['tipo'], tipos_validos):
                datos_actualizar['tipo'] = data['tipo']
        
        # Ubicación
        if 'ubicacion' in data:
            datos_actualizar['ubicacion'] = Validator.sanitizar_texto(data['ubicacion']) if data['ubicacion'] else None
        
        # Capacidad
        if 'capacidad_personas' in data or 'capacidad_estudiantes' in data:
            cap = data.get('capacidad_personas') or data.get('capacidad_estudiantes')
            if cap:
                try:
                    cap = int(cap)
                    if cap < 1 or cap > 100:
                        errores['capacidad'] = 'La capacidad debe estar entre 1 y 100'
                    else:
                        datos_actualizar['capacidad_personas'] = cap
                except (ValueError, TypeError):
                    pass
        
        # Área
        if 'area_m2' in data:
            datos_actualizar['area_m2'] = float(data['area_m2']) if data['area_m2'] else None
        
        # Responsable
        if 'responsable_id' in data:
            datos_actualizar['responsable_id'] = int(data['responsable_id']) if data['responsable_id'] else None
        
        # Estado
        if 'estado' in data and data['estado']:
            if Validator.validar_enum(data['estado'], estados_validos):
                datos_actualizar['estado'] = data['estado']
        
        # Si hay errores, devolverlos todos
        if errores:
            return jsonify({'success': False, 'errores': errores}), 400
        
        if datos_actualizar:
            db.actualizar('laboratorios', datos_actualizar, 'id = %s', (lab_id,))
        
        return jsonify({
            'success': True,
            'message': 'Laboratorio actualizado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error actualizando laboratorio: {str(e)}'}), 500


@laboratorios_bp.route('/validar', methods=['POST'])
@require_auth_session
def validar_laboratorio():
    """POST /api/laboratorios/validar - Validar datos de laboratorio en tiempo real"""
    try:
        data = request.get_json() or {}
        excluir_id = data.get('excluir_id')
        
        errores = {}
        tipos_validos = ['quimica', 'mineria', 'suelos', 'metalurgia', 'general']
        
        # Validar código
        codigo = Validator.sanitizar_texto(data.get('codigo', '') or data.get('codigo_lab', ''))
        if 'codigo' in data or 'codigo_lab' in data:
            if not codigo:
                errores['codigo'] = 'El código es requerido'
            elif not Validator.validar_longitud(codigo, 3, 20):
                errores['codigo'] = 'El código debe tener entre 3 y 20 caracteres'
            else:
                # Verificar único
                if excluir_id:
                    query = "SELECT id FROM laboratorios WHERE codigo_lab = %s AND id != %s"
                    existe = db.obtener_uno(query, (codigo, int(excluir_id)))
                else:
                    existe = db.existe('laboratorios', 'codigo_lab = %s', (codigo,))
                if existe:
                    errores['codigo'] = 'Ya existe un laboratorio con ese código'
        
        # Validar nombre
        nombre = Validator.sanitizar_texto(data.get('nombre', ''))
        if 'nombre' in data:
            if not nombre:
                errores['nombre'] = 'El nombre es requerido'
            elif not Validator.validar_longitud(nombre, 3, 100):
                errores['nombre'] = 'El nombre debe tener entre 3 y 100 caracteres'
        
        # Validar tipo
        tipo = data.get('tipo', '').strip()
        if 'tipo' in data:
            if not tipo:
                errores['tipo'] = 'El tipo es requerido'
            elif not Validator.validar_enum(tipo, tipos_validos):
                errores['tipo'] = f'Tipo inválido. Debe ser: {", ".join(tipos_validos)}'
        
        # Validar capacidad
        if 'capacidad_personas' in data or 'capacidad' in data:
            cap = data.get('capacidad_personas') or data.get('capacidad')
            if cap:
                try:
                    cap = int(cap)
                    if cap < 1 or cap > 100:
                        errores['capacidad'] = 'La capacidad debe estar entre 1 y 100'
                except (ValueError, TypeError):
                    errores['capacidad'] = 'La capacidad debe ser un número válido'
        
        return jsonify({'success': len(errores) == 0, 'errores': errores}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@laboratorios_bp.route('/estadisticas', methods=['GET'])
@require_auth_session
def estadisticas_laboratorios():
    """GET /api/laboratorios/estadisticas - Estadísticas de laboratorios"""
    try:
        # Contar por tipo
        query_tipos = """
            SELECT tipo, COUNT(*) as total
            FROM laboratorios
            GROUP BY tipo
        """
        tipos = db.ejecutar_query(query_tipos) or []
        
        # Contar por estado
        query_estados = """
            SELECT estado, COUNT(*) as total
            FROM laboratorios
            GROUP BY estado
        """
        estados = db.ejecutar_query(query_estados) or []
        
        # Total
        query_total = "SELECT COUNT(*) as total FROM laboratorios"
        total = db.obtener_uno(query_total)
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'total': total['total'] if total else 0,
                'por_tipo': {t['tipo']: t['total'] for t in tipos},
                'por_estado': {e['estado']: e['total'] for e in estados}
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo estadísticas: {str(e)}'}), 500
