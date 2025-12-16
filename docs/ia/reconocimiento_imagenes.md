# 🖼️ Sistema de Reconocimiento de Imágenes - GIL

## 1. Introducción

### 1.1 ¿Qué es el Reconocimiento de Imágenes en GIL?
El Sistema de Reconocimiento de Imágenes del GIL utiliza inteligencia artificial para identificar automáticamente equipos de laboratorio a partir de fotografías. Este sistema permite:

- 🔍 Identificar equipos rápidamente
- 📊 Actualizar inventario automáticamente
- ⚠️ Detectar cambios en el estado físico
- 📈 Analizar patrones de uso

### 1.2 Tecnologías Utilizadas
- **Modelo Base**: MobileNet V2 (pretrained on ImageNet)
- **Framework**: TensorFlow 2.x / Keras
- **Procesamiento de Imágenes**: OpenCV 4.x
- **Backend**: Flask con endpoints específicos
- **Base de Datos**: MySQL para almacenar modelos y resultados

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Componentes
┌─────────────────────────────────────────────────────────┐
│ Frontend (Web/App) │
│ • Captura de imagen (cámara/upload) │
│ • Previsualización │
│ • Mostrar resultados │
└───────────────────────┬─────────────────────────────────┘

┌───────────────────────▼─────────────────────────────────┐
│ Servicio de Reconocimiento │
│ • Preprocesamiento de imágenes │
│ • Carga de modelos │
│ • Inferencia (predicción) │
│ • Post-procesamiento │
└───────────────────────┬─────────────────────────────────┘
│
┌───────────────────────▼─────────────────────────────────┐
│ Base de Datos y Almacenamiento │
│ • MySQL: Resultados, metadatos │
│ • Sistema de archivos: Imágenes, modelos │
│ 
└─────────────────────────────────────────────────────────┘

text

### 2.2 Flujo de Procesamiento
📸 Captura de imagen (224x224 RGB)

🔄 Preprocesamiento (normalización, aumento)

🧠 Inferencia del modelo (MobileNet V2)

📊 Post-procesamiento (softmax, umbrales)

💾 Almacenamiento de resultados

📤 Respuesta al usuario

text

#