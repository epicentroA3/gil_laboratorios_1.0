"""
API: RECONOCIMIENTO DE EQUIPOS CON INTELIGENCIA ARTIFICIAL
Centro Minero de Sogamoso - SENA

Endpoints para el sistema de reconocimiento de equipos mediante MobileNet
Basado en documento de formulación MGA - Objetivo Específico 1

Endpoints implementados:
- POST /api/reconocimiento/entrenar - Entrenar modelo con nuevos equipos
- POST /api/reconocimiento/identificar - Identificar equipo por imagen
- POST /api/reconocimiento/registrar-equipo - Registrar nuevo equipo con imágenes
- GET /api/reconocimiento/estadisticas - Estadísticas del sistema
- GET /api/reconocimiento/equipos-entrenados - Listar equipos entrenados
- POST /api/reconocimiento/validar-imagen - Validar calidad de imagen
"""

from flask import request, jsonify, session
from .blueprints import reconocimiento_bp
from ..utils.database import DatabaseManager
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
import base64

# Imports opcionales para reconocimiento de imágenes
try:
    import numpy as np
    import cv2
    from ..reconocimiento_mobilenet import ReconocimientoMobileNet, validar_calidad_imagen, calcular_hash_imagen
    CV2_DISPONIBLE = True
except ImportError:
    CV2_DISPONIBLE = False
    np = None
    cv2 = None
    ReconocimientoMobileNet = None
    validar_calidad_imagen = None
    calcular_hash_imagen = None

db = DatabaseManager()
logger = logging.getLogger(__name__)

# Inicializar sistema de reconocimiento
sistema_reconocimiento = None

def obtener_sistema():
    """Obtiene o inicializa el sistema de reconocimiento"""
    global sistema_reconocimiento
    if not CV2_DISPONIBLE:
        return None
    if sistema_reconocimiento is None:
        sistema_reconocimiento = ReconocimientoMobileNet()
        # Intentar cargar modelo existente
        try:
            sistema_reconocimiento.cargar_modelo()
            logger.info("✅ Modelo MobileNet cargado exitosamente")
        except FileNotFoundError:
            logger.info("⚠️ No hay modelo entrenado. Esperando primer entrenamiento.")
    return sistema_reconocimiento


@reconocimiento_bp.route('/estadisticas', methods=['GET'])
def estadisticas_reconocimiento():
    """
    GET /api/reconocimiento/estadisticas
    Obtiene estadísticas del sistema de reconocimiento usando tablas existentes
    """
    try:
        # Estadísticas de equipos con imágenes para entrenar
        query_equipos = """
            SELECT 
                COUNT(DISTINCT e.id) as equipos_con_imagen,
                COUNT(DISTINCT ie.id_equipo) as equipos_entrenables,
                COUNT(ie.id) as total_imagenes_entrenamiento
            FROM equipos e
            LEFT JOIN imagenes_entrenamiento ie ON e.id = ie.id_equipo
            WHERE e.imagen_url IS NOT NULL
        """
        stats_equipos = db.obtener_uno(query_equipos) or {}
        
        # Estadísticas de reconocimientos
        query_reconocimientos = """
            SELECT 
                COUNT(*) as total_reconocimientos,
                SUM(CASE WHEN confianza_deteccion >= 0.85 THEN 1 ELSE 0 END) as exitosos,
                AVG(confianza_deteccion) as confianza_promedio
            FROM reconocimientos_imagen
        """
        stats_reconocimientos = db.obtener_uno(query_reconocimientos) or {}
        
        # Info del modelo activo
        query_modelo = """
            SELECT nombre, version, precision_modelo, estado, fecha_entrenamiento
            FROM modelos_ia
            WHERE tipo = 'reconocimiento_imagenes' AND estado = 'activo'
            ORDER BY id DESC LIMIT 1
        """
        modelo_activo = db.obtener_uno(query_modelo)
        
        # Obtener estadísticas del sistema MobileNet (si está disponible)
        sistema = obtener_sistema()
        stats_modelo = sistema.obtener_estadisticas() if sistema else {'disponible': False, 'mensaje': 'OpenCV no instalado'}
        
        estadisticas = {
            'equipos': {
                'con_imagen': stats_equipos.get('equipos_con_imagen', 0),
                'entrenables': stats_equipos.get('equipos_entrenables', 0),
                'imagenes_entrenamiento': stats_equipos.get('total_imagenes_entrenamiento', 0)
            },
            'reconocimientos': {
                'total': stats_reconocimientos.get('total_reconocimientos', 0),
                'exitosos': stats_reconocimientos.get('exitosos', 0),
                'confianza_promedio': float(stats_reconocimientos.get('confianza_promedio', 0) or 0)
            },
            'modelo': modelo_activo if modelo_activo else {'estado': 'sin_entrenar'},
            'sistema': stats_modelo,
            'objetivo_mga': {
                'precision_objetivo': '>85%',
                'equipos_meta': 1500,
                'tiempo_identificacion': '<3 segundos'
            }
        }
        
        return jsonify({'success': True, 'estadisticas': estadisticas}), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/equipos-entrenados', methods=['GET'])
def listar_equipos_entrenados():
    """
    GET /api/reconocimiento/equipos-entrenados
    Lista equipos con imágenes de entrenamiento (usando tabla equipos + imagenes_entrenamiento)
    """
    try:
        query = """
            SELECT 
                e.id,
                e.codigo_interno as codigo_equipo,
                e.nombre as nombre_objeto,
                c.nombre as categoria,
                e.marca,
                e.modelo,
                e.imagen_url,
                COUNT(ie.id) as cantidad_imagenes,
                MAX(ie.fecha_captura) as ultima_imagen,
                CASE 
                    WHEN COUNT(ie.id) >= 5 THEN 'listo'
                    WHEN COUNT(ie.id) > 0 THEN 'parcial'
                    ELSE 'sin_imagenes'
                END as estado_entrenamiento
            FROM equipos e
            LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
            LEFT JOIN imagenes_entrenamiento ie ON e.id = ie.id_equipo
            WHERE e.imagen_url IS NOT NULL OR ie.id IS NOT NULL
            GROUP BY e.id
            ORDER BY cantidad_imagenes DESC, e.nombre ASC
        """
        
        equipos = db.ejecutar_query(query)
        
        # Convertir fechas a string
        for eq in equipos:
            if eq.get('ultima_imagen'):
                eq['ultima_imagen'] = eq['ultima_imagen'].isoformat()
        
        return jsonify({
            'success': True,
            'total': len(equipos),
            'equipos': equipos,
            'mensaje': 'Equipos con mínimo 5 imágenes están listos para entrenar'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error listando equipos entrenados: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/agregar-imagenes/<int:equipo_id>', methods=['POST'])
def agregar_imagenes_entrenamiento(equipo_id):
    """
    POST /api/reconocimiento/agregar-imagenes/{equipo_id}
    Agrega imágenes de entrenamiento a un equipo existente
    
    Body:
    {
        "imagenes": [base64_img1, base64_img2, ...],
        "angulos": ["frontal", "lateral_derecha", "superior", ...]
    }
    """
    if not CV2_DISPONIBLE:
        return jsonify({'success': False, 'error': 'Reconocimiento no disponible. OpenCV no instalado.'}), 503
    
    try:
        data = request.get_json()
        
        if 'imagenes' not in data or not data['imagenes']:
            return jsonify({'success': False, 'error': 'Se requieren imágenes'}), 400
        
        # Verificar que el equipo existe
        equipo = db.obtener_uno("SELECT id, codigo_interno, nombre FROM equipos WHERE id = %s", (equipo_id,))
        if not equipo:
            return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
        
        codigo_equipo = equipo['codigo_interno']
        imagenes_base64 = data['imagenes']
        angulos = data.get('angulos', [])
        
        # Crear directorio para las imágenes
        directorio_equipo = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'entrenamiento', codigo_equipo)
        os.makedirs(directorio_equipo, exist_ok=True)
        
        imagenes_guardadas = []
        
        for idx, img_base64 in enumerate(imagenes_base64):
            try:
                # Decodificar base64
                img_data = base64.b64decode(img_base64.split(',')[1] if ',' in img_base64 else img_base64)
                
                # Guardar imagen
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                angulo = angulos[idx] if idx < len(angulos) else 'perspectiva'
                nombre_archivo = f"{codigo_equipo}_{angulo}_{timestamp}_{idx}.jpg"
                ruta_imagen = os.path.join(directorio_equipo, nombre_archivo)
                ruta_web = f"/uploads/entrenamiento/{codigo_equipo}/{nombre_archivo}"
                
                with open(ruta_imagen, 'wb') as f:
                    f.write(img_data)
                
                # Validar calidad
                validacion = validar_calidad_imagen(ruta_imagen)
                
                if validacion['valida']:
                    # Obtener info del archivo
                    tamano = os.path.getsize(ruta_imagen)
                    img = cv2.imread(ruta_imagen)
                    h, w = img.shape[:2] if img is not None else (0, 0)
                    hash_img = calcular_hash_imagen(ruta_imagen)
                    
                    # Insertar en imagenes_entrenamiento
                    query_img = """
                        INSERT INTO imagenes_entrenamiento (
                            id_equipo, ruta_imagen, angulo_captura,
                            resolucion, formato, tamano_bytes, hash_imagen,
                            calidad_imagen, estado
                        ) VALUES (%s, %s, %s, %s, 'jpg', %s, %s, %s, 'pendiente')
                    """
                    db.ejecutar_comando(query_img, (
                        equipo_id, ruta_web, angulo, f'{w}x{h}',
                        tamano, hash_img, validacion['calidad']
                    ))
                    
                    imagenes_guardadas.append({
                        'ruta': ruta_web,
                        'angulo': angulo,
                        'calidad': validacion['calidad']
                    })
                else:
                    logger.warning(f"⚠️ Imagen {idx} rechazada: {validacion.get('razon', 'Baja calidad')}")
                    os.remove(ruta_imagen)
                    
            except Exception as e:
                logger.error(f"❌ Error procesando imagen {idx}: {e}")
                continue
        
        # Contar total de imágenes del equipo
        total = db.obtener_uno(
            "SELECT COUNT(*) as total FROM imagenes_entrenamiento WHERE id_equipo = %s",
            (equipo_id,)
        )
        
        logger.info(f"✅ {len(imagenes_guardadas)} imágenes agregadas para equipo {codigo_equipo}")
        
        return jsonify({
            'success': True,
            'mensaje': f'{len(imagenes_guardadas)} imágenes agregadas exitosamente',
            'imagenes_guardadas': len(imagenes_guardadas),
            'total_imagenes_equipo': total['total'] if total else len(imagenes_guardadas),
            'listo_para_entrenar': (total['total'] if total else 0) >= 5
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error agregando imágenes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/registrar-equipo', methods=['POST'])
def registrar_equipo():
    """
    POST /api/reconocimiento/registrar-equipo
    Registra un nuevo equipo con sus imágenes para entrenamiento
    Usa tabla equipos existente + imagenes_entrenamiento
    
    Body:
    {
        "id_equipo": 123,  // ID de equipo existente (opcional)
        "codigo_equipo": "EQP-LAP-001",  // O código para buscar
        "imagenes": [base64_img1, base64_img2, ...],
        "angulos": ["frontal", "lateral_derecha", "superior", ...]
    }
    """
    if not CV2_DISPONIBLE:
        return jsonify({'success': False, 'error': 'Reconocimiento no disponible. OpenCV no instalado.'}), 503
    
    try:
        data = request.get_json()
        
        # Buscar equipo existente por ID o código
        equipo_id = data.get('id_equipo')
        codigo_equipo = data.get('codigo_equipo')
        
        if equipo_id:
            equipo = db.obtener_uno("SELECT id, codigo_interno, nombre FROM equipos WHERE id = %s", (equipo_id,))
        elif codigo_equipo:
            equipo = db.obtener_uno("SELECT id, codigo_interno, nombre FROM equipos WHERE codigo_interno = %s", (codigo_equipo,))
        else:
            return jsonify({'success': False, 'error': 'Se requiere id_equipo o codigo_equipo'}), 400
        
        if not equipo:
            return jsonify({'success': False, 'error': 'Equipo no encontrado. Primero registre el equipo en el módulo de Equipos.'}), 404
        
        equipo_id = equipo['id']
        codigo_equipo = equipo['codigo_interno']
        
        imagenes_base64 = data.get('imagenes', [])
        angulos = data.get('angulos', [])
        
        # Validar cantidad mínima de imágenes (5 según documento MGA)
        if len(imagenes_base64) < 5:
            return jsonify({
                'success': False,
                'error': 'Se requieren al menos 5 imágenes para entrenamiento (diferentes ángulos: frontal, laterales, superior, etc.)'
            }), 400
        
        # Crear directorio para las imágenes
        directorio_equipo = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'entrenamiento', codigo_equipo)
        os.makedirs(directorio_equipo, exist_ok=True)
        
        imagenes_guardadas = []
        
        for idx, img_base64 in enumerate(imagenes_base64):
            try:
                img_data = base64.b64decode(img_base64.split(',')[1] if ',' in img_base64 else img_base64)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                angulo = angulos[idx] if idx < len(angulos) else 'perspectiva'
                nombre_archivo = f"{codigo_equipo}_{angulo}_{timestamp}_{idx}.jpg"
                ruta_imagen = os.path.join(directorio_equipo, nombre_archivo)
                ruta_web = f"/uploads/entrenamiento/{codigo_equipo}/{nombre_archivo}"
                
                with open(ruta_imagen, 'wb') as f:
                    f.write(img_data)
                
                validacion = validar_calidad_imagen(ruta_imagen)
                
                if validacion['valida']:
                    tamano = os.path.getsize(ruta_imagen)
                    img = cv2.imread(ruta_imagen)
                    h, w = img.shape[:2] if img is not None else (0, 0)
                    hash_img = calcular_hash_imagen(ruta_imagen)
                    
                    db.ejecutar_comando("""
                        INSERT INTO imagenes_entrenamiento (
                            id_equipo, ruta_imagen, angulo_captura,
                            resolucion, formato, tamano_bytes, hash_imagen,
                            calidad_imagen, estado
                        ) VALUES (%s, %s, %s, %s, 'jpg', %s, %s, %s, 'pendiente')
                    """, (equipo_id, ruta_web, angulo, f'{w}x{h}', tamano, hash_img, validacion['calidad']))
                    
                    imagenes_guardadas.append({'ruta': ruta_web, 'angulo': angulo})
                else:
                    logger.warning(f"⚠️ Imagen {idx} rechazada: {validacion.get('razon')}")
                    os.remove(ruta_imagen)
                    
            except Exception as e:
                logger.error(f"❌ Error procesando imagen {idx}: {e}")
                continue
        
        if len(imagenes_guardadas) < 5:
            return jsonify({
                'success': False,
                'error': f'Solo {len(imagenes_guardadas)} imágenes válidas. Se requieren al menos 5.'
            }), 400
        
        logger.info(f"✅ Equipo {codigo_equipo} registrado con {len(imagenes_guardadas)} imágenes para entrenamiento")
        
        return jsonify({
            'success': True,
            'mensaje': 'Equipo registrado exitosamente para entrenamiento',
            'equipo_id': equipo_id,
            'codigo_equipo': codigo_equipo,
            'nombre': equipo['nombre'],
            'imagenes_guardadas': len(imagenes_guardadas),
            'proximo_paso': 'Entrenar el modelo desde la sección IA Visual'
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error registrando equipo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/entrenar', methods=['POST'])
def entrenar_modelo():
    """
    POST /api/reconocimiento/entrenar
    Entrena el modelo MobileNet con equipos que tienen imágenes de entrenamiento
    Usa tablas: equipos + imagenes_entrenamiento + modelos_ia
    
    Body (opcional):
    {
        "equipos_ids": [1, 2, 3],  // IDs de equipos específicos (vacío = todos los listos)
        "epochs": 10,
        "validation_split": 0.2
    }
    """
    if not CV2_DISPONIBLE:
        return jsonify({'success': False, 'error': 'Reconocimiento no disponible. OpenCV no instalado.'}), 503
    
    try:
        data = request.get_json() or {}
        
        equipos_ids = data.get('equipos_ids', [])
        epochs = data.get('epochs', 10)
        validation_split = data.get('validation_split', 0.2)
        
        # Obtener equipos con mínimo 5 imágenes de entrenamiento
        if equipos_ids:
            placeholders = ','.join(['%s'] * len(equipos_ids))
            query = f"""
                SELECT 
                    e.id,
                    e.codigo_interno as codigo_equipo,
                    e.nombre as nombre_objeto,
                    c.nombre as categoria,
                    GROUP_CONCAT(ie.ruta_imagen) as rutas_imagenes,
                    COUNT(ie.id) as cantidad_imagenes
                FROM equipos e
                LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
                INNER JOIN imagenes_entrenamiento ie ON e.id = ie.id_equipo
                WHERE e.id IN ({placeholders})
                GROUP BY e.id
                HAVING COUNT(ie.id) >= 5
            """
            equipos = db.ejecutar_query(query, tuple(equipos_ids))
        else:
            query = """
                SELECT 
                    e.id,
                    e.codigo_interno as codigo_equipo,
                    e.nombre as nombre_objeto,
                    c.nombre as categoria,
                    GROUP_CONCAT(ie.ruta_imagen) as rutas_imagenes,
                    COUNT(ie.id) as cantidad_imagenes
                FROM equipos e
                LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
                INNER JOIN imagenes_entrenamiento ie ON e.id = ie.id_equipo
                GROUP BY e.id
                HAVING COUNT(ie.id) >= 5
            """
            equipos = db.ejecutar_query(query)
        
        if not equipos:
            return jsonify({
                'success': False,
                'error': 'No hay equipos con suficientes imágenes (mínimo 5) para entrenamiento'
            }), 400
        
        logger.info(f"🎓 Iniciando entrenamiento con {len(equipos)} equipos...")
        
        # Preparar datos para el modelo
        equipos_para_entrenar = []
        for eq in equipos:
            rutas = eq['rutas_imagenes'].split(',') if eq['rutas_imagenes'] else []
            # Convertir rutas web a rutas de archivo
            rutas_archivo = []
            for ruta in rutas:
                if ruta.startswith('/uploads/'):
                    ruta_completa = os.path.join(os.path.dirname(__file__), '..', '..', ruta.lstrip('/'))
                else:
                    ruta_completa = ruta
                if os.path.exists(ruta_completa):
                    rutas_archivo.append(ruta_completa)
            
            equipos_para_entrenar.append({
                'id': eq['id'],
                'codigo_equipo': eq['codigo_equipo'],
                'nombre_objeto': eq['nombre_objeto'],
                'categoria_entrenamiento': eq.get('categoria') or 'General',
                'rutas_imagenes': json.dumps(rutas_archivo)
            })
        
        # Entrenar modelo
        sistema = obtener_sistema()
        sistema.EPOCHS = epochs
        
        try:
            metricas = sistema.entrenar_modelo(equipos_para_entrenar, validation_split)
            
            # Actualizar estado de imágenes a 'entrenado'
            for eq in equipos:
                db.ejecutar_comando(
                    "UPDATE imagenes_entrenamiento SET estado = 'entrenado' WHERE id_equipo = %s",
                    (eq['id'],)
                )
            
            # Registrar/actualizar modelo en modelos_ia
            modelo_existente = db.obtener_uno(
                "SELECT id FROM modelos_ia WHERE tipo = 'reconocimiento_imagenes' AND nombre = 'MobileNetV2'"
            )
            
            if modelo_existente:
                db.ejecutar_comando("""
                    UPDATE modelos_ia 
                    SET precision_modelo = %s,
                        fecha_entrenamiento = CURDATE(),
                        estado = 'activo',
                        parametros_modelo = %s
                    WHERE id = %s
                """, (
                    metricas['val_accuracy'],
                    json.dumps({
                        'epochs': epochs,
                        'clases': metricas['num_clases'],
                        'imagenes': metricas['total_imagenes']
                    }),
                    modelo_existente['id']
                ))
            else:
                db.ejecutar_comando("""
                    INSERT INTO modelos_ia (nombre, tipo, version, ruta_archivo, precision_modelo, 
                                           fecha_entrenamiento, estado, parametros_modelo)
                    VALUES ('MobileNetV2', 'reconocimiento_imagenes', '2.0', %s, %s, CURDATE(), 'activo', %s)
                """, (
                    'models/reconocimiento/mobilenet_equipos.h5',
                    metricas['val_accuracy'],
                    json.dumps({
                        'epochs': epochs,
                        'clases': metricas['num_clases'],
                        'imagenes': metricas['total_imagenes']
                    })
                ))
            
            logger.info(f"✅ Entrenamiento completado exitosamente")
            
            return jsonify({
                'success': True,
                'mensaje': 'Modelo entrenado exitosamente',
                'metricas': {
                    'precision_entrenamiento': f"{metricas['train_accuracy']*100:.2f}%",
                    'precision_validacion': f"{metricas['val_accuracy']*100:.2f}%",
                    'clases_entrenadas': metricas['num_clases'],
                    'total_imagenes': metricas['total_imagenes'],
                    'objetivo_mga_alcanzado': metricas['objetivo_alcanzado']
                }
            }), 200
            
        except Exception as e_train:
            # Marcar imágenes como error
            for eq in equipos:
                db.ejecutar_comando(
                    "UPDATE imagenes_entrenamiento SET estado = 'error' WHERE id_equipo = %s",
                    (eq['id'],)
                )
            raise e_train
        
    except Exception as e:
        logger.error(f"❌ Error entrenando modelo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/identificar', methods=['POST'])
def identificar_equipo():
    """
    POST /api/reconocimiento/identificar
    Identifica un equipo usando el modelo MobileNet entrenado
    Guarda resultado en reconocimientos_imagen
    
    Body:
    {
        "imagen": "base64_encoded_image",
        "top_n": 5
    }
    """
    if not CV2_DISPONIBLE:
        return jsonify({'success': False, 'error': 'Reconocimiento no disponible. OpenCV no instalado.'}), 503
    
    import time
    
    try:
        inicio = time.time()
        data = request.get_json()
        
        if 'imagen' not in data:
            return jsonify({'success': False, 'error': 'Imagen requerida'}), 400
        
        top_n = data.get('top_n', 5)
        usuario_id = session.get('user_id')
        umbral_confianza = 0.85  # 85% según objetivo MGA
        
        # Decodificar imagen base64
        img_base64 = data['imagen']
        img_data = base64.b64decode(img_base64.split(',')[1] if ',' in img_base64 else img_base64)
        
        # Convertir a array numpy (OpenCV)
        nparr = np.frombuffer(img_data, np.uint8)
        imagen_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if imagen_cv2 is None:
            return jsonify({'success': False, 'error': 'Imagen no válida'}), 400
        
        # Identificar con el modelo
        sistema = obtener_sistema()
        
        if not sistema.modelo_cargado:
            return jsonify({
                'success': False,
                'error': 'No hay modelo entrenado. Primero entrene el modelo con imágenes de equipos.',
                'accion_requerida': 'entrenar'
            }), 400
        
        resultados, tiempo_ms = sistema.identificar_equipo_cv2(imagen_cv2, top_n)
        
        # Obtener modelo activo para registrar
        modelo_activo = db.obtener_uno(
            "SELECT id FROM modelos_ia WHERE tipo = 'reconocimiento_imagenes' AND estado = 'activo' LIMIT 1"
        )
        
        # Registrar en reconocimientos_imagen y obtener detalles completos
        if resultados:
            mejor = resultados[0]
            
            # Buscar detalles completos del equipo detectado
            equipo_detectado = db.obtener_uno("""
                SELECT 
                    e.id,
                    e.codigo_interno,
                    e.codigo_qr,
                    e.nombre,
                    e.marca,
                    e.modelo,
                    e.numero_serie,
                    e.descripcion,
                    e.especificaciones_tecnicas,
                    e.valor_adquisicion,
                    e.fecha_adquisicion,
                    e.proveedor,
                    e.garantia_meses,
                    e.vida_util_anos,
                    e.imagen_url,
                    e.estado,
                    e.estado_fisico,
                    e.ubicacion_especifica,
                    e.observaciones,
                    e.fecha_registro,
                    c.nombre as categoria,
                    l.nombre as laboratorio,
                    l.ubicacion as laboratorio_ubicacion
                FROM equipos e
                LEFT JOIN categorias_equipos c ON e.id_categoria = c.id
                LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
                WHERE e.codigo_interno = %s
            """, (mejor['codigo_equipo'],))
            
            # Agregar detalles completos al mejor resultado
            if equipo_detectado:
                mejor['detalles_equipo'] = {
                    'id': equipo_detectado['id'],
                    'codigo_interno': equipo_detectado['codigo_interno'],
                    'codigo_qr': equipo_detectado.get('codigo_qr'),
                    'nombre': equipo_detectado['nombre'],
                    'marca': equipo_detectado.get('marca'),
                    'modelo': equipo_detectado.get('modelo'),
                    'numero_serie': equipo_detectado.get('numero_serie'),
                    'descripcion': equipo_detectado.get('descripcion'),
                    'especificaciones_tecnicas': equipo_detectado.get('especificaciones_tecnicas'),
                    'valor_adquisicion': float(equipo_detectado['valor_adquisicion']) if equipo_detectado.get('valor_adquisicion') else None,
                    'fecha_adquisicion': str(equipo_detectado['fecha_adquisicion']) if equipo_detectado.get('fecha_adquisicion') else None,
                    'proveedor': equipo_detectado.get('proveedor'),
                    'garantia_meses': equipo_detectado.get('garantia_meses'),
                    'vida_util_anos': equipo_detectado.get('vida_util_anos'),
                    'imagen_url': equipo_detectado.get('imagen_url'),
                    'estado': equipo_detectado.get('estado'),
                    'estado_fisico': equipo_detectado.get('estado_fisico'),
                    'ubicacion_especifica': equipo_detectado.get('ubicacion_especifica'),
                    'observaciones': equipo_detectado.get('observaciones'),
                    'fecha_registro': str(equipo_detectado['fecha_registro']) if equipo_detectado.get('fecha_registro') else None,
                    'categoria': equipo_detectado.get('categoria'),
                    'laboratorio': equipo_detectado.get('laboratorio'),
                    'laboratorio_ubicacion': equipo_detectado.get('laboratorio_ubicacion')
                }
            
            try:
                db.ejecutar_comando("""
                    INSERT INTO reconocimientos_imagen (
                        id_equipo_detectado, imagen_original_url, confianza_deteccion,
                        coordenadas_deteccion, id_modelo_usado, procesado_por_usuario,
                        validacion_manual
                    ) VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
                """, (
                    equipo_detectado['id'] if equipo_detectado and mejor['exitoso'] else None,
                    f"reconocimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                    mejor['confianza'],
                    json.dumps([{
                        'codigo': r['codigo_equipo'],
                        'nombre': r['nombre_objeto'],
                        'confianza': r['confianza_porcentaje']
                    } for r in resultados]),
                    modelo_activo['id'] if modelo_activo else None,
                    usuario_id
                ))
            except Exception as e:
                logger.warning(f"No se pudo registrar reconocimiento: {e}")
        
        tiempo_total = (time.time() - inicio) * 1000
        
        logger.info(f"🔍 Identificación: {resultados[0]['nombre_objeto'] if resultados else 'Sin resultados'} ({tiempo_total:.0f}ms)")
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'tiempo_procesamiento_ms': round(tiempo_total, 2),
            'mejor_match': resultados[0] if resultados else None,
            'umbral_confianza': umbral_confianza
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error identificando equipo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/validar-imagen', methods=['POST'])
def validar_imagen():
    """
    POST /api/reconocimiento/validar-imagen
    Valida la calidad de una imagen antes de guardarla
    
    Body:
    {
        "imagen": "base64_encoded_image"
    }
    """
    if not CV2_DISPONIBLE:
        return jsonify({'success': False, 'error': 'Reconocimiento no disponible. OpenCV no instalado.'}), 503
    
    try:
        data = request.get_json()
        
        if 'imagen' not in data:
            return jsonify({'success': False, 'error': 'Imagen requerida'}), 400
        
        # Decodificar y guardar temporalmente
        img_base64 = data['imagen']
        img_data = base64.b64decode(img_base64.split(',')[1] if ',' in img_base64 else img_base64)
        
        temp_path = 'uploads/temp_validation.jpg'
        os.makedirs('uploads', exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(img_data)
        
        # Validar calidad
        validacion = validar_calidad_imagen(temp_path)
        
        # Eliminar temporal
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'validacion': validacion
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error validando imagen: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@reconocimiento_bp.route('/modelo/info', methods=['GET'])
def info_modelo():
    """
    GET /api/reconocimiento/modelo/info
    Obtiene información del modelo desde tabla modelos_ia
    """
    try:
        query = """
            SELECT id, nombre, tipo, version, ruta_archivo, precision_modelo,
                   fecha_entrenamiento, estado, parametros_modelo
            FROM modelos_ia
            WHERE tipo = 'reconocimiento_imagenes' AND estado = 'activo'
            ORDER BY id DESC
            LIMIT 1
        """
        
        info = db.obtener_uno(query)
        
        if not info:
            # Retornar info de que no hay modelo
            return jsonify({
                'success': True,
                'modelo': {
                    'estado': 'sin_entrenar',
                    'mensaje': 'No hay modelo entrenado. Agregue imágenes de entrenamiento y entrene el modelo.'
                }
            }), 200
        
        # Convertir fecha a string
        if info.get('fecha_entrenamiento'):
            info['fecha_entrenamiento'] = info['fecha_entrenamiento'].isoformat()
        
        # Parsear parámetros JSON
        if info.get('parametros_modelo'):
            try:
                info['parametros_modelo'] = json.loads(info['parametros_modelo'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'modelo': info
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo info del modelo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Endpoint de prueba
@reconocimiento_bp.route('/test', methods=['GET'])
def test_reconocimiento():
    """Endpoint de prueba para verificar que la API está funcionando"""
    return jsonify({
        'success': True,
        'mensaje': 'API de Reconocimiento IA funcionando',
        'version': '1.0',
        'objetivo_mga': 'Reconocimiento de equipos con precisión >85%'
    }), 200
