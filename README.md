# 🔬 GIL Laboratorios

**Sistema de Gestión Integral de Laboratorios**  
Centro Minero de Sogamoso - SENA

---

## 📋 Descripción

Sistema web para la gestión integral de laboratorios del SENA, incluyendo:
- ✅ Gestión de usuarios y roles con permisos granulares
- ✅ Inventario inteligente de equipos
- ✅ Sistema de préstamos y trazabilidad
- ✅ Gestión de laboratorios y espacios
- ✅ Prácticas de laboratorio
- ✅ Reconocimiento de equipos con IA (MobileNet)
- ✅ Asistente de voz LUCIA
- ✅ Mantenimiento predictivo
- ✅ Generación de códigos QR

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Farenheit117/gil_laboratorios.git
cd gil_laboratorios
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```
### 4. Configurar variables de entorno (opcional)

Crear archivo `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=gil_laboratorios
SECRET_KEY=tu_clave_secreta
```


### 5. Configurar base de datos MySQL

Crear la base de datos y cargar el esquema:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p gil_laboratorios < database/data.sql
```

O desde MySQL Workbench, ejecutar los scripts en orden:
1. `database/schema.sql`
2. `database/data.sql`





### 6. Ejecutar la aplicación

```bash
python app.py
```

Acceder a: http://localhost:5000


---

## 📁 Estructura del proyecto

```
gil_laboratorios/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── backend/
│   ├── api/              # Endpoints REST
│   ├── models/           # Modelos de datos
│   ├── services/         # Servicios (NLU, etc.)
│   └── utils/            # Utilidades
├── frontend/
│   ├── templates/        # Plantillas HTML (Jinja2)
│   └── static/           # CSS, JS, imágenes
├── database/
│   ├── schema.sql        # Esquema de BD
│   └── data.sql          # Datos de prueba
├── models/               # Modelos de IA
└── uploads/              # Archivos subidos
```

---

## 🛠️ Tecnologías

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos:** MySQL
- **IA:** TensorFlow, MobileNetV2, scikit-learn
- **Voz:** Vosk (reconocimiento), Web Speech API (síntesis)

---

## 📄 Licencia

Proyecto desarrollado para el SENA - Centro Minero de Sogamoso
