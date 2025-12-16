# -*- coding: utf-8 -*-
"""
API de Reconocimiento Facial
Centro Minero de Sogamoso - SENA

Campos de tabla usuarios según schema.sql:
- id, documento, nombres, apellidos, email, telefono, id_rol, 
- password_hash, fecha_registro, ultimo_acceso, estado
- rostro_data (LONGBLOB) - agregado para reconocimiento facial
"""

from flask import request, jsonify, session
from .blueprints import facial_bp
from ..utils.database import DatabaseManager
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64
from datetime import datetime
import os

# Instancia de base de datos
db = DatabaseManager()

# Directorio para guardar imágenes de rostros
ROSTROS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'rostros')
os.makedirs(ROSTROS_DIR, exist_ok=True)

# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def base64_to_image(base64_string):
    """
    Convierte imagen base64 a numpy array
    
    Args:
        base64_string: Imagen en formato base64
        
    Returns:
        numpy array de la imagen
    """
    try:
        # Eliminar prefijo data:image si existe
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]
        
        # Decodificar base64
        img_data = base64.b64decode(base64_string)
        
        # Convertir a numpy array
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
    except Exception as e:
        print(f"Error convirtiendo base64 a imagen: {e}")
        return None

def detectar_rostro(imagen):
    """
    Detecta rostro en imagen usando Haar Cascade
    
    Args:
        imagen: numpy array de la imagen
        
    Returns:
        Rostro extraído y redimensionado, o None
    """
    try:
        cascade_cara = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        rostros = cascade_cara.detectMultiScale(
            gris,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(rostros) == 0:
            return None
        
        # Tomar el rostro más grande
        rostro_principal = max(rostros, key=lambda r: r[2] * r[3])
        x, y, w, h = rostro_principal
        
        # Extraer y redimensionar
        rostro = imagen[y:y+h, x:x+w]
        rostro_redimensionado = cv2.resize(rostro, (200, 200))
        
        return rostro_redimensionado
    except Exception as e:
        print(f"Error detectando rostro: {e}")
        return None

def calcular_similitud(rostro1, rostro2):
    """
    Calcula similitud entre dos rostros
    
    Args:
        rostro1: Primera imagen de rostro
        rostro2: Segunda imagen de rostro
        
    Returns:
        Valor de similitud entre 0 y 1
    """
    try:
        # Redimensionar al mismo tamaño
        rostro1_resize = cv2.resize(rostro1, (200, 200))
        rostro2_resize = cv2.resize(rostro2, (200, 200))
        
        # Convertir a escala de grises
        gris1 = cv2.cvtColor(rostro1_resize, cv2.COLOR_BGR2GRAY)
        gris2 = cv2.cvtColor(rostro2_resize, cv2.COLOR_BGR2GRAY)
        
        # Normalizar
        gris1 = cv2.equalizeHist(gris1)
        gris2 = cv2.equalizeHist(gris2)
        
        # Calcular diferencia
        diferencia = cv2.absdiff(gris1, gris2)
        
        # Calcular similitud (inverso de la diferencia)
        similitud = 1.0 - (np.mean(diferencia) / 255.0)
        
        return similitud
    except Exception as e:
        print(f"Error calculando similitud: {e}")
        return 0.0

# =====================================================================
# ENDPOINTS API
# =====================================================================

@facial_bp.route('/login', methods=['POST'])
def login_facial():
    """
    POST /api/facial/login - Login por reconocimiento facial
    
    Body: { "image": "base64_image_data" }
    Returns: { "success": true, "user": {...} } o error
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere imagen en formato base64'
            }), 400
        
        # Convertir imagen base64 a numpy array
        imagen = base64_to_image(data['image'])
        if imagen is None:
            return jsonify({
                'success': False,
                'error': 'No se pudo procesar la imagen'
            }), 400
        
        # Detectar rostro en la imagen
        rostro_actual = detectar_rostro(imagen)
        if rostro_actual is None:
            return jsonify({
                'success': False,
                'error': 'No se detectó ningún rostro en la imagen'
            }), 400
        
        # Obtener todos los usuarios con rostro registrado
        if not db.conectar():
            return jsonify({
                'success': False,
                'error': 'Error conectando a la base de datos'
            }), 500
        
        # Usar campos correctos del schema.sql
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.email, 
                u.id_rol, u.rostro_data, r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE u.rostro_data IS NOT NULL AND u.estado = 'activo'
        """
        usuarios = db.ejecutar_query(query)
        
        if not usuarios:
            return jsonify({
                'success': False,
                'error': 'No hay usuarios registrados con reconocimiento facial'
            }), 404
        
        # Comparar con cada usuario
        mejor_coincidencia = None
        mejor_similitud = 0
        umbral_similitud = 0.65  # 65% de similitud mínima
        
        for usuario in usuarios:
            if not usuario.get('rostro_data'):
                continue
            # Convertir bytes a imagen
            rostro_db = cv2.imdecode(
                np.frombuffer(usuario['rostro_data'], np.uint8),
                cv2.IMREAD_COLOR
            )
            
            if rostro_db is None:
                continue
            
            # Calcular similitud
            similitud = calcular_similitud(rostro_actual, rostro_db)
            
            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_coincidencia = usuario
        
        # Verificar si supera el umbral
        if mejor_similitud >= umbral_similitud and mejor_coincidencia:
            # Usuario identificado exitosamente
            nombre_completo = f"{mejor_coincidencia['nombres']} {mejor_coincidencia['apellidos']}"
            
            # Crear sesión
            session['user_id'] = mejor_coincidencia['documento']
            session['user_name'] = nombre_completo
            session['user_type'] = mejor_coincidencia.get('nombre_rol', 'Usuario')
            session['user_level'] = mejor_coincidencia.get('id_rol', 1)
            session['login_method'] = 'facial'
            
            # Actualizar último acceso
            update_acceso = "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s"
            db.ejecutar_comando(update_acceso, (mejor_coincidencia['id'],))
            
            return jsonify({
                'success': True,
                'user': {
                    'id': mejor_coincidencia['id'],
                    'documento': mejor_coincidencia['documento'],
                    'nombre': nombre_completo,
                    'rol': mejor_coincidencia.get('nombre_rol', 'Usuario'),
                    'email': mejor_coincidencia.get('email')
                },
                'similitud': round(mejor_similitud * 100, 2),
                'message': f'Bienvenido {nombre_completo}'
            }), 200
        else:
            # No se pudo identificar al usuario
            return jsonify({
                'success': False,
                'error': 'No se pudo identificar al usuario',
                'similitud_maxima': round(mejor_similitud * 100, 2),
                'umbral_requerido': round(umbral_similitud * 100, 2)
            }), 401
            
    except Exception as e:
        print(f"Error en login facial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error procesando solicitud: {str(e)}'
        }), 500
    finally:
        db.desconectar()

@facial_bp.route('/register', methods=['POST'])
def registrar_rostro():
    """
    POST /api/facial/register - Registrar rostro de usuario
    
    Body: { "user_id": "documento_usuario", "image": "base64_image_data" }
    Returns: { "success": true, "message": "..." } o error
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere user_id e image'
            }), 400
        
        user_id = data['user_id']
        
        # Verificar que el usuario existe
        if not db.conectar():
            return jsonify({
                'success': False,
                'error': 'Error conectando a la base de datos'
            }), 500
        
        # Buscar por documento (user_id del frontend es el documento)
        query_user = """
            SELECT id, documento, nombres, apellidos 
            FROM usuarios 
            WHERE documento = %s AND estado = 'activo'
        """
        usuario = db.obtener_uno(query_user, (user_id,))
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': f'Usuario con documento {user_id} no encontrado o inactivo'
            }), 404
        
        nombre_completo = f"{usuario['nombres']} {usuario['apellidos']}"
        
        # Convertir imagen base64 a numpy array
        imagen = base64_to_image(data['image'])
        if imagen is None:
            return jsonify({
                'success': False,
                'error': 'No se pudo procesar la imagen'
            }), 400
        
        # Detectar y extraer rostro
        rostro = detectar_rostro(imagen)
        if rostro is None:
            print(f"[FACIAL] No se detectó rostro para usuario: {user_id}")
            return jsonify({
                'success': False,
                'error': 'No se detectó ningún rostro en la imagen. Asegúrate de estar bien iluminado y mirando a la cámara.'
            }), 400
        
        print(f"[FACIAL] Rostro detectado para usuario: {user_id}, shape: {rostro.shape}")
        
        # Convertir imagen a bytes para guardar en BD
        _, buffer = cv2.imencode('.jpg', rostro)
        imagen_bytes = buffer.tobytes()
        
        print(f"[FACIAL] Imagen convertida a bytes, tamaño: {len(imagen_bytes)} bytes")
        
        # También guardar imagen en archivo para respaldo
        try:
            ruta_imagen = os.path.join(ROSTROS_DIR, f"{user_id}.jpg")
            cv2.imwrite(ruta_imagen, rostro)
            print(f"[FACIAL] Imagen guardada en: {ruta_imagen}")
        except Exception as e:
            print(f"[FACIAL] No se pudo guardar imagen en archivo: {e}")
        
        # Guardar en base de datos
        query_update = "UPDATE usuarios SET rostro_data = %s WHERE documento = %s"
        print(f"[FACIAL] Ejecutando UPDATE para documento: {user_id}")
        resultado_update = db.ejecutar_comando(query_update, (imagen_bytes, user_id))
        
        print(f"[FACIAL] Resultado del UPDATE: {resultado_update}")
        
        if not resultado_update:
            print(f"[FACIAL] ERROR: UPDATE falló para usuario: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Error al guardar el rostro en la base de datos. Verifica los permisos.'
            }), 500
        
        print(f"[FACIAL] Rostro guardado exitosamente para usuario: {user_id}")
        
        # Verificar que se guardó correctamente
        query_verify = "SELECT LENGTH(rostro_data) as size FROM usuarios WHERE documento = %s"
        verify_result = db.obtener_uno(query_verify, (user_id,))
        size = verify_result['size'] if verify_result and verify_result.get('size') else 0
        print(f"[FACIAL] Verificación: rostro_data tiene {size} bytes")
        
        # Desconectar DESPUÉS de todo
        db.desconectar()
        
        return jsonify({
            'success': True,
            'message': f'Rostro registrado exitosamente para {nombre_completo}',
            'user_id': user_id,
            'nombre': nombre_completo
        }), 200
        
    except Exception as e:
        print(f"[FACIAL] ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        
        # Desconectar en caso de error
        try:
            db.desconectar()
        except:
            pass
            
        return jsonify({
            'success': False,
            'error': f'Error procesando solicitud: {str(e)}'
        }), 500

@facial_bp.route('/check/<user_id>', methods=['GET'])
def verificar_rostro_registrado(user_id):
    """
    GET /api/facial/check/<user_id> - Verificar si usuario tiene rostro registrado
    user_id es el documento del usuario
    
    Returns: { "registered": true/false, "user": {...} }
    """
    try:
        if not db.conectar():
            return jsonify({'error': 'Error conectando a BD'}), 500
        
        query = """
            SELECT u.id, u.documento, u.nombres, u.apellidos, u.rostro_data,
                   r.nombre_rol
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE u.documento = %s AND u.estado = 'activo'
        """
        resultado = db.obtener_uno(query, (user_id,))
        
        if not resultado:
            return jsonify({
                'success': False,
                'registered': False,
                'error': 'Usuario no encontrado',
                'user_id': user_id
            }), 404
        
        tiene_rostro = resultado.get('rostro_data') is not None
        nombre_completo = f"{resultado['nombres']} {resultado['apellidos']}"
        
        return jsonify({
            'success': True,
            'registered': tiene_rostro,
            'user_id': user_id,
            'user': {
                'documento': resultado['documento'],
                'nombre': nombre_completo,
                'rol': resultado.get('nombre_rol', 'Usuario')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.desconectar()

@facial_bp.route('/stats', methods=['GET'])
def estadisticas_facial():
    """
    GET /api/facial/stats - Estadísticas de reconocimiento facial
    
    Returns: { "total_usuarios": X, "usuarios_con_rostro": Y, ... }
    """
    try:
        if not db.conectar():
            return jsonify({'error': 'Error conectando a BD'}), 500
        
        # Total de usuarios activos
        query_total = "SELECT COUNT(*) as total FROM usuarios WHERE estado = 'activo'"
        total = db.obtener_uno(query_total)
        total_usuarios = total['total'] if total else 0
        
        # Usuarios con rostro
        query_rostro = "SELECT COUNT(*) as total FROM usuarios WHERE rostro_data IS NOT NULL AND estado = 'activo'"
        con_rostro = db.obtener_uno(query_rostro)
        usuarios_con_rostro = con_rostro['total'] if con_rostro else 0
        
        # Por rol
        query_rol = """
            SELECT r.nombre_rol as rol, 
            COUNT(u.id) as total,
            SUM(CASE WHEN u.rostro_data IS NOT NULL THEN 1 ELSE 0 END) as con_rostro
            FROM usuarios u
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE u.estado = 'activo'
            GROUP BY r.nombre_rol
        """
        por_rol = db.ejecutar_query(query_rol) or []
        
        porcentaje = (usuarios_con_rostro / total_usuarios * 100) if total_usuarios > 0 else 0
        
        return jsonify({
            'success': True,
            'total_usuarios': total_usuarios,
            'usuarios_con_rostro': usuarios_con_rostro,
            'porcentaje_registrado': round(porcentaje, 2),
            'por_rol': por_rol
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.desconectar()
