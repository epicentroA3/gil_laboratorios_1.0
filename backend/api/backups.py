# API REST para Gestión de Backups
# Centro Minero SENA
# Solo accesible para Administradores (id_rol = 1)

from flask import Blueprint, request, jsonify, session, send_file
from functools import wraps
import subprocess
import os
import datetime
import gzip
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.config import Config
from backend.utils.database import DatabaseManager

# Blueprint para backups
backups_bp = Blueprint('backups', __name__, url_prefix='/api/backups')

# Instancia de base de datos
db = DatabaseManager()

# Directorio de backups
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'backups')

# =========================================================
# DECORADORES DE SEGURIDAD
# =========================================================

def require_admin(f):
    """Decorador que requiere que el usuario sea ADMINISTRADOR (id_rol = 1)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Autenticación requerida'}), 401
        
        # Verificar que sea administrador (id_rol = 1)
        user_rol = session.get('user_rol')
        if user_rol != 1:
            return jsonify({
                'success': False, 
                'message': 'Acceso denegado. Solo administradores pueden gestionar backups.'
            }), 403
        
        return f(*args, **kwargs)
    return decorated

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def crear_directorio_backups():
    """Crear directorio de backups si no existe"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"✅ Directorio de backups creado: {BACKUP_DIR}")

def obtener_tamaño_archivo(filepath):
    """Obtener tamaño de archivo en formato legible"""
    try:
        size_bytes = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    except:
        return "0 B"

# =========================================================
# ENDPOINTS DE BACKUPS
# =========================================================

@backups_bp.route('/listar', methods=['GET'])
@require_admin
def listar_backups():
    """Listar todos los backups disponibles"""
    try:
        crear_directorio_backups()
        
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.sql') or filename.endswith('.sql.gz'):
                filepath = os.path.join(BACKUP_DIR, filename)
                
                # Obtener información del archivo
                stat = os.stat(filepath)
                fecha_creacion = datetime.datetime.fromtimestamp(stat.st_mtime)
                
                backups.append({
                    'nombre': filename,
                    'fecha': fecha_creacion.strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_timestamp': stat.st_mtime,
                    'tamaño': obtener_tamaño_archivo(filepath),
                    'tamaño_bytes': stat.st_size
                })
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x['fecha_timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'backups': backups,
            'total': len(backups)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error listando backups: {str(e)}'}), 500

@backups_bp.route('/crear', methods=['POST'])
@require_admin
def crear_backup():
    """Crear un nuevo backup de la base de datos"""
    try:
        crear_directorio_backups()
        
        # Generar nombre del archivo
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.sql"
        filepath = os.path.join(BACKUP_DIR, filename)
        
        # Obtener credenciales de la base de datos
        db_config = Config.get_db_config()
        
        # Comando mysqldump
        cmd = [
            'mysqldump',
            f'--host={db_config["host"]}',
            f'--port={db_config["port"]}',
            f'--user={db_config["user"]}',
            f'--password={db_config["password"]}',
            '--single-transaction',
            '--routines',
            '--triggers',
            '--events',
            db_config['database']
        ]
        
        # Ejecutar mysqldump
        with open(filepath, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                'success': False, 
                'message': f'Error creando backup: {error_msg}'
            }), 500
        
        # Comprimir el archivo
        filepath_gz = filepath + '.gz'
        with open(filepath, 'rb') as f_in:
            with gzip.open(filepath_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Eliminar archivo sin comprimir
        os.remove(filepath)
        
        # Registrar en logs
        try:
            log_query = """
                INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                VALUES ('backups', 'INFO', %s, %s, %s)
            """
            mensaje = f'Backup creado: {filename}.gz'
            db.ejecutar_comando(log_query, (mensaje, session.get('user_id'), request.remote_addr))
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Backup creado exitosamente',
            'filename': filename + '.gz',
            'tamaño': obtener_tamaño_archivo(filepath_gz)
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creando backup: {str(e)}'}), 500

@backups_bp.route('/descargar/<filename>', methods=['GET'])
@require_admin
def descargar_backup(filename):
    """Descargar un archivo de backup"""
    try:
        filepath = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        # Registrar descarga en logs
        try:
            log_query = """
                INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                VALUES ('backups', 'INFO', %s, %s, %s)
            """
            mensaje = f'Backup descargado: {filename}'
            db.ejecutar_comando(log_query, (mensaje, session.get('user_id'), request.remote_addr))
        except:
            pass
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error descargando backup: {str(e)}'}), 500

@backups_bp.route('/eliminar', methods=['POST'])
@require_admin
def eliminar_backup():
    """Eliminar un archivo de backup"""
    try:
        data = request.get_json()
        filename = data.get('filename', '').strip()
        
        if not filename:
            return jsonify({'success': False, 'message': 'Nombre de archivo requerido'}), 400
        
        filepath = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        # Eliminar archivo
        os.remove(filepath)
        
        # Registrar eliminación en logs
        try:
            log_query = """
                INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                VALUES ('backups', 'WARNING', %s, %s, %s)
            """
            mensaje = f'Backup eliminado: {filename}'
            db.ejecutar_comando(log_query, (mensaje, session.get('user_id'), request.remote_addr))
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Backup eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error eliminando backup: {str(e)}'}), 500

@backups_bp.route('/restaurar', methods=['POST'])
@require_admin
def restaurar_backup():
    """Restaurar la base de datos desde un backup"""
    try:
        data = request.get_json()
        filename = data.get('filename', '').strip()
        
        if not filename:
            return jsonify({'success': False, 'message': 'Nombre de archivo requerido'}), 400
        
        filepath = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        # Descomprimir si es necesario
        if filename.endswith('.gz'):
            filepath_sql = filepath[:-3]  # Remover .gz
            with gzip.open(filepath, 'rb') as f_in:
                with open(filepath_sql, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            filepath_sql = filepath
        
        # Obtener credenciales de la base de datos
        db_config = Config.get_db_config()
        
        # Comando mysql para restaurar
        cmd = [
            'mysql',
            f'--host={db_config["host"]}',
            f'--port={db_config["port"]}',
            f'--user={db_config["user"]}',
            f'--password={db_config["password"]}',
            db_config['database']
        ]
        
        # Ejecutar restauración
        with open(filepath_sql, 'r', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
        
        # Limpiar archivo temporal si se descomprimió
        if filename.endswith('.gz') and os.path.exists(filepath_sql):
            os.remove(filepath_sql)
        
        if result.returncode != 0:
            error_msg = result.stderr
            return jsonify({
                'success': False,
                'message': f'Error restaurando backup: {error_msg}'
            }), 500
        
        # Registrar restauración en logs
        try:
            log_query = """
                INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
                VALUES ('backups', 'CRITICAL', %s, %s, %s)
            """
            mensaje = f'Base de datos restaurada desde: {filename}'
            db.ejecutar_comando(log_query, (mensaje, session.get('user_id'), request.remote_addr))
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': 'Base de datos restaurada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error restaurando backup: {str(e)}'}), 500

@backups_bp.route('/info', methods=['GET'])
@require_admin
def info_sistema():
    """Obtener información del sistema de backups"""
    try:
        crear_directorio_backups()
        
        # Contar archivos
        total_backups = len([f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql') or f.endswith('.sql.gz')])
        
        # Calcular espacio usado
        total_size = sum(os.path.getsize(os.path.join(BACKUP_DIR, f)) 
                        for f in os.listdir(BACKUP_DIR) 
                        if f.endswith('.sql') or f.endswith('.sql.gz'))
        
        # Obtener tamaño de la base de datos
        try:
            query = """
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
            """
            result = db.obtener_uno(query)
            db_size_mb = result['size_mb'] if result else 0
        except:
            db_size_mb = 0
        
        return jsonify({
            'success': True,
            'info': {
                'total_backups': total_backups,
                'espacio_usado': obtener_tamaño_archivo(total_size) if total_size > 0 else "0 B",
                'espacio_usado_bytes': total_size,
                'directorio': BACKUP_DIR,
                'tamaño_bd_mb': db_size_mb,
                'usuario': session.get('user_name'),
                'rol': session.get('user_type')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error obteniendo información: {str(e)}'}), 500
