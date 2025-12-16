"""
Servicio de Mantenimiento Predictivo con IA
Precisión objetivo: >80%
Utiliza Random Forest para predecir fallas en equipos
"""
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime, timedelta
import os


class MantenimientoPredictivo:
    """
    Clase principal para el sistema de mantenimiento predictivo.
    Entrena modelos de ML para predecir fallas en equipos.
    """
    
    def __init__(self, db):
        self.db = db
        self.modelo = None
        self.scaler = StandardScaler()
        self.modelo_path = 'models/mantenimiento/modelo_predictivo.joblib'
        self.scaler_path = 'models/mantenimiento/scaler.joblib'
        self.precision_minima = 0.80  # 80% requerido
        self.feature_names = [
            'dias_antiguedad',
            'vida_util_dias', 
            'valor',
            'total_mantenimientos',
            'costo_promedio',
            'inactividad_promedio',
            'dias_sin_mantenimiento',
            'estado_numerico',
            'total_prestamos',
            'id_categoria'
        ]
        
    def obtener_datos_entrenamiento(self):
        """
        Extrae datos históricos para entrenar el modelo.
        Features: días desde último mant., antigüedad, uso, tipo equipo, etc.
        Target: 1 = falló antes de lo esperado, 0 = no falló
        """
        query = """
            SELECT 
                e.id as equipo_id,
                COALESCE(e.id_categoria, 1) as id_categoria,
                COALESCE(DATEDIFF(CURDATE(), e.fecha_adquisicion), 365) as dias_antiguedad,
                COALESCE(e.vida_util_anos, 5) * 365 as vida_util_dias,
                COALESCE(e.valor_adquisicion, 0) as valor,
                
                -- Historial de mantenimientos (incluir solo completados)
                COUNT(hm.id) as total_mantenimientos,
                COALESCE(AVG(hm.costo_mantenimiento), 0) as costo_promedio,
                COALESCE(AVG(hm.tiempo_inactividad_horas), 0) as inactividad_promedio,
                
                -- Días desde último mantenimiento (usar fecha_fin en lugar de fecha_mantenimiento)
                COALESCE(DATEDIFF(CURDATE(), MAX(hm.fecha_fin)), 30) as dias_sin_mantenimiento,
                
                -- Estado actual
                CASE e.estado_fisico 
                    WHEN 'excelente' THEN 4
                    WHEN 'bueno' THEN 3
                    WHEN 'regular' THEN 2
                    WHEN 'malo' THEN 1
                    ELSE 3
                END as estado_numerico,
                
                -- Préstamos (uso del equipo)
                (SELECT COUNT(*) FROM prestamos p WHERE p.id_equipo = e.id) as total_prestamos,
                
                -- Target: ¿Tuvo mantenimiento correctivo (no preventivo)?
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM historial_mantenimiento hm2
                        JOIN tipos_mantenimiento tm ON hm2.id_tipo_mantenimiento = tm.id
                        WHERE hm2.id_equipo = e.id 
                        AND tm.es_preventivo = 0
                        AND hm2.estado = 'completado'
                    ) THEN 1
                    ELSE 0
                END as tuvo_falla
                
            FROM equipos e
            LEFT JOIN historial_mantenimiento hm ON e.id = hm.id_equipo AND hm.estado = 'completado'
            WHERE e.estado != 'dado_baja'
            GROUP BY e.id, e.id_categoria, e.fecha_adquisicion, e.vida_util_anos, 
                    e.valor_adquisicion, e.estado_fisico
            HAVING total_mantenimientos > 0 OR total_prestamos > 0 OR e.estado_fisico IN ('malo', 'regular')
        """
        return self.db.ejecutar_query(query) or []
    
    def preparar_features(self, datos):
        """Prepara las características para el modelo"""
        X = []
        y = []
        
        for d in datos:
            features = [
                float(d['dias_antiguedad'] or 365),
                float(d['vida_util_dias'] or 1825),
                float(d['valor'] or 0),
                float(d['total_mantenimientos'] or 0),
                float(d['costo_promedio'] or 0),
                float(d['inactividad_promedio'] or 0),
                float(d['dias_sin_mantenimiento'] or 30),
                float(d['estado_numerico'] or 3),
                float(d['total_prestamos'] or 0),
                float(d['id_categoria'] or 1)
            ]
            X.append(features)
            y.append(int(d['tuvo_falla']))
        
        return np.array(X), np.array(y)
    
    def generar_datos_sinteticos(self, X, y, n_samples=50):
        """
        Genera datos sintéticos para aumentar el dataset cuando hay pocos datos.
        Usa técnica de perturbación con ruido gaussiano.
        """
        X_sintetico = []
        y_sintetico = []
        
        for _ in range(n_samples):
            idx = np.random.randint(0, len(X))
            muestra = X[idx].copy()
            # Agregar ruido gaussiano (5-10% de variación)
            ruido = np.random.normal(0, 0.05, len(muestra))
            muestra_perturbada = muestra * (1 + ruido)
            # Asegurar valores no negativos
            muestra_perturbada = np.maximum(muestra_perturbada, 0)
            X_sintetico.append(muestra_perturbada)
            y_sintetico.append(y[idx])
        
        return np.array(X_sintetico), np.array(y_sintetico)
    
    def entrenar_modelo(self):
        """
        Entrena el modelo de predicción.
        Retorna métricas de precisión.
        """
        print("🤖 Iniciando entrenamiento del modelo predictivo...")
        datos = self.obtener_datos_entrenamiento()
        
        if len(datos) < 5:
            return {
                'success': False,
                'error': f'Datos insuficientes. Necesitas al menos 5 registros con historial, tienes {len(datos)}',
                'registros_actuales': len(datos),
                'sugerencia': 'Registra más mantenimientos en el sistema para entrenar el modelo'
            }
        
        X, y = self.preparar_features(datos)
        
        # Si hay pocos datos, generar sintéticos
        if len(X) < 20:
            print(f"📊 Generando datos sintéticos (datos originales: {len(X)})")
            X_sint, y_sint = self.generar_datos_sinteticos(X, y, n_samples=max(50 - len(X), 20))
            X = np.vstack([X, X_sint])
            y = np.concatenate([y, y_sint])
        
        # Normalizar datos
        X_scaled = self.scaler.fit_transform(X)
        
        # Dividir en entrenamiento y prueba
        test_size = 0.2 if len(X) >= 10 else 0.1
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Entrenar modelo Random Forest
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            class_weight='balanced'
        )
        self.modelo.fit(X_train, y_train)
        
        # Evaluar
        y_pred = self.modelo.predict(X_test)
        precision = accuracy_score(y_test, y_pred)
        
        # Validación cruzada para robustez
        n_splits = min(5, len(X) // 2)
        if n_splits >= 2:
            cv_scores = cross_val_score(self.modelo, X_scaled, y, cv=n_splits)
            precision_cv = cv_scores.mean()
        else:
            precision_cv = precision
        
        # Importancia de características
        importancias = dict(zip(self.feature_names, self.modelo.feature_importances_))
        top_features = sorted(importancias.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Guardar modelo
        os.makedirs('models/mantenimiento', exist_ok=True)
        joblib.dump(self.modelo, self.modelo_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        print(f"✅ Modelo entrenado. Precisión: {precision_cv*100:.2f}%")
        
        return {
            'success': True,
            'precision_test': round(float(precision) * 100, 2),
            'precision_cv': round(float(precision_cv) * 100, 2),
            'cumple_objetivo': bool(precision_cv >= self.precision_minima),
            'objetivo': f'{self.precision_minima * 100}%',
            'total_registros': int(len(datos)),
            'registros_usados': int(len(X)),
            'registros_entrenamiento': int(len(X_train)),
            'registros_prueba': int(len(X_test)),
            'features_importantes': [{'nombre': f[0], 'importancia': round(float(f[1])*100, 2)} for f in top_features],
            'mensaje': '¡Modelo entrenado exitosamente!' if precision_cv >= self.precision_minima else f'Modelo entrenado pero precisión ({precision_cv*100:.1f}%) por debajo del objetivo ({self.precision_minima*100}%)'
        }
    
    def cargar_modelo(self):
        """Carga el modelo entrenado"""
        try:
            if os.path.exists(self.modelo_path) and os.path.exists(self.scaler_path):
                self.modelo = joblib.load(self.modelo_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
        except Exception as e:
            print(f"Error cargando modelo: {e}")
        return False
    
    def predecir_falla(self, equipo_id):
        """
        Predice probabilidad de falla para un equipo específico.
        Retorna probabilidad entre 0 y 1.
        """
        if not self.modelo:
            if not self.cargar_modelo():
                return None
        
        query = """
            SELECT 
                COALESCE(e.id_categoria, 1) as id_categoria,
                COALESCE(DATEDIFF(CURDATE(), e.fecha_adquisicion), 365) as dias_antiguedad,
                COALESCE(e.vida_util_anos, 5) * 365 as vida_util_dias,
                COALESCE(e.valor_adquisicion, 0) as valor,
                COUNT(hm.id) as total_mantenimientos,
                COALESCE(AVG(hm.costo_mantenimiento), 0) as costo_promedio,
                COALESCE(AVG(hm.tiempo_inactividad_horas), 0) as inactividad_promedio,
                COALESCE(DATEDIFF(CURDATE(), MAX(hm.fecha_fin)), 30) as dias_sin_mantenimiento,
                CASE e.estado_fisico 
                    WHEN 'excelente' THEN 4
                    WHEN 'bueno' THEN 3
                    WHEN 'regular' THEN 2
                    WHEN 'malo' THEN 1
                    ELSE 3
                END as estado_numerico,
                (SELECT COUNT(*) FROM prestamos p WHERE p.id_equipo = e.id) as total_prestamos,
                e.estado_fisico
            FROM equipos e
            LEFT JOIN historial_mantenimiento hm ON e.id = hm.id_equipo AND hm.estado = 'completado'
            WHERE e.id = %s
            GROUP BY e.id, e.id_categoria, e.fecha_adquisicion, e.vida_util_anos, 
                     e.valor_adquisicion, e.estado_fisico
        """
        datos = self.db.obtener_uno(query, (equipo_id,))
        
        if not datos:
            return None
        
        features = [[
            float(datos['dias_antiguedad'] or 365),
            float(datos['vida_util_dias'] or 1825),
            float(datos['valor'] or 0),
            float(datos['total_mantenimientos'] or 0),
            float(datos['costo_promedio'] or 0),
            float(datos['inactividad_promedio'] or 0),
            float(datos['dias_sin_mantenimiento'] or 30),
            float(datos['estado_numerico'] or 3),
            float(datos['total_prestamos'] or 0),
            float(datos['id_categoria'] or 1)
        ]]
        
        try:
            X_scaled = self.scaler.transform(features)
            proba = self.modelo.predict_proba(X_scaled)[0]
            
            # Si el modelo solo tiene una clase, usar estado físico como indicador
            if len(proba) == 1:
                estado_fisico = datos.get('estado_fisico', 'bueno')
                if estado_fisico == 'malo':
                    return 0.95
                elif estado_fisico == 'regular':
                    return 0.75
                elif estado_fisico == 'bueno':
                    return 0.30  # Bajo riesgo
                else:  # excelente
                    return 0.10  # Muy bajo riesgo
            
            # Probabilidad de la clase positiva (falla)
            probabilidad = proba[1]
            return round(float(probabilidad), 4)
        except Exception as e:
            print(f"Error en predicción: {e}")
            # Fallback: usar estado físico como indicador conservador
            estado_fisico = datos.get('estado_fisico', 'bueno')
            if estado_fisico == 'malo':
                return 0.95
            elif estado_fisico == 'regular':
                return 0.75
            elif estado_fisico == 'bueno':
                return 0.30
            else:  # excelente
                return 0.10
            return None
    
    def analizar_todos_equipos(self):
        """
        Analiza todos los equipos y genera alertas predictivas.
        Retorna lista de equipos con alta probabilidad de falla.
        """
        if not self.modelo:
            if not self.cargar_modelo():
                return {'success': False, 'error': 'Modelo no entrenado. Ejecute primero POST /api/predictivo/entrenar'}
        
        equipos = self.db.ejecutar_query("""
            SELECT id, nombre, codigo_interno, estado_fisico
            FROM equipos 
            WHERE estado NOT IN ('dado_baja')
        """) or []
        
        if not equipos:
            return {'success': False, 'error': 'No hay equipos registrados'}
        
        alertas_generadas = 0
        equipos_riesgo = []
        equipos_analizados = 0
        
        for equipo in equipos:
            equipos_analizados += 1
            
            # Detectar equipos con estado físico crítico (malo o regular)
            estado_fisico = equipo.get('estado_fisico', 'bueno')
            es_estado_critico = estado_fisico in ['malo', 'regular']
            
            # Predecir con el modelo
            prob = self.predecir_falla(equipo['id'])
            
            # Determinar si el equipo está en riesgo
            en_riesgo = False
            riesgo = None
            probabilidad_final = 0
            
            if es_estado_critico:
                # Equipos con estado físico malo/regular son automáticamente CRÍTICO
                en_riesgo = True
                riesgo = 'CRÍTICO' if estado_fisico == 'malo' else 'ALTO'
                probabilidad_final = 95.0 if estado_fisico == 'malo' else 75.0
                print(f"⚠️ Equipo {equipo['nombre']} detectado con estado físico {estado_fisico} - Riesgo {riesgo}")
            elif prob is not None and prob >= 0.6:
                # Predicción del modelo
                en_riesgo = True
                riesgo = 'CRÍTICO' if prob >= 0.85 else 'ALTO' if prob >= 0.7 else 'MEDIO'
                probabilidad_final = round(prob * 100, 1)
            
            if en_riesgo:
                equipos_riesgo.append({
                    'equipo_id': equipo['id'],
                    'nombre': equipo['nombre'],
                    'codigo': equipo['codigo_interno'],
                    'probabilidad_falla': probabilidad_final,
                    'riesgo': riesgo,
                    'motivo': f'Estado físico: {estado_fisico}' if es_estado_critico else 'Predicción IA'
                })
                
                # Crear alertas para riesgo ALTO o CRÍTICO
                if riesgo in ['ALTO', 'CRÍTICO']:
                    alerta_existente = self.db.obtener_uno("""
                        SELECT id FROM alertas_mantenimiento 
                        WHERE id_equipo = %s 
                        AND tipo_alerta = 'falla_predicha'
                        AND estado_alerta IN ('pendiente', 'en_proceso')
                    """, (equipo['id'],))
                    
                    if not alerta_existente:
                        descripcion = f"⚠️ Equipo con estado físico {estado_fisico.upper()} - {equipo['nombre']} ({equipo['codigo_interno']})" if es_estado_critico else f"🤖 IA predice falla con {probabilidad_final}% de probabilidad para {equipo['nombre']} ({equipo['codigo_interno']})"
                        
                        self.db.insertar('alertas_mantenimiento', {
                            'id_equipo': equipo['id'],
                            'tipo_alerta': 'falla_predicha',
                            'descripcion_alerta': descripcion,
                            'fecha_limite': (datetime.now() + timedelta(days=3 if es_estado_critico else 7)).strftime('%Y-%m-%d'),
                            'prioridad': 'critica' if riesgo == 'CRÍTICO' else 'alta',
                            'estado_alerta': 'pendiente'
                        })
                        alertas_generadas += 1
        
        # Ordenar por probabilidad descendente
        equipos_riesgo.sort(key=lambda x: x['probabilidad_falla'], reverse=True)
        
        return {
            'success': True,
            'equipos_analizados': equipos_analizados,
            'equipos_riesgo': len(equipos_riesgo),
            'alertas_generadas': alertas_generadas,
            'detalle': equipos_riesgo[:20],  # Top 20
            'mensaje': f'Análisis completado. {alertas_generadas} alertas predictivas generadas.'
        }
    
    def obtener_estado_modelo(self):
        """Retorna el estado actual del modelo"""
        modelo_existe = os.path.exists(self.modelo_path)
        
        info = {
            'modelo_entrenado': modelo_existe,
            'precision_objetivo': f'{self.precision_minima * 100}%',
            'ruta_modelo': self.modelo_path
        }
        
        if modelo_existe and self.cargar_modelo():
            info['n_estimators'] = self.modelo.n_estimators
            info['max_depth'] = self.modelo.max_depth
            info['features'] = self.feature_names
        
        return info
