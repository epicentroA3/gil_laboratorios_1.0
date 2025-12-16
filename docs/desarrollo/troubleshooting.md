### **7. doc/desarrollo/troubleshooting.md**
```markdown
# 🔧 Solución de Problemas - Sistema GIL

## 1. Problemas Comunes y Soluciones

### 1.1 Error de Conexión a Base de Datos

#### Síntomas:
OperationalError: (2003, "Can't connect to MySQL server on 'localhost' ([Errno 111] Connection refused)")

text

#### Soluciones:
```bash
# 1. Verificar si MySQL está corriendo
sudo systemctl status mysql

# 2. Si no está corriendo, iniciarlo
sudo systemctl start mysql

# 3. Verificar credenciales en .env
cat .env | grep DB_

# 4. Verificar que el usuario tiene permisos
mysql -u root -p -e "SHOW GRANTS FOR 'gil_app'@'localhost';"

# 5. Verificar puerto MySQL
netstat -tlnp | grep 3306

# 6. Si MySQL escucha en socket en lugar de TCP
# Editar /etc/mysql/mysql.conf.d/mysqld.cnf
# Cambiar: bind-address = 127.0.0.1 a 0.0.0.0
Configuración de .env correcta:
env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gil_laboratorios
DB_USER=gil_app
DB_PASSWORD=TuContraseñaSegura123!
1.2 Error de Autenticación JWT
Síntomas:
text
jwt.exceptions.DecodeError: It is required that you pass in a value for the "algorithms" argument
Soluciones:
python
# 1. Verificar que el token se está generando correctamente
import jwt
from datetime import datetime, timedelta

payload = {
    'user_id': 1,
    'exp': datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(
    payload, 
    app.config['SECRET_KEY'], 
    algorithm='HS256'
)

# 2. Verificar que se usa el mismo algoritmo para decodificar
try:
    decoded = jwt.decode(
        token, 
        app.config['SECRET_KEY'], 
        algorithms=['HS256']
    )
except jwt.ExpiredSignatureError:
    print("Token expirado")
except jwt.InvalidTokenError:
    print("Token inválido")

# 3. Verificar SECRET_KEY en configuración
print(app.config.get('SECRET_KEY'))
1.3 Error al Subir Archivos
Síntomas:
text
OSError: [Errno 28] No space left on device
Soluciones:
bash
# 1. Verificar espacio en disco
df -h

# 2. Limpiar archivos temporales
# Archivos de más de 30 días
find /var/www/gil/uploads -type f -mtime +30 -delete

# 3. Limpiar logs antiguos
find /var/www/gil/logs -name "*.log" -mtime +7 -delete

# 4. Verificar límites de tamaño
# Configurar en Nginx
client_max_body_size 100M;

# Configurar en Flask
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
1.4 Problemas de Rendimiento
Síntomas:
Lentitud en consultas

Timeouts en API

Alto uso de CPU

Soluciones:
python
# 1. Optimizar consultas SQL
# Usar EXPLAIN para analizar consultas lentas
EXPLAIN SELECT * FROM equipos WHERE estado = 'disponible';

# 2. Agregar índices
CREATE INDEX idx_equipos_estado ON equipos(estado);
CREATE INDEX idx_prestamos_fecha ON prestamos(fecha_solicitud);

# 3. Implementar caché
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

@cache.memoize(timeout=300)  # 5 minutos
def obtener_equipos_disponibles():
    return Equipo.query.filter_by(estado='disponible').all()

# 4. Usar paginación
@app.route('/api/v1/equipos')
def listar_equipos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    equipos = Equipo.query.paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    return {
        'data': [e.to_dict() for e in equipos.items],
        'total': equipos.total,
        'pages': equipos.pages,
        'page': page
    }
2. Problemas Específicos por Módulo
2.1 Módulo de Autenticación
Problema: Usuario no puede hacer login
python
# Pasos de diagnóstico:
def diagnose_login_issue(documento, password):
    """
    Diagnostica problemas de login.
    """
    # 1. Verificar que el usuario existe
    usuario = Usuario.query.filter_by(documento=documento).first()
    if not usuario:
        return "Usuario no encontrado"
    
    # 2. Verificar estado del usuario
    if usuario.estado != 'activo':
        return f"Usuario {usuario.estado}. Contacte al administrador"
    
    # 3. Verificar contraseña
    if not bcrypt.checkpw(password.encode(), usuario.password_hash.encode()):
        # Incrementar contador de intentos fallidos
        incrementar_intentos_fallidos(usuario.id)
        return "Contraseña incorrecta"
    
    # 4. Verificar si está bloqueado por intentos fallidos
    if usuario.intentos_fallidos >= 3:
        return "Cuenta bloqueada por múltiples intentos fallidos"
    
    # 5. Si pasa todas las validaciones
        return None  # Login exitoso
2.2 Módulo de Equipos
Problema: No se pueden crear nuevos equipos
python
# Verificaciones:
def check_equipo_creation():
    """
    Verifica problemas comunes al crear equipos.
    """
    issues = []
    
    # 1. Verificar permisos de usuario
    if not current_user.tiene_permiso('equipos_crear'):
        issues.append("Usuario no tiene permisos para crear equipos")
    
    # 2. Verificar categorías existentes
    categorias = CategoriaEquipo.query.all()
    if not categorias:
        issues.append("No hay categorías definidas")
    
    # 3. Verificar laboratorios existentes
    laboratorios = Laboratorio.query.all()
    if not laboratorios:
        issues.append("No hay laboratorios definidos")
    
    # 4. Verificar código único
    codigo = request.json.get('codigo_interno')
    if Equipo.query.filter_by(codigo_interno=codigo).first():
        issues.append(f"El código {codigo} ya existe")
    
    return issues
2.3 Módulo de Préstamos
Problema: No se puede aprobar préstamo
bash
# Comandos de diagnóstico:
# 1. Verificar estado actual del préstamo
SELECT id, estado FROM prestamos WHERE id = 123;

# 2. Verificar estado del equipo
SELECT e.codigo_interno, e.estado 
FROM prestamos p
JOIN equipos e ON p.id_equipo = e.id
WHERE p.id = 123;

# 3. Verificar permisos del usuario que aprueba
SELECT u.documento, r.nombre_rol, r.permisos
FROM usuarios u
JOIN roles r ON u.id_rol = r.id
WHERE u.id = 456;

# 4. Verificar si hay préstamos activos del mismo usuario
SELECT COUNT(*) as prestamos_activos
FROM prestamos
WHERE id_usuario_solicitante = 789
  AND estado IN ('activo', 'aprobado');
2.4 Módulo de IA
Problema: Reconocimiento de imágenes no funciona
python
def diagnose_image_recognition():
    """
    Diagnostica problemas del módulo de reconocimiento de imágenes.
    """
    issues = []
    
    # 1. Verificar que el modelo existe
    model_path = 'models/mobilenet_v2.h5'
    if not os.path.exists(model_path):
        issues.append(f"Modelo no encontrado en {model_path}")
    
    # 2. Verificar dependencias de TensorFlow
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
    except ImportError as e:
        issues.append(f"TensorFlow no instalado: {e}")
    
    # 3. Verificar GPU/CUDA
    if tf.test.gpu_device_name():
        print('GPU encontrada:', tf.test.gpu_device_name())
    else:
        issues.append("No se encontró GPU, usando CPU")
    
    # 4. Verificar formato de imagen
    allowed_formats = ['.jpg', '.jpeg', '.png', '.bmp']
    # ...
    
    return issues
3. Monitoreo y Logs
3.1 Configuración de Logs
python
# config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """
    Configura sistema de logging para la aplicación.
    """
    # Crear directorio de logs si no existe
    log_dir = app.config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar logger principal
    logger = logging.getLogger('gil')
    logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Handler para archivo
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'gil.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    logger.addHandler(file_handler)
    
    # Handler para consola
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)
    
    return logger

# Uso en la aplicación
logger = setup_logging(app)

# En los módulos
logger.info(f"Usuario {user_id} inició sesión")
logger.error(f"Error al procesar imagen: {str(e)}")
logger.debug(f"Consulta SQL: {query}")
3.2 Monitoreo con Prometheus
python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from flask import Response

# Métricas definidas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'app_errors_total',
    'Total application errors',
    ['error_type', 'module']
)

# Decorador para medir endpoints
def monitor_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            status = response.status_code
        except Exception as e:
            status = 500
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                module=f.__module__
            ).inc()
            raise
        
        # Registrar métricas
        request_latency = time.time() - start_time
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=status
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.path
        ).observe(request_latency)
        
        return response
    return decorated_function

# Endpoint para métricas
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')
4. Herramientas de Diagnóstico
4.1 Script de Diagnóstico del Sistema
bash
#!/bin/bash
# diagnose_system.sh

echo "🔍 Diagnóstico del Sistema GIL"
echo "================================"

echo ""
echo "1. Verificando servicios..."
echo "----------------------------"

# MySQL
if systemctl is-active --quiet mysql; then
    echo "✅ MySQL está corriendo"
else
    echo "❌ MySQL NO está corriendo"
    echo "   Intentando iniciar..."
    sudo systemctl start mysql
fi

# Gunicorn/Nginx
if systemctl is-active --quiet gil; then
    echo "✅ Servicio GIL está corriendo"
else
    echo "❌ Servicio GIL NO está corriendo"
fi

echo ""
echo "2. Verificando conexión a BD..."
echo "--------------------------------"

python3 -c "
import MySQLdb
try:
    db = MySQLdb.connect(
        host='localhost',
        user='${DB_USER}',
        passwd='${DB_PASSWORD}',
        db='${DB_NAME}'
    )
    print('✅ Conexión a BD exitosa')
    
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    count = cursor.fetchone()[0]
    print(f'   Usuarios en sistema: {count}')
    
    db.close()
except Exception as e:
    print(f'❌ Error conexión BD: {e}')
"

echo ""
echo "3. Verificando espacio en disco..."
echo "-----------------------------------"

df -h | grep -E "(Filesystem|/var|/)"

echo ""
echo "4. Verificando logs de errores..."
echo "----------------------------------"

if [ -f "/var/www/gil/logs/error.log" ]; then
    echo "Últimos 10 errores:"
    tail -n 10 /var/www/gil/logs/error.log
else
    echo "❌ Archivo de logs no encontrado"
fi

echo ""
echo "5. Verificando endpoints de API..."
echo "-----------------------------------"

curl -s http://localhost:5000/api/v1/health | python3 -m json.tool

echo ""
echo "Diagnóstico completado."
4.2 Comandos Útiles para Troubleshooting
bash
# Verificar uso de memoria
free -h

# Verificar uso de CPU
top -bn1 | grep "Cpu(s)"

# Verificar procesos Python
ps aux | grep python

# Verificar conexiones MySQL
mysqladmin processlist -u root -p

# Verificar logs en tiempo real
tail -f /var/www/gil/logs/*.log

# Verificar permisos de archivos
ls -la /var/www/gil/

# Probar conectividad
curl -v http://localhost:5000/api/v1/health

# Verificar certificados SSL
openssl s_client -connect localhost:443 -servername gil.centrominero.edu.co
5. Problemas de Despliegue
5.1 Problemas con Docker
dockerfile
# Solución para problemas comunes en Docker

# 1. Si la aplicación no inicia
# Verificar logs del contenedor
docker logs <nombre_contenedor>

# 2. Si no puede conectarse a MySQL
# Verificar red Docker
docker network ls
docker inspect <nombre_contenedor> | grep Network

# 3. Si hay problemas de permisos
# Reconstruir con --no-cache
docker-compose build --no-cache

# 4. Si ocupa mucho espacio
# Limpiar imágenes no usadas
docker system prune -a

# 5. Debug interactivo
docker exec -it <nombre_contenedor> bash
python debug.py
5.2 Problemas con Nginx
nginx
# Verificar configuración
sudo nginx -t

# Recargar configuración
sudo nginx -s reload

# Reiniciar servicio
sudo systemctl restart nginx

# Verificar logs
sudo tail -f /var/log/nginx/error.log

# Configuración de ejemplo para problemas comunes
server {
    # Si hay problemas de CORS
    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
    
    # Si hay problemas de timeouts
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    send_timeout 300s;
    
    # Si hay problemas de tamaño de archivos
    client_max_body_size 100M;
}
6. Recuperación de Desastres
6.1 Restauración de Base de Datos
bash
#!/bin/bash
# restore_database.sh

set -e

echo "🔄 Iniciando restauración de base de datos..."

# Parámetros
BACKUP_FILE=$1
DB_NAME="gil_laboratorios"
DB_USER="gil_app"
DB_PASS="TuContraseñaSegura123!"

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Especificar archivo de backup"
    echo "Uso: $0 <backup_file.sql>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Archivo de backup no encontrado: $BACKUP_FILE"
    exit 1
fi

# 1. Detener aplicación
echo "🛑 Deteniendo aplicación..."
sudo systemctl stop gil.service

# 2. Crear backup actual
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP="backup_before_restore_$TIMESTAMP.sql"
echo "📦 Creando backup actual..."
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $CURRENT_BACKUP

# 3. Restaurar backup
echo "🗄️ Restaurando backup..."
mysql -u $DB_USER -p$DB_PASS $DB_NAME < $BACKUP_FILE

# 4. Iniciar aplicación
echo "🚀 Iniciando aplicación..."
sudo systemctl start gil.service

# 5. Verificar
echo "🔍 Verificando restauración..."
sleep 5
curl -s http://localhost:5000/api/v1/health | grep -q '"status": "ok"'

if [ $? -eq 0 ]; then
    echo "✅ Restauración completada exitosamente"
else
    echo "❌ Error en restauración, revisar logs"
    # Restaurar backup anterior
    mysql -u $DB_USER -p$DB_PASS $DB_NAME < $CURRENT_BACKUP
    sudo systemctl start gil.service
fi