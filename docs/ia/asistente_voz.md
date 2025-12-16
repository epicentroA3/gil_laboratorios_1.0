
# 🎤 Asistente de Voz LUCIA - Sistema GIL

## 1. Introducción a LUCIA

### 1.1 ¿Qué es LUCIA?
**LUCIA** (Laboratory User Conversational Intelligent Assistant) es el asistente de voz inteligente integrado en el Sistema GIL. Permite la interacción natural con el sistema mediante comandos de voz, facilitando operaciones comunes sin necesidad de usar la interfaz gráfica.

### 1.2 Características Principales
- 🗣️ **Reconocimiento de voz en español**
- 🧠 **Procesamiento de lenguaje natural (NLP)**
- 🔄 **Integración completa con todos los módulos del sistema**
- 📱 **Disponible en web**


## 1.3 Arquitectura General
┌─────────────────────────────────────────────────────┐
│ Interfaz de Usuario │
│ Web: Micrófono en navegador │
└───────────────────────┬─────────────────────────────┘
│ Audio Stream
┌───────────────────────▼─────────────────────────────┐
│ Servicio de Reconocimiento de Voz │
│ • Web Speech API / SpeechRecognition │
│ 
└───────────────────────┬─────────────────────────────┘
│ Texto Transcrito
┌───────────────────────▼─────────────────────────────┐
│ Procesamiento de Lenguaje Natural │
│ • spaCy para español │
│ • Identificación de intenciones │
│ • Extracción de entidades │
└───────────────────────┬─────────────────────────────┘
│ Resultados de Acción
┌───────────────────────▼─────────────────────────────┐
│ Servicio de Síntesis de Voz │
│ • Web Speech API (navegador) │
│ • Responsiva en texto para leer │