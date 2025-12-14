# Modelos de IA - Sistema GIL

## Asistente de Voz LUCIA

### Modelo Vosk (Reconocimiento de Voz)

Para que el asistente de voz funcione correctamente, necesitas descargar el modelo de Vosk para español.

#### Pasos de instalación:

1. **Descargar el modelo:**
   - Ve a: https://alphacephei.com/vosk/models
   - Descarga: `vosk-model-small-es-0.42` (~39MB)
   - O el modelo completo: `vosk-model-es-0.42` (~1.4GB) para mayor precisión

2. **Extraer el modelo:**
   - Descomprime el archivo ZIP
   - Renombra la carpeta a `vosk-model-small-es`
   - Colócala en esta carpeta (`models/`)

3. **Estructura esperada:**
   ```
   models/
   ├── vosk-model-small-es/
   │   ├── am/
   │   ├── conf/
   │   ├── graph/
   │   ├── ivector/
   │   └── README
   └── nlu_model.joblib (se genera automáticamente)
   ```

### Modelo NLU (Clasificador de Intenciones)

El archivo `nlu_model.joblib` se genera automáticamente la primera vez que se inicia el sistema.
Contiene el clasificador entrenado con scikit-learn para identificar intenciones de voz.

## Dependencias requeridas

```bash
pip install vosk pyaudio pydub webrtcvad scikit-learn joblib
```

### Notas para Windows:
- PyAudio puede requerir instalación especial:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- O descargar el wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### Notas para pydub:
- Requiere FFmpeg instalado en el sistema
- Windows: Descargar de https://ffmpeg.org/download.html y agregar al PATH
- Linux: `sudo apt install ffmpeg`

## Verificar instalación

Ejecuta el siguiente comando para verificar que todo está instalado:

```python
python -c "import vosk; import pyaudio; import pydub; print('OK')"
```

## Endpoints de la API

- `GET /api/voz/status` - Estado del servicio
- `POST /api/voz/procesar-audio` - Procesar audio grabado
- `POST /api/voz/procesar-texto` - Procesar texto directamente
- `GET /api/voz/historial` - Historial de interacciones
- `GET /api/voz/estadisticas` - Estadísticas de uso
