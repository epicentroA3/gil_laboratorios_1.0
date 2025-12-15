# 🔐 Sistema de Recuperación de Contraseña - Instrucciones de Implementación

## ✅ Archivos Creados:

1. **`database/migrations/add_password_reset_table.sql`** - Tabla para tokens
2. **`app_password_reset_routes.py`** - Rutas backend (copiar a app.py)
3. **`frontend/templates/reset_password.html`** - Página de restablecimiento
4. **`frontend/templates/login.html`** - Actualizado con API real

---

## 📋 Pasos para Implementar:

### **1. Crear la Tabla en la Base de Datos**

Ejecuta el script SQL:

```bash
mysql -u root -p gil_laboratorios < database/migrations/add_password_reset_table.sql
```

O desde MySQL Workbench/phpMyAdmin, ejecuta el contenido del archivo.

---

### **2. Agregar las Rutas al Backend (app.py)**

Abre `app_password_reset_routes.py` y **copia todo el contenido** en `app.py` después de la ruta `/register` (línea ~335).

Las rutas a agregar son:
- `@app.route('/forgot-password', methods=['POST'])` - Solicitar reset
- `@app.route('/reset-password/<token>', methods=['GET', 'POST'])` - Cambiar contraseña

---

### **3. Verificar Dependencias**

Asegúrate de tener instalado:

```bash
pip install bcrypt
```

Ya debería estar instalado si el login funciona con contraseñas.

---

## 🔄 Flujo Completo:

### **Paso 1: Usuario Olvida su Contraseña**
1. Usuario hace click en "¿Olvidó su contraseña?" en el login
2. Se abre el modal
3. Ingresa su correo electrónico
4. Click en "Enviar Instrucciones"

### **Paso 2: Backend Procesa Solicitud**
1. Verifica que el email exista en la BD
2. Genera un token único y seguro (32 caracteres)
3. Guarda el token en `password_reset_tokens` con expiración de 1 hora
4. **TODO:** Envía email con el enlace (por ahora solo imprime en consola)
5. Responde con mensaje de éxito

### **Paso 3: Usuario Recibe Enlace**
- URL: `http://localhost:5000/reset-password/TOKEN_AQUI`
- En modo DEBUG, el enlace se muestra en el modal (solo desarrollo)
- En producción, se enviaría por email

### **Paso 4: Usuario Restablece Contraseña**
1. Hace click en el enlace recibido
2. Backend verifica que el token sea válido y no haya expirado
3. Muestra formulario para ingresar nueva contraseña
4. Usuario ingresa y confirma nueva contraseña
5. Backend hashea la contraseña con bcrypt
6. Actualiza `usuarios.password_hash`
7. Marca el token como usado
8. Redirige al login con mensaje de éxito

---

## 🔒 Seguridad Implementada:

✅ **Tokens únicos** generados con `secrets.token_urlsafe(32)`
✅ **Expiración** de 1 hora para los tokens
✅ **Uso único** - Token se marca como usado después del cambio
✅ **Validación de contraseña** - Mínimo 8 caracteres
✅ **Hasheo seguro** con bcrypt
✅ **Logs de seguridad** en `logs_sistema`
✅ **Registro de IP** en solicitudes
✅ **Respuesta genérica** - No revela si el email existe o no

---

## 📧 Configurar Envío de Emails (Opcional - Producción)

Para enviar emails reales, agrega en `app.py`:

```python
from flask_mail import Mail, Message

# Configuración
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'tu-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@centrominero.edu.co'

mail = Mail(app)

# En la función forgot_password(), reemplaza el TODO:
def enviar_email_reset(email, reset_url, nombre):
    msg = Message(
        'Restablecer Contraseña - Centro Minero SENA',
        recipients=[email]
    )
    msg.html = f'''
    <h2>Hola {nombre},</h2>
    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
    <p>Haz click en el siguiente enlace para continuar:</p>
    <p><a href="{reset_url}" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
    <p>Este enlace expirará en 1 hora.</p>
    <p>Si no solicitaste este cambio, ignora este correo.</p>
    <hr>
    <small>Centro Minero de Sogamoso - SENA</small>
    '''
    mail.send(msg)
```

---

## 🧪 Probar el Sistema:

### **Desarrollo (sin email):**

1. Inicia el servidor: `python app.py`
2. Ve a http://localhost:5000/login
3. Click en "¿Olvidó su contraseña?"
4. Ingresa un email registrado (ej: `admin@sena.edu.co`)
5. En la consola del servidor verás:
   ```
   === TOKEN DE RESTABLECIMIENTO ===
   Usuario: Roberto Díaz Silva
   Email: admin@sena.edu.co
   URL: http://localhost:5000/reset-password/TOKEN_AQUI
   Expira: 2024-12-15 08:00:00
   ================================
   ```
6. Copia la URL y ábrela en el navegador
7. Ingresa nueva contraseña
8. Inicia sesión con la nueva contraseña

### **Producción (con email):**

1. Configura Flask-Mail (ver sección anterior)
2. El usuario recibirá el enlace por email
3. Todo lo demás funciona igual

---

## 📊 Tabla `password_reset_tokens`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INT | ID autoincremental |
| `id_usuario` | INT | FK a usuarios |
| `token` | VARCHAR(255) | Token único |
| `email` | VARCHAR(255) | Email del usuario |
| `expira_en` | DATETIME | Fecha/hora de expiración |
| `usado` | BOOLEAN | Si ya se usó el token |
| `fecha_creacion` | TIMESTAMP | Cuándo se creó |
| `ip_solicitud` | VARCHAR(45) | IP desde donde se solicitó |

---

## ✨ Características:

- ✅ Modal integrado en el login
- ✅ Validación de email en frontend
- ✅ API REST para solicitar reset
- ✅ Tokens seguros con expiración
- ✅ Página dedicada para cambiar contraseña
- ✅ Indicador de fortaleza de contraseña
- ✅ Logs de seguridad
- ✅ Responsive y con Bootstrap 5
- ✅ Mensajes flash informativos
- ✅ Protección contra ataques de fuerza bruta

---

## 🐛 Solución de Problemas:

**Error: "Token inválido"**
- El token ya fue usado
- El token expiró (>1 hora)
- El token no existe en la BD

**Error: "Email no encontrado"**
- El email no está registrado en la BD
- El usuario está inactivo

**No recibo el email**
- Verifica configuración SMTP
- Revisa carpeta de spam
- Verifica que Flask-Mail esté instalado

---

## 🎯 Próximos Pasos:

1. ✅ Ejecutar el script SQL
2. ✅ Copiar rutas a app.py
3. ✅ Probar en desarrollo
4. ⏳ Configurar envío de emails (producción)
5. ⏳ Personalizar plantilla de email
6. ⏳ Agregar límite de intentos (rate limiting)

---

**¡Sistema de recuperación de contraseña listo para usar!** 🎉
