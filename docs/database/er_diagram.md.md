# 📊 Diagrama Entidad-Relación

## 🔗 Relaciones del Sistema GIL

```mermaid
erDiagram
    usuarios ||--o{ prestamos : "solicita"
    usuarios ||--o{ prestamos : "autoriza"
    usuarios ||--o{ laboratorios : "responsable"
    usuarios ||--o{ historial_mantenimiento : "tecnico_responsable"
    usuarios ||--o{ logs_sistema : "genera"
    usuarios ||--o{ logs_cambios : "registra"
    usuarios ||--o{ encuestas : "responde"
    
    roles ||--o{ usuarios : "tiene"
    
    equipos ||--o{ prestamos : "prestado_en"
    equipos ||--o{ historial_mantenimiento : "mantenido_en"
    equipos ||--o{ alertas_mantenimiento : "tiene_alertas"
    equipos ||--o{ reconocimientos_imagen : "detectado_en"
    equipos ||--o{ imagenes_entrenamiento : "entrenado_con"
    
    categorias_equipos ||--o{ equipos : "clasifica"
    
    laboratorios ||--o{ equipos : "contiene"
    laboratorios ||--o{ practicas_laboratorio : "utilizado_en"
    
    tipos_mantenimiento ||--o{ historial_mantenimiento : "tipo"
    
    programas_formacion ||--o{ practicas_laboratorio : "programa"
    
    instructores ||--o{ practicas_laboratorio : "instructor"
    usuarios ||--|| instructores : "es"
    
    modelos_ia ||--o{ reconocimientos_imagen : "usado_por"