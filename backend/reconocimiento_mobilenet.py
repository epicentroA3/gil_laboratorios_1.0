"""
MÓDULO DE RECONOCIMIENTO DE EQUIPOS CON MOBILENET
Centro Minero de Sogamoso - SENA

Sistema de IA para identificación automática de equipos de laboratorio
Basado en MobileNetV2 con transfer learning

Objetivo MGA: Precisión >85% en identificación de equipos
"""

import os
import json
import logging
import hashlib
import time
from datetime import datetime
import numpy as np

# Configurar logging
logger = logging.getLogger(__name__)

# Intentar importar dependencias de IA
try:
    import cv2
    CV2_DISPONIBLE = True
except ImportError:
    CV2_DISPONIBLE = False
    logger.warning("⚠️ OpenCV no disponible")

try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TF_DISPONIBLE = True
except ImportError:
    TF_DISPONIBLE = False
    logger.warning("⚠️ TensorFlow no disponible")

try:
    from PIL import Image
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False
    logger.warning("⚠️ Pillow no disponible")


# Configuración del modelo
MODELO_DIR = 'models/reconocimiento'
MODELO_PATH = os.path.join(MODELO_DIR, 'mobilenet_equipos.h5')
CLASES_PATH = os.path.join(MODELO_DIR, 'clases_equipos.json')
CONFIG_PATH = os.path.join(MODELO_DIR, 'config_modelo.json')

# Parámetros de imagen
IMG_SIZE = (224, 224)
UMBRAL_CONFIANZA = 0.85  # 85% según objetivo MGA


def validar_calidad_imagen(ruta_imagen):
    """
    Valida la calidad de una imagen para entrenamiento/identificación
    
    Returns:
        dict: {valida: bool, calidad: float, razon: str}
    """
    try:
        if not CV2_DISPONIBLE:
            return {'valida': True, 'calidad': 0.7, 'razon': 'OpenCV no disponible, validación omitida'}
        
        img = cv2.imread(ruta_imagen)
        if img is None:
            return {'valida': False, 'calidad': 0, 'razon': 'No se pudo leer la imagen'}
        
        h, w = img.shape[:2]
        
        # Verificar resolución mínima (224x224 para MobileNet)
        if h < 224 or w < 224:
            return {'valida': False, 'calidad': 0.3, 'razon': f'Resolución muy baja: {w}x{h}'}
        
        # Calcular nitidez (Laplacian variance)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calcular brillo promedio
        brillo = np.mean(gray)
        
        # Calcular contraste
        contraste = np.std(gray)
        
        # Evaluar calidad
        calidad = 0.0
        razones = []
        
        # Nitidez (peso: 40%)
        if laplacian_var > 100:
            calidad += 0.4
        elif laplacian_var > 50:
            calidad += 0.25
            razones.append('Imagen ligeramente borrosa')
        else:
            calidad += 0.1
            razones.append('Imagen muy borrosa')
        
        # Brillo (peso: 30%)
        if 50 < brillo < 200:
            calidad += 0.3
        elif 30 < brillo < 220:
            calidad += 0.2
            razones.append('Brillo no óptimo')
        else:
            calidad += 0.1
            razones.append('Imagen muy oscura o muy clara')
        
        # Contraste (peso: 30%)
        if contraste > 40:
            calidad += 0.3
        elif contraste > 25:
            calidad += 0.2
            razones.append('Bajo contraste')
        else:
            calidad += 0.1
            razones.append('Muy bajo contraste')
        
        # Resolución bonus
        if h >= 640 and w >= 640:
            calidad = min(1.0, calidad + 0.1)
        
        valida = calidad >= 0.6  # Mínimo 60% de calidad
        
        return {
            'valida': valida,
            'calidad': round(calidad, 2),
            'razon': '; '.join(razones) if razones else 'Imagen de buena calidad',
            'metricas': {
                'resolucion': f'{w}x{h}',
                'nitidez': round(laplacian_var, 2),
                'brillo': round(brillo, 2),
                'contraste': round(contraste, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error validando imagen: {e}")
        return {'valida': False, 'calidad': 0, 'razon': str(e)}


def calcular_hash_imagen(ruta_imagen):
    """Calcula hash MD5 de una imagen para detectar duplicados"""
    try:
        with open(ruta_imagen, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculando hash: {e}")
        return None


class ReconocimientoMobileNet:
    """
    Sistema de reconocimiento de equipos basado en MobileNetV2
    
    Características:
    - Transfer learning desde ImageNet
    - Fine-tuning para equipos de laboratorio
    - Umbral de confianza configurable (default 85%)
    - Soporte para múltiples categorías de equipos
    """
    
    def __init__(self, umbral_confianza=UMBRAL_CONFIANZA):
        self.umbral_confianza = umbral_confianza
        self.modelo = None
        self.clases = {}
        self.num_clases = 0
        self.modelo_cargado = False
        self.estadisticas = {
            'total_identificaciones': 0,
            'identificaciones_exitosas': 0,
            'precision_promedio': 0.0,
            'tiempo_promedio_ms': 0.0
        }
        
        # Parámetros de entrenamiento
        self.EPOCHS = 10
        self.BATCH_SIZE = 32
        self.LEARNING_RATE = 0.0001
        
        # Crear directorio de modelos
        os.makedirs(MODELO_DIR, exist_ok=True)
        
        logger.info("🤖 Sistema de Reconocimiento MobileNet inicializado")
    
    def _crear_modelo_base(self, num_clases):
        """Crea el modelo base MobileNetV2 con capas personalizadas"""
        if not TF_DISPONIBLE:
            raise ImportError("TensorFlow no está instalado")
        
        # Cargar MobileNetV2 preentrenado (sin capas superiores)
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Congelar capas base inicialmente
        for layer in base_model.layers:
            layer.trainable = False
        
        # Agregar capas personalizadas
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.3)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.2)(x)
        predictions = Dense(num_clases, activation='softmax')(x)
        
        # Crear modelo final
        modelo = Model(inputs=base_model.input, outputs=predictions)
        
        # Compilar
        modelo.compile(
            optimizer=Adam(learning_rate=self.LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"✅ Modelo creado con {num_clases} clases")
        return modelo
    
    def _preparar_imagen(self, imagen_path_o_array):
        """Prepara una imagen para el modelo"""
        if isinstance(imagen_path_o_array, str):
            # Es una ruta
            if PIL_DISPONIBLE:
                img = Image.open(imagen_path_o_array)
                img = img.resize(IMG_SIZE)
                img_array = np.array(img)
            elif CV2_DISPONIBLE:
                img = cv2.imread(imagen_path_o_array)
                img = cv2.resize(img, IMG_SIZE)
                img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                raise ImportError("Ni PIL ni OpenCV están disponibles")
        else:
            # Es un array numpy (de OpenCV)
            if CV2_DISPONIBLE:
                img = cv2.resize(imagen_path_o_array, IMG_SIZE)
                img_array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                img_array = imagen_path_o_array
        
        # Expandir dimensiones y preprocesar
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array.astype('float32'))
        
        return img_array
    
    def entrenar_modelo(self, equipos_data, validation_split=0.2):
        """
        Entrena el modelo con los equipos proporcionados
        
        Args:
            equipos_data: Lista de dicts con {codigo_equipo, nombre_objeto, categoria_entrenamiento, rutas_imagenes}
            validation_split: Proporción de datos para validación
            
        Returns:
            dict: Métricas de entrenamiento
        """
        if not TF_DISPONIBLE:
            raise ImportError("TensorFlow no está instalado. Ejecute: pip install tensorflow")
        
        logger.info(f"🎓 Iniciando entrenamiento con {len(equipos_data)} equipos...")
        
        # Preparar datos
        imagenes = []
        etiquetas = []
        self.clases = {}
        
        for idx, equipo in enumerate(equipos_data):
            codigo = equipo['codigo_equipo']
            nombre = equipo['nombre_objeto']
            rutas = json.loads(equipo['rutas_imagenes']) if isinstance(equipo['rutas_imagenes'], str) else equipo['rutas_imagenes']
            
            self.clases[idx] = {
                'codigo': codigo,
                'nombre': nombre,
                'categoria': equipo.get('categoria_entrenamiento', 'General')
            }
            
            for ruta in rutas:
                if os.path.exists(ruta):
                    try:
                        img_array = self._preparar_imagen(ruta)
                        imagenes.append(img_array[0])  # Quitar dimensión batch
                        etiquetas.append(idx)
                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando {ruta}: {e}")
        
        if len(imagenes) < 5:
            raise ValueError(f"Insuficientes imágenes para entrenamiento: {len(imagenes)}. Se requieren mínimo 5.")
        
        self.num_clases = len(self.clases)
        
        # Convertir a arrays numpy
        X = np.array(imagenes)
        y_labels = np.array(etiquetas)
        
        logger.info(f"📊 Dataset original: {len(X)} imágenes, {self.num_clases} clases")
        
        # Aplicar Data Augmentation para generar más variaciones
        X_augmented, y_augmented = self._aplicar_data_augmentation(X, y_labels)
        
        # Convertir etiquetas a one-hot
        y = tf.keras.utils.to_categorical(y_augmented, num_classes=self.num_clases)
        
        logger.info(f"📊 Dataset aumentado: {len(X_augmented)} imágenes, {self.num_clases} clases")
        
        # Crear modelo
        self.modelo = self._crear_modelo_base(self.num_clases)
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            ModelCheckpoint(MODELO_PATH, monitor='val_accuracy', save_best_only=True)
        ]
        
        # Entrenar con más épocas para mejor convergencia
        history = self.modelo.fit(
            X_augmented, y,
            epochs=self.EPOCHS,
            batch_size=self.BATCH_SIZE,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        # Guardar clases y configuración
        with open(CLASES_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.clases, f, ensure_ascii=False, indent=2)
        
        config = {
            'num_clases': self.num_clases,
            'umbral_confianza': self.umbral_confianza,
            'fecha_entrenamiento': datetime.now().isoformat(),
            'epochs': self.EPOCHS,
            'total_imagenes': len(X)
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Guardar características de referencia para validación de similitud
        self._guardar_caracteristicas_referencia(equipos_data)
        
        # Métricas finales
        train_acc = history.history['accuracy'][-1]
        val_acc = history.history['val_accuracy'][-1]
        
        self.modelo_cargado = True
        
        metricas = {
            'train_accuracy': train_acc,
            'val_accuracy': val_acc,
            'num_clases': self.num_clases,
            'total_imagenes': len(X),
            'objetivo_alcanzado': val_acc >= 0.85
        }
        
        logger.info(f"✅ Entrenamiento completado: Precisión={val_acc*100:.2f}%")
        
        return metricas
    
    def _calcular_histograma(self, img):
        """Calcula histograma de color normalizado"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist.flatten()
    
    def _guardar_caracteristicas_referencia(self, equipos_data):
        """Guarda características de referencia de las imágenes de entrenamiento"""
        try:
            histogramas = []
            
            for equipo in equipos_data:
                rutas = json.loads(equipo['rutas_imagenes']) if isinstance(equipo['rutas_imagenes'], str) else equipo['rutas_imagenes']
                
                for ruta in rutas[:3]:  # Máximo 3 imágenes por equipo
                    if os.path.exists(ruta):
                        img = cv2.imread(ruta)
                        if img is not None:
                            img_resized = cv2.resize(img, (224, 224))
                            hist = self._calcular_histograma(img_resized)
                            histogramas.append(hist.tolist())
            
            ref_data = {
                'histogramas': histogramas,
                'fecha': datetime.now().isoformat(),
                'num_equipos': len(equipos_data)
            }
            
            ref_path = os.path.join(MODELO_DIR, 'caracteristicas_referencia.json')
            with open(ref_path, 'w') as f:
                json.dump(ref_data, f)
            
            logger.info(f"✅ Guardadas {len(histogramas)} características de referencia")
            
        except Exception as e:
            logger.warning(f"⚠️ Error guardando características de referencia: {e}")
    
    def _aplicar_data_augmentation(self, X, y):
        """
        Aplica Data Augmentation para generar más variaciones de las imágenes.
        Esto mejora significativamente la precisión del modelo.
        """
        X_augmented = list(X)
        y_augmented = list(y)
        
        # Número de augmentaciones por imagen
        num_augmentaciones = 4
        
        for i, img in enumerate(X):
            etiqueta = y[i]
            
            for _ in range(num_augmentaciones):
                img_aug = img.copy()
                
                # Aplicar transformaciones aleatorias
                # 1. Flip horizontal (50% probabilidad)
                if np.random.random() > 0.5:
                    img_aug = np.fliplr(img_aug)
                
                # 2. Rotación pequeña (-15 a +15 grados)
                if np.random.random() > 0.3:
                    angle = np.random.uniform(-15, 15)
                    img_aug = self._rotar_imagen(img_aug, angle)
                
                # 3. Ajuste de brillo (-20% a +20%)
                if np.random.random() > 0.3:
                    factor = np.random.uniform(0.8, 1.2)
                    img_aug = np.clip(img_aug * factor, -1, 1)
                
                # 4. Zoom aleatorio (90% a 110%)
                if np.random.random() > 0.5:
                    zoom = np.random.uniform(0.9, 1.1)
                    img_aug = self._zoom_imagen(img_aug, zoom)
                
                # 5. Ruido gaussiano pequeño
                if np.random.random() > 0.7:
                    noise = np.random.normal(0, 0.02, img_aug.shape)
                    img_aug = np.clip(img_aug + noise, -1, 1)
                
                X_augmented.append(img_aug)
                y_augmented.append(etiqueta)
        
        # Mezclar datos
        indices = np.random.permutation(len(X_augmented))
        X_augmented = np.array(X_augmented)[indices]
        y_augmented = np.array(y_augmented)[indices]
        
        return X_augmented, y_augmented
    
    def _rotar_imagen(self, img, angle):
        """Rota una imagen por un ángulo dado"""
        try:
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            # Crear matriz de rotación
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            # Aplicar rotación
            rotated = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
            return rotated
        except:
            return img
    
    def _zoom_imagen(self, img, zoom_factor):
        """Aplica zoom a una imagen"""
        try:
            h, w = img.shape[:2]
            # Calcular nuevo tamaño
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            
            if zoom_factor > 1:
                # Zoom in: recortar centro
                resized = cv2.resize(img, (new_w, new_h))
                start_h = (new_h - h) // 2
                start_w = (new_w - w) // 2
                return resized[start_h:start_h+h, start_w:start_w+w]
            else:
                # Zoom out: agregar padding
                resized = cv2.resize(img, (new_w, new_h))
                pad_h = (h - new_h) // 2
                pad_w = (w - new_w) // 2
                padded = np.zeros_like(img)
                padded[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
                return padded
        except:
            return img
    
    def cargar_modelo(self):
        """Carga un modelo previamente entrenado"""
        if not TF_DISPONIBLE:
            raise ImportError("TensorFlow no está instalado")
        
        if not os.path.exists(MODELO_PATH):
            raise FileNotFoundError(f"No existe modelo en {MODELO_PATH}")
        
        self.modelo = load_model(MODELO_PATH)
        
        with open(CLASES_PATH, 'r', encoding='utf-8') as f:
            self.clases = json.load(f)
        
        # Convertir keys a int
        self.clases = {int(k): v for k, v in self.clases.items()}
        self.num_clases = len(self.clases)
        
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                self.umbral_confianza = config.get('umbral_confianza', UMBRAL_CONFIANZA)
        
        self.modelo_cargado = True
        logger.info(f"✅ Modelo cargado: {self.num_clases} clases")
    
    def identificar_equipo(self, imagen_path, top_n=3):
        """
        Identifica un equipo a partir de una imagen
        
        Args:
            imagen_path: Ruta a la imagen
            top_n: Número de resultados a retornar
            
        Returns:
            tuple: (resultados, tiempo_ms)
        """
        return self._identificar(imagen_path, top_n)
    
    def identificar_equipo_cv2(self, imagen_cv2, top_n=3):
        """
        Identifica un equipo a partir de un array de OpenCV
        
        Args:
            imagen_cv2: Array numpy de OpenCV (BGR)
            top_n: Número de resultados a retornar
            
        Returns:
            tuple: (resultados, tiempo_ms)
        """
        return self._identificar(imagen_cv2, top_n)
    
    def _identificar(self, imagen, top_n=3):
        """Método interno de identificación"""
        if not self.modelo_cargado:
            # Intentar cargar modelo
            try:
                self.cargar_modelo()
            except FileNotFoundError:
                return [], 0
        
        inicio = time.time()
        
        try:
            # Preparar imagen
            img_array = self._preparar_imagen(imagen)
            
            # Predecir
            predicciones = self.modelo.predict(img_array, verbose=0)[0]
            
            # Obtener top N
            indices_top = np.argsort(predicciones)[-top_n:][::-1]
            
            # Calcular entropía de las predicciones para detectar incertidumbre
            # Si solo hay 1 clase, usar análisis de características adicional
            entropia = -np.sum(predicciones * np.log(predicciones + 1e-10))
            max_entropia = np.log(len(predicciones)) if len(predicciones) > 1 else 1
            incertidumbre = entropia / max_entropia if max_entropia > 0 else 0
            
            # Aplicar penalización basada en características siempre que haya pocas clases
            # Esto ayuda a evitar falsos positivos cuando el modelo tiene pocas clases
            penalizacion = 1.0
            if self.num_clases <= 5:
                # Con pocas clases, el modelo tiende a clasificar cualquier imagen
                # Aplicar análisis de características para penalizar imágenes muy diferentes
                penalizacion = self._calcular_similitud_caracteristicas(imagen)
                logger.info(f"🔍 {self.num_clases} clase(s) - Penalización por similitud: {penalizacion:.2f}")
            
            resultados = []
            for idx in indices_top:
                confianza_raw = float(predicciones[idx])
                # Aplicar penalización si hay pocas clases
                confianza = confianza_raw * penalizacion
                
                clase_info = self.clases.get(idx, {'codigo': 'DESCONOCIDO', 'nombre': 'Desconocido', 'categoria': 'N/A'})
                
                resultados.append({
                    'codigo_equipo': clase_info['codigo'],
                    'nombre_objeto': clase_info['nombre'],
                    'categoria': clase_info['categoria'],
                    'confianza': confianza,
                    'confianza_porcentaje': f"{confianza * 100:.1f}%",
                    'exitoso': confianza >= self.umbral_confianza
                })
            
            tiempo_ms = (time.time() - inicio) * 1000
            
            # Actualizar estadísticas
            self.estadisticas['total_identificaciones'] += 1
            if resultados and resultados[0]['exitoso']:
                self.estadisticas['identificaciones_exitosas'] += 1
            
            return resultados, tiempo_ms
            
        except Exception as e:
            logger.error(f"❌ Error en identificación: {e}")
            return [], 0
    
    def _calcular_similitud_caracteristicas(self, imagen):
        """
        Calcula similitud basada en características de imagen
        para validar cuando hay pocas clases.
        Usa múltiples métricas para mayor precisión.
        """
        try:
            # Preparar imagen para análisis
            if isinstance(imagen, str):
                img = cv2.imread(imagen)
            else:
                img = imagen
            
            if img is None:
                return 0.3  # Penalización alta si no se puede leer
            
            # Redimensionar para análisis
            img_resized = cv2.resize(img, (224, 224))
            
            # Cargar características de referencia si existen
            ref_path = os.path.join(MODELO_DIR, 'caracteristicas_referencia.json')
            if os.path.exists(ref_path):
                with open(ref_path, 'r') as f:
                    ref_data = json.load(f)
                
                # Calcular histograma de color de la imagen actual
                hist_actual = self._calcular_histograma(img_resized)
                
                # Comparar con histogramas de referencia usando múltiples métodos
                similitudes_correl = []
                similitudes_chi = []
                similitudes_intersect = []
                
                for ref_hist in ref_data.get('histogramas', []):
                    ref_hist_array = np.array(ref_hist, dtype=np.float32)
                    hist_actual_f32 = hist_actual.astype(np.float32)
                    
                    # Correlación (1 = idéntico, -1 = opuesto)
                    correl = cv2.compareHist(hist_actual_f32, ref_hist_array, cv2.HISTCMP_CORREL)
                    similitudes_correl.append(max(0, correl))
                    
                    # Chi-cuadrado (0 = idéntico, mayor = diferente)
                    chi = cv2.compareHist(hist_actual_f32, ref_hist_array, cv2.HISTCMP_CHISQR)
                    # Convertir a similitud (normalizar inversamente)
                    chi_sim = 1.0 / (1.0 + chi)
                    similitudes_chi.append(chi_sim)
                    
                    # Intersección (mayor = más similar)
                    intersect = cv2.compareHist(hist_actual_f32, ref_hist_array, cv2.HISTCMP_INTERSECT)
                    similitudes_intersect.append(min(1.0, intersect))
                
                if similitudes_correl:
                    # Combinar las mejores similitudes de cada método
                    mejor_correl = max(similitudes_correl)
                    mejor_chi = max(similitudes_chi)
                    mejor_intersect = max(similitudes_intersect)
                    
                    # Promedio ponderado de las métricas
                    # Correlación es más importante para detectar similitud visual
                    similitud_combinada = (mejor_correl * 0.5 + mejor_chi * 0.3 + mejor_intersect * 0.2)
                    
                    logger.info(f"📊 Similitud - Correl: {mejor_correl:.3f}, Chi: {mejor_chi:.3f}, Intersect: {mejor_intersect:.3f} -> Combinada: {similitud_combinada:.3f}")
                    
                    # Aplicar umbral más estricto
                    # Si la similitud combinada es baja, penalizar fuertemente
                    if similitud_combinada < 0.3:
                        return 0.1  # Muy diferente - penalización muy alta
                    elif similitud_combinada < 0.5:
                        return 0.3  # Diferente - penalización alta
                    elif similitud_combinada < 0.7:
                        return 0.6  # Algo similar - penalización moderada
                    else:
                        return min(1.0, similitud_combinada)  # Similar - poca o ninguna penalización
            
            # Si no hay referencia, aplicar penalización alta
            return 0.4
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculando similitud: {e}")
            return 0.4
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del sistema"""
        tasa_exito = 0
        if self.estadisticas['total_identificaciones'] > 0:
            tasa_exito = (self.estadisticas['identificaciones_exitosas'] / 
                         self.estadisticas['total_identificaciones']) * 100
        
        return {
            'modelo_cargado': self.modelo_cargado,
            'num_clases': self.num_clases,
            'umbral_confianza': f"{self.umbral_confianza * 100}%",
            'total_identificaciones': self.estadisticas['total_identificaciones'],
            'identificaciones_exitosas': self.estadisticas['identificaciones_exitosas'],
            'tasa_exito': f"{tasa_exito:.1f}%"
        }


class ReconocimientoSimple:
    """
    Sistema de reconocimiento simplificado usando características de imagen
    Para usar cuando TensorFlow no está disponible
    """
    
    def __init__(self, umbral_confianza=0.85):
        self.umbral_confianza = umbral_confianza
        self.equipos_registrados = {}
        self.caracteristicas_db = {}
        
    def registrar_equipo(self, codigo, nombre, imagen_path):
        """Registra un equipo con sus características"""
        if not CV2_DISPONIBLE:
            return False
        
        try:
            img = cv2.imread(imagen_path)
            if img is None:
                return False
            
            # Extraer características básicas
            caracteristicas = self._extraer_caracteristicas(img)
            
            self.equipos_registrados[codigo] = {
                'nombre': nombre,
                'caracteristicas': caracteristicas
            }
            
            return True
        except Exception as e:
            logger.error(f"Error registrando equipo: {e}")
            return False
    
    def _extraer_caracteristicas(self, img):
        """Extrae características básicas de una imagen"""
        # Histograma de color
        hist_b = cv2.calcHist([img], [0], None, [32], [0, 256]).flatten()
        hist_g = cv2.calcHist([img], [1], None, [32], [0, 256]).flatten()
        hist_r = cv2.calcHist([img], [2], None, [32], [0, 256]).flatten()
        
        # Normalizar
        hist_b = hist_b / hist_b.sum()
        hist_g = hist_g / hist_g.sum()
        hist_r = hist_r / hist_r.sum()
        
        # Características de forma (bordes)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'hist_color': np.concatenate([hist_b, hist_g, hist_r]),
            'edge_density': edge_density
        }
    
    def identificar(self, imagen_cv2, top_n=3):
        """Identifica un equipo por similitud de características"""
        if not self.equipos_registrados:
            return [], 0
        
        inicio = time.time()
        
        try:
            caracteristicas = self._extraer_caracteristicas(imagen_cv2)
            
            similitudes = []
            for codigo, info in self.equipos_registrados.items():
                # Comparar histogramas
                hist_sim = 1 - np.sum(np.abs(
                    caracteristicas['hist_color'] - info['caracteristicas']['hist_color']
                )) / 2
                
                # Comparar densidad de bordes
                edge_sim = 1 - abs(
                    caracteristicas['edge_density'] - info['caracteristicas']['edge_density']
                )
                
                # Similitud combinada
                similitud = 0.7 * hist_sim + 0.3 * edge_sim
                
                similitudes.append({
                    'codigo_equipo': codigo,
                    'nombre_objeto': info['nombre'],
                    'confianza': similitud,
                    'confianza_porcentaje': f"{similitud * 100:.1f}%",
                    'exitoso': similitud >= self.umbral_confianza
                })
            
            # Ordenar por similitud
            similitudes.sort(key=lambda x: x['confianza'], reverse=True)
            
            tiempo_ms = (time.time() - inicio) * 1000
            
            return similitudes[:top_n], tiempo_ms
            
        except Exception as e:
            logger.error(f"Error en identificación simple: {e}")
            return [], 0
