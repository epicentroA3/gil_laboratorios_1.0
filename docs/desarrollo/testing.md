
```markdown
# 🧪 Guía de Pruebas - Sistema GIL

## 1. Estrategia de Pruebas

### Pirámide de Pruebas
text
    /¯¯¯¯¯¯¯¯¯¯¯¯¯¯\
   /  Pruebas E2E   \
  /      (10%)       \
 /____________________\
/                      \
/ Pruebas Integración
/ (20%)
/__________________________
/
| Pruebas Unitarias |
| (70%) |
|____________________________|

text

### Cobertura por Módulo
| Módulo | Unitarias | Integración | E2E | Total |
|--------|-----------|-------------|-----|-------|
| Autenticación | 85% | 90% | 80% | 85% |
| Equipos | 90% | 85% | 75% | 85% |
| Préstamos | 85% | 80% | 70% | 80% |
| IA | 80% | 75% | 65% | 75% |
| Reportes | 75% | 80% | 70% | 75% |
| **Total** | **85%** | **82%** | **72%** | **80%** |

## 2. Tipos de Pruebas

### 2.1 Pruebas Unitarias
```python
# tests/unit/test_auth_service.py
import pytest
from unittest.mock import Mock, patch
from services.auth_service import AuthService
from exceptions import AuthenticationError

class TestAuthService:
    
    @pytest.fixture
    def auth_service(self):
        """Fixture que retorna instancia del servicio."""
        return AuthService()
    
    @pytest.fixture
    def mock_user(self):
        """Fixture que retorna usuario mock."""
        return Mock(
            id=1,
            documento='123456789',
            password_hash='$2b$12$...'
        )
    
    def test_login_exitoso(self, auth_service, mock_user):
        """Test: login con credenciales válidas."""
        # Arrange
        documento = '123456789'
        password = 'Password123!'
        
        # Mock del repositorio
        with patch('repositories.user_repository.find_by_document') as mock_find:
            mock_find.return_value = mock_user
            
            # Mock de bcrypt
            with patch('bcrypt.checkpw') as mock_check:
                mock_check.return_value = True
                
                # Act
                resultado = auth_service.login(documento, password)
                
                # Assert
                assert resultado['success'] is True
                assert 'token' in resultado
                assert resultado['user']['documento'] == documento
    
    def test_login_password_incorrecto(self, auth_service, mock_user):
        """Test: login con password incorrecto."""
        # Arrange
        with patch('repositories.user_repository.find_by_document') as mock_find:
            mock_find.return_value = mock_user
            
            with patch('bcrypt.checkpw') as mock_check:
                mock_check.return_value = False
                
                # Act & Assert
                with pytest.raises(AuthenticationError) as exc_info:
                    auth_service.login('123456789', 'WrongPass123!')
                
                assert 'contraseña incorrecta' in str(exc_info.value)
    
    @pytest.mark.parametrize('documento,password', [
        ('', 'Password123!'),  # documento vacío
        ('123456789', ''),     # password vacío
        ('abc', 'Password123!'),  # documento muy corto
        ('123456789', 'short'),   # password muy corto
    ])
    def test_login_datos_invalidos(self, auth_service, documento, password):
        """Test: login con datos inválidos."""
        with pytest.raises(ValidationError):
            auth_service.login(documento, password)
2.2 Pruebas de Integración
python
# tests/integration/test_prestamo_flow.py
import pytest
from datetime import datetime, timedelta
from app import create_app
from database import db

class TestPrestamoIntegration:
    
    @pytest.fixture
    def app(self):
        """Fixture que crea aplicación de prueba."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Fixture que retorna cliente de pruebas."""
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client):
        """Fixture que obtiene headers de autenticación."""
        # Crear usuario de prueba
        response = client.post('/api/v1/auth/register', json={
            'documento': 'TEST001',
            'nombres': 'Usuario',
            'apellidos': 'Prueba',
            'email': 'test@example.com',
            'password': 'Test123!'
        })
        
        # Login para obtener token
        response = client.post('/api/v1/auth/login', json={
            'documento': 'TEST001',
            'password': 'Test123!'
        })
        
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_flujo_completo_prestamo(self, client, auth_headers):
        """Test: flujo completo de solicitud de préstamo."""
        # 1. Crear equipo de prueba
        equipo_data = {
            'codigo_interno': 'EQP-TEST-001',
            'nombre': 'Microscopio Test',
            'estado': 'disponible'
        }
        
        response = client.post(
            '/api/v1/equipos',
            json=equipo_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        equipo_id = response.json['data']['id']
        
        # 2. Solicitar préstamo
        prestamo_data = {
            'id_equipo': equipo_id,
            'proposito': 'Prueba de integración',
            'fecha_devolucion_programada': (
                datetime.now() + timedelta(days=7)
            ).isoformat()
        }
        
        response = client.post(
            '/api/v1/prestamos',
            json=prestamo_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        prestamo_id = response.json['data']['id']
        
        # 3. Verificar que el equipo cambió de estado
        response = client.get(
            f'/api/v1/equipos/{equipo_id}',
            headers=auth_headers
        )
        assert response.json['data']['estado'] == 'prestado'
        
        # 4. Registrar devolución
        response = client.post(
            f'/api/v1/prestamos/{prestamo_id}/devolver',
            json={'observaciones': 'Equipo devuelto en buen estado'},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # 5. Verificar que el equipo vuelve a disponible
        response = client.get(
            f'/api/v1/equipos/{equipo_id}',
            headers=auth_headers
        )
        assert response.json['data']['estado'] == 'disponible'
2.3 Pruebas E2E
python
# tests/e2e/test_user_journey.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserJourneyE2E:
    
    @pytest.fixture
    def driver(self):
        """Fixture que inicializa el driver de Selenium."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_journey_prestamo_equipo(self, driver):
        """Test E2E: Usuario solicita y devuelve equipo."""
        # 1. Navegar a la aplicación
        driver.get('http://localhost:5000')
        
        # 2. Login
        driver.find_element(By.ID, 'documento').send_keys('APRENDIZ001')
        driver.find_element(By.ID, 'password').send_keys('Aprendiz123!')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # Esperar redirección al dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains('/dashboard')
        )
        
        # 3. Navegar a equipos disponibles
        driver.find_element(By.LINK_TEXT, 'Equipos').click()
        driver.find_element(By.LINK_TEXT, 'Disponibles').click()
        
        # 4. Seleccionar primer equipo disponible
        equipos = driver.find_elements(By.CSS_SELECTOR, '.equipo-card')
        assert len(equipos) > 0
        equipos[0].find_element(By.CSS_SELECTOR, '.btn-prestar').click()
        
        # 5. Completar formulario de préstamo
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'proposito'))
        )
        
        driver.find_element(By.ID, 'proposito').send_keys(
            'Prueba práctica de laboratorio'
        )
        driver.find_element(By.ID, 'fecha_devolucion').send_keys(
            '2024-12-31'
        )
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 6. Verificar confirmación
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        
        mensaje = driver.find_element(By.CLASS_NAME, 'alert-success').text
        assert 'solicitud fue enviada' in mensaje.lower()
3. Configuración del Entorno de Pruebas
3.1 pytest.ini
ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=backend
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
    -p no:warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
3.2 conftest.py
python
# tests/conftest.py
import pytest
import tempfile
import os
from app import create_app
from database import db

@pytest.fixture(scope='session')
def app():
    """Fixture de aplicación para pruebas."""
    # Crear archivo temporal para base de datos
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Limpiar archivo temporal
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Fixture de cliente de pruebas."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture de CLI runner."""
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def enable_transactional_tests(app):
    """Habilitar tests transaccionales."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        db.session = session
        
        yield
        
        transaction.rollback()
        connection.close()
        session.remove()
4. Pruebas Específicas por Módulo
4.1 Pruebas de API
python
# tests/api/test_equipos_endpoints.py
class TestEquiposEndpoints:
    
    def test_listar_equipos(self, client, auth_headers):
        """Test: GET /api/v1/equipos"""
        response = client.get(
            '/api/v1/equipos',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert 'data' in response.json
        assert isinstance(response.json['data'], list)
    
    def test_crear_equipo(self, client, auth_headers):
        """Test: POST /api/v1/equipos"""
        equipo_data = {
            'codigo_interno': 'EQP-TEST-001',
            'nombre': 'Equipo de Prueba',
            'marca': 'TestBrand',
            'modelo': 'TestModel',
            'estado': 'disponible'
        }
        
        response = client.post(
            '/api/v1/equipos',
            json=equipo_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        assert response.json['success'] is True
        assert 'id' in response.json['data']
    
    def test_equipo_no_encontrado(self, client, auth_headers):
        """Test: GET equipo inexistente"""
        response = client.get(
            '/api/v1/equipos/999999',
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert response.json['success'] is False
4.2 Pruebas de Modelos IA
python
# tests/ia/test_reconocimiento.py
import cv2
import numpy as np
from services.ia.reconocimiento import ReconocimientoService

class TestReconocimientoService:
    
    def test_reconocimiento_imagen_valida(self):
        """Test: reconocer equipo en imagen válida."""
        # Crear imagen de prueba
        imagen = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.putText(imagen, 'microscopio', (50, 112), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        servicio = ReconocimientoService()
        resultado = servicio.reconocer_equipo(imagen)
        
        assert 'equipo_detectado' in resultado
        assert 'confianza' in resultado
        assert isinstance(resultado['confianza'], float)
        assert 0 <= resultado['confianza'] <= 1
    
    def test_imagen_invalida(self):
        """Test: manejo de imagen inválida."""
        servicio = ReconocimientoService()
        
        with pytest.raises(ValueError):
            servicio.reconocer_equipo(None)
5. Pruebas de Rendimiento
5.1 Locust - Pruebas de Carga
python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class GILUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login al iniciar."""
        response = self.client.post('/api/v1/auth/login', json={
            'documento': 'PERF001',
            'password': 'Perf123!'
        })
        
        if response.status_code == 200:
            self.token = response.json()['access_token']
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
    
    @task(3)
    def listar_equipos(self):
        """Listar equipos disponibles."""
        self.client.get(
            '/api/v1/equipos/disponibles',
            headers=self.headers
        )
    
    @task(1)
    def ver_detalle_equipo(self):
        """Ver detalle de equipo específico."""
        self.client.get(
            '/api/v1/equipos/1',
            headers=self.headers
        )
    
    @task(2)
    def listar_prestamos(self):
        """Listar préstamos activos."""
        self.client.get(
            '/api/v1/prestamos?estado=activo',
            headers=self.headers
        )
5.2 k6 - Pruebas de Estrés
javascript
// tests/performance/stress_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
    stages: [
        { duration: '30s', target: 50 },   // Rampa hasta 50 usuarios
        { duration: '1m', target: 100 },   // Rampa hasta 100 usuarios
        { duration: '2m', target: 200 },   // Rampa hasta 200 usuarios
        { duration: '30s', target: 0 },    // Rampa descendente
    ],
    thresholds: {
        'http_req_duration': ['p(95)<500'], // 95% de requests < 500ms
        'errors': ['rate<0.1'],             // < 10% de errores
    },
};

const BASE_URL = 'http://localhost:5000';
const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...';

export default function() {
    const params = {
        headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/json',
        },
    };
    
    // Test 1: Health check
    let res = http.get(`${BASE_URL}/api/v1/health`, params);
    let success = check(res, {
        'health check status 200': (r) => r.status === 200,
        'health check response time < 200ms': (r) => r.timings.duration < 200,
    });
    errorRate.add(!success);
    
    // Test 2: Listar equipos
    res = http.get(`${BASE_URL}/api/v1/equipos`, params);
    success = check(res, {
        'listar equipos status 200': (r) => r.status === 200,
        'listar equipos tiene datos': (r) => r.json().data.length > 0,
    });
    errorRate.add(!success);
    
    sleep(1);
}
6. Pruebas de Seguridad
6.1 OWASP ZAP Integration
python
# tests/security/security_scan.py
import requests
from zapv2 import ZAPv2

class TestSecurity:
    
    def test_owasp_scan(self):
        """Ejecutar escaneo de seguridad OWASP."""
        zap = ZAPv2(apikey='your-api-key', 
                   proxies={'http': 'http://127.0.0.1:8080'})
        
        # Configurar escaneo
        target = 'http://localhost:5000'
        
        # Iniciar spider
        print('Iniciando spider...')
        scan_id = zap.spider.scan(target)
        
        # Esperar completar spider
        while int(zap.spider.status(scan_id)) < 100:
            time.sleep(5)
        
        # Iniciar escaneo activo
        print('Iniciando escaneo activo...')
        scan_id = zap.ascan.scan(target)
        
        # Esperar completar escaneo
        while int(zap.ascan.status(scan_id)) < 100:
            time.sleep(5)
        
        # Obtener resultados
        alerts = zap.core.alerts()
        
        # Verificar vulnerabilidades críticas
        critical_alerts = [
            alert for alert in alerts 
            if alert['risk'] == 'High'
        ]
        
        assert len(critical_alerts) == 0, \
            f'Se encontraron {len(critical_alerts)} vulnerabilidades críticas'
6.2 Pruebas de Inyección SQL
python
# tests/security/test_sql_injection.py
class TestSQLInjection:
    
    def test_sql_injection_login(self, client):
        """Test: prevenir SQL injection en login."""
        # Intentar inyección SQL
        payloads = [
            "' OR '1'='1",
            "' UNION SELECT * FROM usuarios --",
            "admin'--",
            "' OR 1=1--",
        ]
        
        for payload in payloads:
            response = client.post('/api/v1/auth/login', json={
                'documento': payload,
                'password': payload
            })
            
            # Debe rechazar todas las inyecciones
            assert response.status_code != 200
            assert 'error' in response.json
7. Pruebas de Usabilidad
7.1 Pruebas de Accesibilidad
python
# tests/usability/test_accessibility.py
from axe_selenium_python import Axe

class TestAccessibility:
    
    def test_accessibility_compliance(self, driver):
        """Test: cumplimiento de estándares de accesibilidad."""
        driver.get('http://localhost:5000/login')
        
        # Ejecutar análisis de accesibilidad
        axe = Axe(driver)
        axe.inject()
        results = axe.run()
        
        # Verificar violaciones críticas
        critical_violations = [
            v for v in results['violations']
            if v['impact'] in ['critical', 'serious']
        ]
        
        assert len(critical_violations) == 0, \
            f'Se encontraron {len(critical_violations)} violaciones críticas de accesibilidad'
8. Automatización de Pruebas
8.1 GitHub Actions
yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: gil_test
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      env:
        DB_HOST: localhost
        DB_PORT: 3306
        DB_NAME: gil_test
        DB_USER: root
        DB_PASSWORD: root
      run: |
        pytest tests/ --cov=backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
    
    - name: Run security scan
      run: |
        python tests/security/security_scan.py
9. Reportes y Métricas
9.1 Generación de Reportes
python
# utils/test_reporter.py
import json
import pandas as pd
from datetime import datetime

class TestReporter:
    
    def generate_html_report(self, test_results):
        """Generar reporte HTML de pruebas."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de Pruebas - Sistema GIL</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; }
                .metric { display: inline-block; margin: 0 20px; }
                .passed { color: green; }
                .failed { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>Reporte de Pruebas - Sistema GIL</h1>
            <div class="summary">
                <h2>Resumen</h2>
                <div class="metric">
                    <h3>Cobertura Total</h3>
                    <p class="passed">85%</p>
                </div>
                <!-- más métricas -->
            </div>
            <!-- detalles de pruebas -->
        </body>
        </html>
        """
        return html
10. Checklist de Pruebas
Antes de cada Release:
Ejecutar todas las pruebas unitarias

Ejecutar pruebas de integración

Ejecutar pruebas E2E

Ejecutar pruebas de rendimiento

Ejecutar pruebas de seguridad

Verificar cobertura de código >= 80%

Revisar y corregir pruebas fallidas

Generar reporte de pruebas

Aprobar pruebas por QA

Pruebas Específicas por Módulo:
Auth: Login, logout, recuperación de contraseña

Equipos: CRUD, búsqueda, filtros

Préstamos: Flujo completo, validaciones

IA: Reconocimiento imágenes, asistente voz

Reportes: Generación, exportación

API: Todos los endpoints documentados

Base de Datos: Migraciones, integridad

Frontend: Usabilidad, responsive design