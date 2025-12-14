# Funciones Auxiliares
# Centro Minero SENA

import uuid
from datetime import datetime, timedelta, date
from typing import Optional, Union
import json

def generar_id(prefijo: str = '', longitud: int = 8) -> str:
    """
    Genera un ID único
    
    Args:
        prefijo: Prefijo para el ID (ej: 'USR', 'EQP')
        longitud: Longitud del ID sin prefijo
        
    Returns:
        ID único
    """
    id_unico = str(uuid.uuid4()).replace('-', '').upper()[:longitud]
    return f"{prefijo}{id_unico}"

def formatear_fecha(fecha: Union[datetime, date], formato: str = '%d/%m/%Y') -> str:
    """
    Formatea una fecha
    
    Args:
        fecha: Fecha a formatear
        formato: Formato deseado
        
    Returns:
        Fecha formateada
    """
    if fecha is None:
        return ''
    return fecha.strftime(formato)

def formatear_fecha_hora(fecha_hora: datetime, formato: str = '%d/%m/%Y %H:%M') -> str:
    """
    Formatea una fecha y hora
    
    Args:
        fecha_hora: Fecha y hora a formatear
        formato: Formato deseado
        
    Returns:
        Fecha y hora formateada
    """
    if fecha_hora is None:
        return ''
    return fecha_hora.strftime(formato)

def parsear_fecha(fecha_str: str, formato: str = '%Y-%m-%d') -> Optional[date]:
    """
    Parsea un string a fecha
    
    Args:
        fecha_str: String con la fecha
        formato: Formato del string
        
    Returns:
        Objeto date o None si hay error
    """
    try:
        return datetime.strptime(fecha_str, formato).date()
    except (ValueError, TypeError):
        return None

def parsear_fecha_hora(fecha_hora_str: str, formato: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    Parsea un string a fecha y hora
    
    Args:
        fecha_hora_str: String con la fecha y hora
        formato: Formato del string
        
    Returns:
        Objeto datetime o None si hay error
    """
    try:
        return datetime.strptime(fecha_hora_str, formato)
    except (ValueError, TypeError):
        return None

def calcular_duracion(fecha_inicio: datetime, fecha_fin: datetime, unidad: str = 'horas') -> float:
    """
    Calcula la duración entre dos fechas
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        unidad: Unidad de tiempo ('segundos', 'minutos', 'horas', 'dias')
        
    Returns:
        Duración en la unidad especificada
    """
    duracion = fecha_fin - fecha_inicio
    segundos = duracion.total_seconds()
    
    if unidad == 'segundos':
        return segundos
    elif unidad == 'minutos':
        return segundos / 60
    elif unidad == 'horas':
        return segundos / 3600
    elif unidad == 'dias':
        return segundos / 86400
    else:
        return segundos

def formatear_duracion(minutos: int) -> str:
    """
    Formatea una duración en minutos a formato legible
    
    Args:
        minutos: Duración en minutos
        
    Returns:
        Duración formateada (ej: '2h 30min')
    """
    if minutos < 60:
        return f"{minutos} min"
    
    horas = minutos // 60
    mins = minutos % 60
    
    if mins == 0:
        return f"{horas}h"
    return f"{horas}h {mins}min"

def calcular_porcentaje(parte: float, total: float) -> float:
    """
    Calcula un porcentaje
    
    Args:
        parte: Parte del total
        total: Total
        
    Returns:
        Porcentaje
    """
    if total == 0:
        return 0.0
    return (parte / total) * 100

def formatear_moneda(valor: float, simbolo: str = '$') -> str:
    """
    Formatea un valor como moneda
    
    Args:
        valor: Valor a formatear
        simbolo: Símbolo de moneda
        
    Returns:
        Valor formateado
    """
    return f"{simbolo}{valor:,.2f}"

def truncar_texto(texto: str, longitud: int = 50, sufijo: str = '...') -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        texto: Texto a truncar
        longitud: Longitud máxima
        sufijo: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if len(texto) <= longitud:
        return texto
    return texto[:longitud - len(sufijo)] + sufijo

def convertir_a_json(obj: dict) -> str:
    """
    Convierte un objeto a JSON string
    
    Args:
        obj: Objeto a convertir
        
    Returns:
        JSON string
    """
    return json.dumps(obj, ensure_ascii=False, default=str)

def parsear_json(json_str: str) -> Optional[dict]:
    """
    Parsea un JSON string a objeto
    
    Args:
        json_str: JSON string
        
    Returns:
        Objeto parseado o None si hay error
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def obtener_fecha_actual() -> date:
    """
    Obtiene la fecha actual
    
    Returns:
        Fecha actual
    """
    return date.today()

def obtener_fecha_hora_actual() -> datetime:
    """
    Obtiene la fecha y hora actual
    
    Returns:
        Fecha y hora actual
    """
    return datetime.now()

def agregar_dias(fecha: date, dias: int) -> date:
    """
    Agrega días a una fecha
    
    Args:
        fecha: Fecha base
        dias: Días a agregar (puede ser negativo)
        
    Returns:
        Nueva fecha
    """
    return fecha + timedelta(days=dias)

def dias_entre_fechas(fecha1: date, fecha2: date) -> int:
    """
    Calcula los días entre dos fechas
    
    Args:
        fecha1: Primera fecha
        fecha2: Segunda fecha
        
    Returns:
        Número de días
    """
    return abs((fecha2 - fecha1).days)

def es_fecha_pasada(fecha: date) -> bool:
    """
    Verifica si una fecha es pasada
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        True si es fecha pasada
    """
    return fecha < date.today()

def es_fecha_futura(fecha: date) -> bool:
    """
    Verifica si una fecha es futura
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        True si es fecha futura
    """
    return fecha > date.today()

# =====================================================================
# FUNCIONES DE CÓDIGOS QR
# =====================================================================

def generar_qr(datos: str, ruta_salida: str = None, tamano: int = 10) -> Optional[str]:
    """
    Genera un código QR con los datos proporcionados
    
    Args:
        datos: Datos a codificar en el QR
        ruta_salida: Ruta donde guardar la imagen (opcional)
        tamano: Tamaño del QR (1-40)
        
    Returns:
        Ruta del archivo generado o datos base64 si no se especifica ruta
    """
    try:
        import qrcode
        import io
        import base64
        
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=tamano,
            border=4,
        )
        qr.add_data(datos)
        qr.make(fit=True)
        
        # Generar imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        if ruta_salida:
            # Guardar en archivo
            img.save(ruta_salida)
            return ruta_salida
        else:
            # Retornar como base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
            
    except ImportError:
        print("Error: Se requiere la librería 'qrcode'. Instalar con: pip install qrcode[pil]")
        return None
    except Exception as e:
        print(f"Error generando QR: {e}")
        return None

def leer_qr(ruta_imagen: str) -> Optional[str]:
    """
    Lee un código QR desde una imagen
    
    Args:
        ruta_imagen: Ruta de la imagen con el código QR
        
    Returns:
        Datos decodificados del QR o None si hay error
    """
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        
        # Abrir imagen
        img = Image.open(ruta_imagen)
        
        # Decodificar QR
        codigos = decode(img)
        
        if codigos:
            return codigos[0].data.decode('utf-8')
        return None
        
    except ImportError:
        print("Error: Se requiere la librería 'pyzbar'. Instalar con: pip install pyzbar")
        return None
    except Exception as e:
        print(f"Error leyendo QR: {e}")
        return None

def generar_qr_equipo(equipo_id: str, nombre: str, ubicacion: str = '') -> Optional[str]:
    """
    Genera un código QR específico para un equipo
    
    Args:
        equipo_id: ID del equipo
        nombre: Nombre del equipo
        ubicacion: Ubicación del equipo
        
    Returns:
        Datos base64 del QR generado
    """
    datos_equipo = {
        'tipo': 'equipo',
        'id': equipo_id,
        'nombre': nombre,
        'ubicacion': ubicacion,
        'timestamp': obtener_fecha_hora_actual().isoformat()
    }
    
    datos_json = convertir_a_json(datos_equipo)
    return generar_qr(datos_json)

def generar_qr_inventario(item_id: str, nombre: str, categoria: str = '') -> Optional[str]:
    """
    Genera un código QR específico para un item de inventario
    
    Args:
        item_id: ID del item
        nombre: Nombre del item
        categoria: Categoría del item
        
    Returns:
        Datos base64 del QR generado
    """
    datos_item = {
        'tipo': 'inventario',
        'id': item_id,
        'nombre': nombre,
        'categoria': categoria,
        'timestamp': obtener_fecha_hora_actual().isoformat()
    }
    
    datos_json = convertir_a_json(datos_item)
    return generar_qr(datos_json)

# =====================================================================
# FUNCIONES DE PROCESAMIENTO DE IMÁGENES
# =====================================================================

def guardar_imagen_equipo(imagen_data, equipo_id: str, directorio: str = 'uploads/equipment_images') -> Optional[tuple]:
    """
    Guarda una imagen de equipo y calcula su hash
    
    Args:
        imagen_data: Datos de la imagen (bytes o base64)
        equipo_id: ID del equipo
        directorio: Directorio donde guardar
        
    Returns:
        Tupla (ruta_relativa, hash_md5) de la imagen guardada o None
    """
    try:
        import os
        import base64
        import hashlib
        from pathlib import Path
        
        # Crear directorio si no existe
        Path(directorio).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = obtener_fecha_hora_actual().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{equipo_id}_{timestamp}.jpg"
        ruta_completa = os.path.join(directorio, nombre_archivo)
        
        # Si es base64, decodificar
        if isinstance(imagen_data, str) and imagen_data.startswith('data:image'):
            imagen_data = imagen_data.split(',')[1]
            imagen_data = base64.b64decode(imagen_data)
        
        # Calcular hash MD5 de la imagen (según guía línea 17)
        imagen_hash = hashlib.md5(imagen_data).hexdigest()
        
        # Guardar imagen
        with open(ruta_completa, 'wb') as f:
            f.write(imagen_data)
        
        return (ruta_completa, imagen_hash)
        
    except Exception as e:
        print(f"Error guardando imagen: {e}")
        return None

def redimensionar_imagen(ruta_imagen: str, ancho: int = 800, alto: int = 600) -> bool:
    """
    Redimensiona una imagen manteniendo la proporción
    
    Args:
        ruta_imagen: Ruta de la imagen
        ancho: Ancho máximo
        alto: Alto máximo
        
    Returns:
        True si se redimensionó correctamente
    """
    try:
        from PIL import Image
        
        img = Image.open(ruta_imagen)
        img.thumbnail((ancho, alto), Image.Resampling.LANCZOS)
        img.save(ruta_imagen, optimize=True, quality=85)
        
        return True
        
    except Exception as e:
        print(f"Error redimensionando imagen: {e}")
        return False
