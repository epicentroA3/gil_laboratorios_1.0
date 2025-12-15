# API de Gestión de Equipos
# Centro Minero SENA

from flask import request, jsonify, send_file, session
from functools import wraps
from .blueprints import equipos_bp
from ..utils.database import DatabaseManager
import json
import os

db = DatabaseManager()

def require_auth_or_session(f):
    """Decorador que permite autenticación por sesión web o JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verificar sesión web
        if 'user_id' in session:
            return f(*args, **kwargs)
        # Verificar JWT
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            try:
                from config.api_config import JWTManager
                payload, error = JWTManager.decode_token(token)
                if payload:
                    return f(*args, **kwargs)
            except:
                pass
        return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
    return decorated

@equipos_bp.route('', methods=['GET'])
@require_auth_or_session
def listar_equipos():
    """GET /api/equipos - Listar todos los equipos
    
    Query params:
        - estado: Filtrar por estado (disponible, prestado, mantenimiento, reparacion, dado_baja)
    """
    try:
        # Filtro por estado
        estado_filtro = request.args.get('estado')
        
        query = """
            SELECT 
                e.id,
                e.codigo_interno,
                e.nombre,
                e.marca,
                e.modelo,
                CONCAT(e.marca, ' ', e.modelo) as tipo,
                e.estado,
                e.estado_fisico,
                e.ubicacion_especifica as ubicacion,
                e.especificaciones_tecnicas as especificaciones,
                e.imagen_url,
                e.id_laboratorio,
                l.nombre as laboratorio_nombre,
                l.codigo_lab as laboratorio_codigo,
                c.nombre as categoria_nombre,
                DATE_FORMAT(e.fecha_adquisicion, '%d/%m/%Y') as fecha_adquisicion
            FROM equipos e
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
        """
        
        params = []
        if estado_filtro:
            query += " WHERE e.estado = %s"
            params.append(estado_filtro)
        
        query += " ORDER BY e.nombre"
        
        equipos = db.ejecutar_query(query, tuple(params) if params else None)
        
        # Procesar especificaciones JSON
        for equipo in equipos:
            if equipo['especificaciones']:
                try:
                    equipo['especificaciones'] = json.loads(equipo['especificaciones'])
                except:
                    equipo['especificaciones'] = {}
        
        return jsonify({'success': True, 'equipos': equipos}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error listando equipos: {str(e)}'}), 500

@equipos_bp.route('/<int:equipo_id>', methods=['GET'])
@require_auth_or_session
def obtener_equipo(equipo_id):
    """GET /api/equipos/{id} - Obtener equipo específico"""
    try:
        query = """
            SELECT 
                e.id,
                e.codigo_interno,
                e.nombre,
                e.marca,
                e.modelo,
                CONCAT(e.marca, ' ', e.modelo) as tipo,
                e.estado,
                e.estado_fisico,
                e.ubicacion_especifica as ubicacion,
                e.especificaciones_tecnicas as especificaciones,
                e.imagen_url,
                e.id_laboratorio,
                l.nombre as laboratorio_nombre,
                c.nombre as categoria_nombre,
                DATE_FORMAT(e.fecha_adquisicion, '%d/%m/%Y') as fecha_adquisicion,
                e.valor_adquisicion,
                e.proveedor,
                e.garantia_meses,
                e.vida_util_anos,
                DATE_FORMAT(e.fecha_registro, '%d/%m/%Y') as fecha_registro
            FROM equipos e
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            WHERE e.id = %s
        """
        equipo = db.obtener_uno(query, (equipo_id,))
        
        if not equipo:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        if equipo['especificaciones']:
            try:
                equipo['especificaciones'] = json.loads(equipo['especificaciones'])
            except:
                equipo['especificaciones'] = {}
        
        return jsonify({'success': True, 'equipo': equipo}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo equipo: {str(e)}'}), 500

@equipos_bp.route('', methods=['POST'])
@require_auth_or_session
def crear_equipo():
    """POST /api/equipos - Crear nuevo equipo con validaciones según schema BD"""
    try:
        data = request.get_json()
        
        # === VALIDACIONES SEGÚN SCHEMA BD ===
        # nombre: VARCHAR(200) NOT NULL - OBLIGATORIO
        if not data or 'nombre' not in data or not data['nombre'].strip():
            return jsonify({'error': 'Nombre es requerido (NOT NULL)'}), 400
        
        nombre = data['nombre'].strip()
        if len(nombre) > 200:
            return jsonify({'error': 'Nombre muy largo (máx 200 caracteres)'}), 400
        
        # Validar longitudes de campos VARCHAR opcionales
        if data.get('marca') and len(data['marca']) > 100:
            return jsonify({'error': 'Marca muy larga (máx 100 caracteres)'}), 400
        if data.get('modelo') and len(data['modelo']) > 100:
            return jsonify({'error': 'Modelo muy largo (máx 100 caracteres)'}), 400
        if data.get('numero_serie') and len(data['numero_serie']) > 150:
            return jsonify({'error': 'Número de serie muy largo (máx 150 caracteres)'}), 400
        if data.get('proveedor') and len(data['proveedor']) > 200:
            return jsonify({'error': 'Proveedor muy largo (máx 200 caracteres)'}), 400
        if data.get('ubicacion') and len(data['ubicacion']) > 200:
            return jsonify({'error': 'Ubicación muy larga (máx 200 caracteres)'}), 400
        if data.get('codigo_qr') and len(data['codigo_qr']) > 255:
            return jsonify({'error': 'Código QR muy largo (máx 255 caracteres)'}), 400
        if data.get('imagen_url') and len(data['imagen_url']) > 500:
            return jsonify({'error': 'URL de imagen muy larga (máx 500 caracteres)'}), 400
        if data.get('imagen_hash') and len(data['imagen_hash']) > 64:
            return jsonify({'error': 'Hash de imagen muy largo (máx 64 caracteres)'}), 400
        
        # Validar ENUM estado
        estados_validos = ['disponible', 'prestado', 'mantenimiento', 'reparacion', 'dado_baja']
        if data.get('estado') and data['estado'] not in estados_validos:
            return jsonify({'error': f'Estado inválido. Valores válidos: {estados_validos}'}), 400
        
        # Validar ENUM estado_fisico
        estados_fisicos_validos = ['excelente', 'bueno', 'regular', 'malo']
        if data.get('estado_fisico') and data['estado_fisico'] not in estados_fisicos_validos:
            return jsonify({'error': f'Estado físico inválido. Valores válidos: {estados_fisicos_validos}'}), 400
        
        # Validar DECIMAL(12,2) valor_adquisicion
        if data.get('valor_adquisicion'):
            try:
                valor = float(data['valor_adquisicion'])
                if valor < 0 or valor > 9999999999.99:
                    return jsonify({'error': 'Valor de adquisición fuera de rango (DECIMAL 12,2)'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Valor de adquisición inválido'}), 400
        
        import uuid
        codigo_interno = f"EQP-{uuid.uuid4().hex[:8].upper()}"
        
        # Construir datos del equipo con todos los campos posibles
        datos_equipo = {
            'codigo_interno': codigo_interno,
            'nombre': data['nombre'],
            'marca': data.get('marca', ''),
            'modelo': data.get('modelo', ''),
            'numero_serie': data.get('numero_serie', ''),
            'estado': data.get('estado', 'disponible'),
            'estado_fisico': data.get('estado_fisico', 'bueno'),
            'ubicacion_especifica': data.get('ubicacion', ''),
            'descripcion': data.get('descripcion', ''),
            'observaciones': data.get('observaciones', '')
        }
        
        # Campos opcionales con FK
        if data.get('id_laboratorio'):
            datos_equipo['id_laboratorio'] = int(data['id_laboratorio'])
        if data.get('id_categoria'):
            datos_equipo['id_categoria'] = int(data['id_categoria'])
        
        # Especificaciones técnicas
        specs = data.get('especificaciones_tecnicas') or data.get('especificaciones', '')
        if isinstance(specs, dict):
            datos_equipo['especificaciones_tecnicas'] = json.dumps(specs)
        else:
            datos_equipo['especificaciones_tecnicas'] = specs
        
        # Datos de adquisición
        if data.get('valor_adquisicion'):
            datos_equipo['valor_adquisicion'] = float(data['valor_adquisicion'])
        if data.get('fecha_adquisicion'):
            datos_equipo['fecha_adquisicion'] = data['fecha_adquisicion']
        if data.get('proveedor'):
            datos_equipo['proveedor'] = data['proveedor']
        if data.get('garantia_meses'):
            datos_equipo['garantia_meses'] = int(data['garantia_meses'])
        if data.get('vida_util_anos'):
            datos_equipo['vida_util_anos'] = int(data['vida_util_anos'])
        
        # Campos de imagen y QR
        if data.get('codigo_qr'):
            datos_equipo['codigo_qr'] = data['codigo_qr']
        if 'imagen_url' in data and data['imagen_url']:
            datos_equipo['imagen_url'] = data['imagen_url']
            print(f"📷 imagen_url recibida: {data['imagen_url']}")
        if data.get('imagen_hash'):
            datos_equipo['imagen_hash'] = data['imagen_hash']
        
        # Remover campos vacíos
        datos_equipo = {k: v for k, v in datos_equipo.items() if v is not None and v != ''}
        
        equipo_id = db.insertar('equipos', datos_equipo)
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'id': equipo_id,
            'codigo_interno': codigo_interno
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creando equipo: {str(e)}'}), 500

@equipos_bp.route('/<int:equipo_id>', methods=['PUT'])
@require_auth_or_session
def actualizar_equipo(equipo_id):
    """PUT /api/equipos/{id} - Actualizar equipo con todos los campos"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        existe = db.obtener_uno("SELECT id FROM equipos WHERE id = %s", (equipo_id,))
        if not existe:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        # Mapeo de campos permitidos
        campos_permitidos = {
            'nombre': 'nombre',
            'marca': 'marca',
            'modelo': 'modelo',
            'numero_serie': 'numero_serie',
            'estado': 'estado',
            'estado_fisico': 'estado_fisico',
            'ubicacion': 'ubicacion_especifica',
            'descripcion': 'descripcion',
            'observaciones': 'observaciones',
            'id_laboratorio': 'id_laboratorio',
            'id_categoria': 'id_categoria',
            'proveedor': 'proveedor'
        }
        
        datos_actualizar = {}
        for campo_entrada, campo_bd in campos_permitidos.items():
            if campo_entrada in data:
                datos_actualizar[campo_bd] = data[campo_entrada]
        
        # Especificaciones técnicas
        if 'especificaciones' in data or 'especificaciones_tecnicas' in data:
            specs = data.get('especificaciones_tecnicas') or data.get('especificaciones', '')
            if isinstance(specs, dict):
                datos_actualizar['especificaciones_tecnicas'] = json.dumps(specs)
            else:
                datos_actualizar['especificaciones_tecnicas'] = specs
        
        # Campos numéricos
        if 'valor_adquisicion' in data and data['valor_adquisicion']:
            datos_actualizar['valor_adquisicion'] = float(data['valor_adquisicion'])
        if 'garantia_meses' in data and data['garantia_meses']:
            datos_actualizar['garantia_meses'] = int(data['garantia_meses'])
        if 'vida_util_anos' in data and data['vida_util_anos']:
            datos_actualizar['vida_util_anos'] = int(data['vida_util_anos'])
        
        # Fecha de adquisición
        if 'fecha_adquisicion' in data:
            datos_actualizar['fecha_adquisicion'] = data['fecha_adquisicion'] if data['fecha_adquisicion'] else None
        
        # Campos de imagen y QR
        if 'codigo_qr' in data:
            datos_actualizar['codigo_qr'] = data['codigo_qr'] if data['codigo_qr'] else None
        if 'imagen_url' in data:
            datos_actualizar['imagen_url'] = data['imagen_url'] if data['imagen_url'] else None
        if 'imagen_hash' in data:
            datos_actualizar['imagen_hash'] = data['imagen_hash'] if data['imagen_hash'] else None
        
        if not datos_actualizar:
            return jsonify({'error': 'No hay campos válidos para actualizar'}), 400
        
        db.actualizar('equipos', datos_actualizar, 'id = %s', (equipo_id,))
        
        return jsonify({
            'success': True,
            'message': 'Equipo actualizado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error actualizando equipo: {str(e)}'}), 500

@equipos_bp.route('/<int:equipo_id>', methods=['DELETE'])
@require_auth_or_session
def eliminar_equipo(equipo_id):
    """DELETE /api/equipos/{id} - Eliminar equipo"""
    try:
        existe = db.obtener_uno("SELECT id FROM equipos WHERE id = %s", (equipo_id,))
        if not existe:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        db.eliminar('equipos', 'id = %s', (equipo_id,))
        
        return jsonify({
            'success': True,
            'message': 'Equipo eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error eliminando equipo: {str(e)}'}), 500

@equipos_bp.route('/buscar-qr', methods=['GET'])
@require_auth_or_session
def buscar_por_qr():
    """GET /api/equipos/buscar-qr?codigo=XXX - Buscar equipo por código escaneado del QR"""
    try:
        codigo = request.args.get('codigo', '').strip()
        
        if not codigo:
            return jsonify({'success': False, 'error': 'Código requerido'}), 400
        
        # Buscar equipo por codigo_interno
        query = """
            SELECT e.id, e.codigo_interno, e.nombre, e.marca, e.modelo,
                   e.estado, e.estado_fisico, e.ubicacion_especifica as ubicacion,
                   e.imagen_url, c.nombre as categoria, l.nombre as laboratorio
            FROM equipos e
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            WHERE e.codigo_interno = %s
        """
        equipo = db.obtener_uno(query, (codigo,))
        
        if not equipo:
            return jsonify({
                'success': False, 
                'error': f'Equipo con código "{codigo}" no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'equipo': {
                'id': equipo['id'],
                'codigo_interno': equipo['codigo_interno'],
                'nombre': equipo['nombre'],
                'marca': equipo.get('marca', ''),
                'modelo': equipo.get('modelo', ''),
                'estado': equipo.get('estado', 'disponible'),
                'estado_fisico': equipo.get('estado_fisico', 'bueno'),
                'ubicacion': equipo.get('ubicacion', ''),
                'imagen_url': equipo.get('imagen_url', ''),
                'categoria': equipo.get('categoria', 'General'),
                'laboratorio': equipo.get('laboratorio', 'Sin asignar')
            },
            'metodo': 'qr_scan'
        }), 200
        
    except Exception as e:
        print(f"Error buscando equipo por QR: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@equipos_bp.route('/<int:equipo_id>/qr', methods=['GET'])
@require_auth_or_session
def generar_qr(equipo_id):
    """GET /api/equipos/{id}/qr - Generar código QR del equipo"""
    try:
        query = "SELECT id, codigo_interno, nombre, ubicacion_especifica as ubicacion FROM equipos WHERE id = %s"
        equipo = db.obtener_uno(query, (equipo_id,))
        
        if not equipo:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        # Generar código QR simple con qrcode
        import qrcode
        import io
        import base64
        
        qr_content = f"EQUIPO:{equipo.get('codigo_interno', '')}|{equipo.get('nombre', '')}|{equipo.get('ubicacion', '')}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'equipo_id': equipo_id,
            'codigo_interno': equipo.get('codigo_interno', '')
        }), 200
        
    except ImportError as e:
        print(f"Error importando qrcode: {e}")
        return jsonify({'error': 'Módulo qrcode no instalado. Ejecute: pip install qrcode[pil]'}), 500
    except Exception as e:
        print(f"Error generando QR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error generando QR: {str(e)}'}), 500

@equipos_bp.route('/<int:equipo_id>/imagen', methods=['POST'])
@require_auth_or_session
def subir_imagen(equipo_id):
    """POST /api/equipos/{id}/imagen - Subir imagen del equipo"""
    try:
        print(f"📷 Subiendo imagen para equipo {equipo_id}")
        print(f"📷 Content-Type: {request.content_type}")
        print(f"📷 Files: {list(request.files.keys())}")
        
        existe = db.obtener_uno("SELECT id FROM equipos WHERE id = %s", (equipo_id,))
        if not existe:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        # Primero verificar si hay archivo en request.files
        imagen_base64 = None
        if 'imagen' not in request.files:
            # Si no hay archivo, intentar obtener base64 del JSON
            try:
                data = request.get_json() or {}
                imagen_base64 = data.get('image_base64') or data.get('imagen_data')
            except:
                pass
        
        if not imagen_base64 and 'imagen' not in request.files:
            print(f"📷 ERROR: No se encontró imagen en files ni en JSON")
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        import hashlib
        import base64
        
        # Procesar imagen
        if 'imagen' in request.files:
            imagen_data = request.files['imagen'].read()
        else:
            if ',' in imagen_base64:
                imagen_base64 = imagen_base64.split(',')[1]
            imagen_data = base64.b64decode(imagen_base64)
        
        # Calcular hash
        imagen_hash = hashlib.md5(imagen_data).hexdigest()
        
        # Guardar imagen
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'equipos')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{equipo_id}_{imagen_hash[:8]}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(imagen_data)
        
        # URL accesible desde el navegador (relativa al servidor)
        imagen_url_web = f"/uploads/equipos/{filename}"
        
        # Actualizar BD con URL web accesible
        db.actualizar('equipos', {
            'imagen_url': imagen_url_web,
            'imagen_hash': imagen_hash
        }, 'id = %s', (equipo_id,))
        
        print(f"📷 Imagen guardada: {filepath} -> URL: {imagen_url_web}")
        
        return jsonify({
            'success': True,
            'message': 'Imagen subida exitosamente',
            'imagen_url': imagen_url_web,
            'imagen_hash': imagen_hash
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error subiendo imagen: {str(e)}'}), 500

@equipos_bp.route('/<int:equipo_id>/imagen', methods=['GET'])
@require_auth_or_session
def obtener_imagen(equipo_id):
    """GET /api/equipos/{id}/imagen - Obtener imagen del equipo"""
    try:
        query = "SELECT imagen_url FROM equipos WHERE id = %s"
        equipo = db.obtener_uno(query, (equipo_id,))
        
        if not equipo:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        if not equipo['imagen_url'] or not os.path.exists(equipo['imagen_url']):
            return jsonify({'error': 'Imagen no disponible'}), 404
        
        return send_file(equipo['imagen_url'], mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo imagen: {str(e)}'}), 500

@equipos_bp.route('/disponibles', methods=['GET'])
@require_auth_or_session
def equipos_disponibles():
    """GET /api/equipos/disponibles - Listar equipos disponibles"""
    try:
        query = """
            SELECT 
                e.id,
                e.codigo_interno,
                e.nombre,
                CONCAT(e.marca, ' ', e.modelo) as tipo,
                e.ubicacion_especifica as ubicacion,
                l.nombre as laboratorio_nombre
            FROM equipos e
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            WHERE e.estado = 'disponible'
            ORDER BY e.nombre
        """
        equipos = db.ejecutar_query(query)
        
        return jsonify({'success': True, 'equipos': equipos}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error listando equipos disponibles: {str(e)}'}), 500

@equipos_bp.route('/reconocer', methods=['POST'])
@equipos_bp.route('/recognize', methods=['POST'])  # Alias para compatibilidad
def reconocer_equipo():
    """POST /api/equipos/reconocer - Reconocer equipo por imagen (prototipo básico)"""
    try:
        # Obtener imagen del request
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        imagen_file = request.files['imagen']
        imagen_data = imagen_file.read()
        
        # Calcular hash de la imagen capturada
        import hashlib
        import cv2
        import numpy as np
        
        # Convertir bytes a imagen OpenCV
        nparr = np.frombuffer(imagen_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Imagen inválida'}), 400
        
        # Calcular hash de la imagen
        img_hash = hashlib.md5(imagen_data).hexdigest()
        
        # Buscar equipos con imágenes similares (comparación básica por hash)
        query = """
            SELECT 
                e.id,
                e.codigo_interno,
                e.nombre,
                CONCAT(e.marca, ' ', e.modelo) as tipo,
                e.estado,
                e.ubicacion_especifica as ubicacion,
                e.imagen_url,
                e.imagen_hash
            FROM equipos e
            WHERE e.imagen_url IS NOT NULL
            ORDER BY e.nombre
        """
        equipos = db.ejecutar_query(query)
        
        # Implementación prototipo: retornar todos los equipos con imagen
        # En producción se haría comparación más sofisticada
        equipos_encontrados = []
        
        for equipo in equipos:
            # Por ahora, agregar todos los equipos que tengan imagen
            # Esto es un prototipo básico según las guías
            equipos_encontrados.append({
                'id': equipo['id'],
                'nombre': equipo['nombre'],
                'tipo': equipo['tipo'],
                'estado': equipo['estado'],
                'ubicacion': equipo['ubicacion'],
                'similitud': 0.75  # Valor simulado para prototipo
            })
        
        if equipos_encontrados:
            return jsonify({
                'success': True,
                'equipos': equipos_encontrados,
                'message': f'Se encontraron {len(equipos_encontrados)} equipos con imagen registrada'
            }), 200
        else:
            return jsonify({
                'success': True,
                'equipos': [],
                'message': 'No se encontraron equipos con imágenes registradas'
            }), 200
            
    except Exception as e:
        print(f"Error en reconocimiento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error reconociendo equipo: {str(e)}'}), 500

@equipos_bp.route('/buscar-por-hash', methods=['POST'])
@require_auth_or_session
def buscar_por_hash():
    """POST /api/equipos/buscar-por-hash - Buscar equipo por hash de imagen"""
    try:
        data = request.get_json()
        imagen_hash = data.get('imagen_hash') or data.get('hash')
        
        if not imagen_hash:
            return jsonify({'error': 'Hash de imagen requerido'}), 400
        
        query = """
            SELECT 
                e.id, e.codigo_interno, e.nombre, e.marca, e.modelo,
                e.estado, e.ubicacion_especifica as ubicacion,
                e.imagen_url, e.imagen_hash,
                l.nombre as laboratorio_nombre,
                c.nombre as categoria_nombre
            FROM equipos e
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            WHERE e.imagen_hash = %s
        """
        equipo = db.obtener_uno(query, (imagen_hash,))
        
        if equipo:
            return jsonify({
                'success': True,
                'encontrado': True,
                'equipo': equipo
            }), 200
        else:
            return jsonify({
                'success': True,
                'encontrado': False,
                'message': 'No se encontró equipo con ese hash de imagen'
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Error buscando equipo: {str(e)}'}), 500

@equipos_bp.route('/categorias', methods=['GET'])
@require_auth_or_session
def listar_categorias():
    """GET /api/equipos/categorias - Listar categorías de equipos"""
    try:
        query = "SELECT id, nombre, codigo, descripcion FROM categorias_equipos ORDER BY nombre"
        categorias = db.ejecutar_query(query) or []
        return jsonify({'success': True, 'categorias': categorias}), 200
    except Exception as e:
        return jsonify({'error': f'Error listando categorías: {str(e)}'}), 500

@equipos_bp.route('/estadisticas', methods=['GET'])
@require_auth_or_session
def estadisticas_equipos():
    """GET /api/equipos/estadisticas - Estadísticas de equipos"""
    try:
        stats = {}
        
        # Por estado
        query_estado = "SELECT estado, COUNT(*) as total FROM equipos GROUP BY estado"
        resultados = db.ejecutar_query(query_estado) or []
        stats['por_estado'] = {r['estado']: r['total'] for r in resultados}
        
        # Por categoría
        query_cat = """
            SELECT c.nombre as categoria, COUNT(e.id) as total 
            FROM equipos e
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            GROUP BY c.nombre
        """
        resultados = db.ejecutar_query(query_cat) or []
        stats['por_categoria'] = {(r['categoria'] or 'Sin categoría'): r['total'] for r in resultados}
        
        # Por laboratorio
        query_lab = """
            SELECT l.nombre as laboratorio, COUNT(e.id) as total 
            FROM equipos e
            LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
            GROUP BY l.nombre
        """
        resultados = db.ejecutar_query(query_lab) or []
        stats['por_laboratorio'] = {(r['laboratorio'] or 'Sin asignar'): r['total'] for r in resultados}
        
        # Total
        query_total = "SELECT COUNT(*) as total FROM equipos"
        resultado = db.obtener_uno(query_total)
        stats['total'] = resultado['total'] if resultado else 0
        
        return jsonify({'success': True, 'estadisticas': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500
