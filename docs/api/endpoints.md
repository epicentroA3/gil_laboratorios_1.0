
# 🔌 API REST - Documentación de Endpoints Basicos

## 🌐 Información General
- **URL Base:** `http://localhost:5000`
- **Formato:** JSON (UTF-8)
- **Autenticación:** JWT Bearer Token

## 📋 Índice de Endpoints

### 🔐 Autenticación
| Método | Endpoint | Descripción | Nivel Requerido |
|--------|----------|-------------|-----------------|
| POST | `/auth/login` | Autenticación de usuario | Público |
| GET | `/auth/verify` | Verifica token JWT | Usuario |
| POST | `/auth/logout` | Cierra sesión | Usuario |
| GET | `/auth/me` | Info usuario actual | Usuario |
| POST | `/auth/register` | Registro nuevo usuario | Público |

### 🔧 Equipos
| Método | Endpoint | Descripción | Nivel Requerido |
|--------|----------|-------------|-----------------|
| GET | `/equipos` | Lista equipos | 1+ |
| GET | `/equipos/{id}` | Detalle de equipo | 1+ |
| GET | `/equipos/disponibles` | Equipos disponibles | 1+ |
| POST | `/equipos` | Crear equipo | 3+ |
| PUT | `/equipos/{id}` | Actualizar equipo | 3+ |
| DELETE | `/equipos/{id}` | Eliminar equipo | 5+ |

### 📦 Préstamos
| Método | Endpoint | Descripción | Nivel Requerido |
|--------|----------|-------------|-----------------|
| GET | `/prestamos` | Lista préstamos | 1+ |
| POST | `/prestamos` | Solicitar préstamo | 2+ |
| POST | `/prestamos/{id}/aprobar` | Aprobar préstamo | 3+ |
| POST | `/prestamos/{id}/devolver` | Registrar devolución | 2+ |

## 📝 Ejemplos de Uso

### 1. Autenticación
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123456789", "password": "P@ssw0rd123!"}'
2. Obtener Equipos
bash
curl -X GET http://localhost:5000/equipos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
3. Solicitar Préstamo
bash
curl -X POST http://localhost:5000/prestamos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id_equipo": 1,
    "proposito": "Práctica de laboratorio",
    "fecha_devolucion_programada": "2024-01-22T17:00:00"
  }'
🔐 Códigos de Estado HTTP
Código	Descripción	Ejemplo
200	OK	Operación exitosa
201	Created	Recurso creado
400	Bad Request	Datos inválidos
401	Unauthorized	No autenticado
403	Forbidden	Sin permisos
404	Not Found	Recurso no existe
500	Internal Server Error	Error del servidor
📊 Estructura de Respuestas
json
{
  "success": true,
  "message": "Operación exitosa",
  "data": {},
  "errors": [],
  "metadata": {
    "total": 1,
    "page": 1,
    "per_page": 20
  }
}
🧪 Pruebas con Swagger UI
Accede a la documentación interactiva en:

text
http://localhost:5000/api/docs
Para generar la especificación OpenAPI:

bash
# Generar archivo YAML
python generate_openapi.py > doc/api/openapi.yaml

# Generar archivo JSON
python generate_openapi.py --format json > doc/api/openapi.json
🔗 Recursos Adicionales
Especificación OpenAPI

Colección Postman

Ejemplos de código