

# 📊 Diagramas de Flujo del Sistema GIL

## Flujos de Procesos Principales

### 1. Flujo de Autenticación
```mermaid
graph TD
    A[Usuario accede al sistema] --> B{¿Sesión activa?}
    B -->|No| C[Mostrar formulario login]
    B -->|Sí| D[Redirigir a dashboard]
    C --> E[Ingresar credenciales]
    E --> F{¿Credenciales válidas?}
    F -->|No| G[Mostrar error]
    F -->|Sí| H[Generar token JWT]
    H --> I[Establecer sesión]
    I --> J[Redirigir a página solicitada]
    G --> E