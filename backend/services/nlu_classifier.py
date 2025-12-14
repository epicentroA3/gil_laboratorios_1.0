# Clasificador de Intenciones NLU con scikit-learn
# Centro Minero SENA
# Sistema GIL - Asistente LUCIA

import os
import json
import re
from typing import Dict, List, Tuple, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn no está instalado. Instalar con: pip install scikit-learn joblib")


class NLUClassifier:
    """
    Clasificador de intenciones usando NLP y scikit-learn
    Identifica la intención del usuario a partir de texto
    """
    
    _instance = None
    
    # Ruta para guardar el modelo entrenado
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'nlu_model.joblib')
    
    # Datos de entrenamiento para el clasificador
    # Comandos basados en las secciones del sidebar
    TRAINING_DATA = {
        # === INTERACCIÓN BÁSICA ===
        'saludo': [
            'hola', 'hola lucia', 'buenos días', 'buenas tardes', 'buenas noches',
            'qué tal', 'cómo estás', 'hey', 'hola qué tal', 'saludos',
            'hola buenas', 'muy buenos días', 'qué hay', 'holi'
        ],
        'despedida': [
            'adiós', 'chao', 'hasta luego', 'nos vemos', 'bye',
            'hasta pronto', 'me voy', 'gracias adiós', 'hasta mañana'
        ],
        'apagar_microfono': [
            'lucia apagar', 'lucia apágate', 'apagar lucia', 'apágate lucia',
            'lucia detente', 'lucia para', 'lucia stop', 'lucia silencio',
            'lucia deja de escuchar', 'lucia desactivar', 'desactivar lucia',
            'lucia descansar', 'lucia dormir', 'lucia pausar', 'lucia pausa',
            'lucia ya no escuches', 'lucia terminar', 'lucia finalizar',
            'lucia off', 'lucia apagar micrófono', 'lucia cierra el micrófono'
        ],
        'ayuda': [
            'ayuda', 'qué puedes hacer', 'cuáles son tus funciones', 'comandos disponibles',
            'cómo funciona', 'necesito ayuda', 'qué haces', 'para qué sirves',
            'opciones', 'menú', 'qué comandos hay', 'instrucciones'
        ],
        
        # === NAVEGACIÓN - DASHBOARD ===
        'ir_dashboard': [
            'lucia ir al dashboard', 'lucia abrir dashboard', 'lucia ver dashboard', 
            'lucia mostrar dashboard', 'lucia panel principal', 'lucia inicio', 
            'lucia ir al inicio', 'lucia página principal', 'lucia ver panel', 
            'lucia abrir panel de control', 'lucia ir a inicio'
        ],
        
        # === SECCIÓN GESTIÓN ===
        'ir_buscador': [
            'lucia buscar', 'lucia buscador', 'lucia ir al buscador', 
            'lucia abrir buscador', 'lucia buscar equipo', 'lucia buscar en inventario', 
            'lucia hacer búsqueda', 'lucia quiero buscar'
        ],
        'ir_usuarios': [
            'lucia ver usuarios', 'lucia ir a usuarios', 'lucia gestionar usuarios', 
            'lucia abrir usuarios', 'lucia lista de usuarios', 'lucia administrar usuarios', 
            'lucia mostrar usuarios', 'lucia usuarios del sistema', 'lucia ver lista de usuarios',
            'lucia usuarios', 'lucia ir usuarios', 'lucia sección usuarios', 'lucia gestión usuarios',
            'lucia entrar a usuarios', 'lucia acceder a usuarios', 'lucia módulo usuarios'
        ],
        'ir_roles': [
            'lucia ver roles', 'lucia ir a roles', 'lucia gestionar roles', 
            'lucia abrir roles', 'lucia permisos', 'lucia ver permisos', 
            'lucia administrar roles', 'lucia configurar roles'
        ],
        'ir_programas': [
            'lucia ver programas', 'lucia ir a programas', 'lucia programas de formación', 
            'lucia abrir programas', 'lucia lista de programas', 'lucia programas académicos', 
            'lucia mostrar programas', 'lucia ver fichas', 'lucia programas del sena'
        ],
        'listar_equipos': [
            'lucia equipos disponibles', 'lucia mostrar inventario', 'lucia listar equipos',
            'lucia qué equipos hay', 'lucia ver todos los equipos', 'lucia inventario',
            'lucia equipos del laboratorio', 'lucia catálogo de equipos', 'lucia lista de equipos',
            'lucia mostrar equipos', 'lucia ver equipos disponibles', 'lucia ir a equipos',
            'lucia abrir equipos', 'lucia gestionar equipos', 'lucia ver equipos',
            'lucia equipos', 'lucia ir equipos', 'lucia gestión de equipos',
            'lucia administrar equipos', 'lucia sección equipos', 'lucia módulo equipos',
            'lucia entrar a equipos', 'lucia acceder a equipos', 'lucia dame los equipos',
            'lucia muéstrame los equipos', 'lucia quiero ver equipos', 'lucia necesito ver equipos'
        ],
        'consultar_laboratorio': [
            'lucia laboratorios disponibles', 'lucia ver laboratorios', 'lucia información del laboratorio',
            'lucia horario del laboratorio', 'lucia qué laboratorios hay', 'lucia estado del laboratorio',
            'lucia consultar laboratorio', 'lucia laboratorios abiertos', 'lucia ir a laboratorios',
            'lucia abrir laboratorios', 'lucia gestionar laboratorios', 'lucia lista de laboratorios',
            'lucia laboratorios', 'lucia ir laboratorios', 'lucia sección laboratorios',
            'lucia entrar a laboratorios', 'lucia acceder a laboratorios', 'lucia gestión laboratorios'
        ],
        'ir_practicas': [
            'lucia ver prácticas', 'lucia ir a prácticas', 'lucia prácticas de laboratorio', 
            'lucia abrir prácticas', 'lucia programar práctica', 'lucia agendar práctica', 
            'lucia nueva práctica', 'lucia crear práctica de laboratorio', 
            'lucia reservar laboratorio para práctica', 'lucia programar sesión', 
            'lucia agendar clase práctica', 'lucia gestionar prácticas',
            'lucia lista de prácticas', 'lucia prácticas programadas'
        ],
        'ir_prestamos': [
            'lucia ir a préstamos', 'lucia abrir préstamos', 'lucia préstamos',
            'lucia ir préstamos', 'lucia sección préstamos', 'lucia entrar a préstamos',
            'lucia acceder a préstamos', 'lucia gestión préstamos', 'lucia ver préstamos',
            'lucia gestionar préstamos', 'lucia mis préstamos', 'lucia préstamos activos',
            'lucia ir a reservas', 'lucia abrir reservas', 'lucia gestionar reservas',
            'lucia reservas', 'lucia ir reservas', 'lucia sección reservas',
            'lucia entrar a reservas', 'lucia acceder a reservas', 'lucia gestión reservas'
        ],
        'listar_reservas': [
            'lucia mis reservas', 'lucia ver reservas', 
            'lucia qué tengo reservado', 'lucia listar reservas', 'lucia mostrar mis préstamos', 
            'lucia reservas pendientes', 'lucia ver mis préstamos', 'lucia consultar reservas', 
            'lucia estado de mis reservas', 'lucia qué equipos tengo', 'lucia mis préstamos actuales'
        ],
        'crear_reserva': [
            'lucia reservar equipo', 'lucia quiero reservar', 'lucia necesito el microscopio',
            'lucia préstame el osciloscopio', 'lucia solicitar préstamo', 'lucia pedir equipo',
            'lucia reservar microscopio', 'lucia quiero el multímetro', 'lucia necesito usar',
            'lucia apartar equipo', 'lucia solicitar equipo', 'lucia hacer reserva', 
            'lucia nueva reserva', 'lucia reservar para mañana', 'lucia necesito reservar', 
            'lucia quiero hacer una reserva', 'lucia préstamo de equipo', 'lucia solicitar un préstamo'
        ],
        'cancelar_reserva': [
            'lucia cancelar reserva', 'lucia anular préstamo', 'lucia devolver equipo',
            'lucia ya no necesito', 'lucia cancelar mi reserva', 'lucia quiero cancelar',
            'lucia anular reserva', 'lucia eliminar reserva', 'lucia borrar préstamo'
        ],
        'consultar_mantenimiento': [
            'lucia mantenimiento pendiente', 'lucia equipos en mantenimiento', 
            'lucia estado de mantenimiento', 'lucia próximo mantenimiento', 
            'lucia historial de mantenimiento', 'lucia ver mantenimientos',
            'lucia ir a mantenimiento', 'lucia abrir mantenimiento', 
            'lucia gestionar mantenimiento', 'lucia mantenimientos programados', 
            'lucia ver mantenimiento', 'lucia mantenimiento', 'lucia ir mantenimiento',
            'lucia sección mantenimiento', 'lucia entrar a mantenimiento'
        ],
        'ir_capacitaciones': [
            'lucia ver capacitaciones', 'lucia ir a capacitaciones', 'lucia abrir capacitaciones',
            'lucia capacitaciones disponibles', 'lucia cursos', 'lucia entrenamientos',
            'lucia lista de capacitaciones', 'lucia gestionar capacitaciones', 'lucia mis capacitaciones'
        ],
        'reporte': [
            'lucia generar reporte', 'lucia estadísticas', 'lucia informe de uso', 
            'lucia reporte de préstamos', 'lucia ver estadísticas', 'lucia métricas', 
            'lucia resumen de actividad', 'lucia ir a reportes', 'lucia abrir reportes', 
            'lucia ver reportes', 'lucia informes', 'lucia reportes', 'lucia ir reportes',
            'lucia sección reportes', 'lucia entrar a reportes', 'lucia gestión reportes'
        ],
        
        # === SECCIÓN IA & AUTOMATIZACIÓN ===
        'ir_reconocimiento': [
            'lucia reconocer equipo', 'lucia identificar equipo', 'lucia escanear equipo', 
            'lucia leer qr', 'lucia escanear código', 'lucia reconocimiento', 
            'lucia ir a reconocimiento', 'lucia abrir cámara', 'lucia identificar con cámara', 
            'lucia usar cámara', 'lucia reconocer con ia', 'lucia identificar equipo con ia'
        ],
        'ir_registro_facial': [
            'lucia registro facial', 'lucia registrar mi cara', 'lucia registrar rostro',
            'lucia ir a registro facial', 'lucia abrir registro facial', 'lucia configurar rostro',
            'lucia agregar mi foto', 'lucia registrar mi rostro', 'lucia reconocimiento facial'
        ],
        'ir_asistente': [
            'lucia abrir asistente', 'lucia ir al asistente', 'lucia asistente lucia',
            'lucia hablar con lucia', 'lucia asistente de voz', 'lucia comandos de voz'
        ],
        'ir_ia_visual': [
            'lucia ia visual', 'lucia entrenamiento ia', 'lucia entrenar modelo', 
            'lucia ir a ia visual', 'lucia abrir ia visual', 'lucia configurar ia', 
            'lucia modelo de reconocimiento'
        ],
        'ir_nuevo_equipo_ia': [
            'lucia nuevo equipo ia', 'lucia registrar equipo ia', 'lucia agregar equipo ia',
            'lucia crear equipo con ia', 'lucia nuevo registro ia'
        ],
        'ir_gestionar_registros': [
            'lucia gestionar registros', 'lucia ver registros ia', 'lucia administrar registros',
            'lucia registros de ia', 'lucia ir a gestionar registros'
        ],
        
        # === SECCIÓN ADMINISTRACIÓN ===
        'ir_backup': [
            'lucia backup', 'lucia respaldo', 'lucia copia de seguridad', 'lucia ir a backup',
            'lucia hacer backup', 'lucia crear respaldo', 'lucia abrir backup', 
            'lucia respaldar datos', 'lucia ver backups', 'lucia gestionar backups'
        ],
        'ir_configuracion': [
            'lucia configuración', 'lucia ajustes', 'lucia ir a configuración', 
            'lucia abrir configuración', 'lucia configurar sistema', 'lucia opciones del sistema', 
            'lucia preferencias', 'lucia ajustes del sistema', 'lucia ver configuración'
        ],
        
        # === SECCIÓN USUARIO ===
        'ir_perfil': [
            'lucia mi perfil', 'lucia ver perfil', 'lucia ir a perfil', 'lucia abrir perfil',
            'lucia mis datos', 'lucia información personal', 'lucia editar perfil',
            'lucia ver mis datos', 'lucia configurar perfil'
        ],
        'ir_ayuda': [
            'lucia ir a ayuda', 'lucia abrir ayuda', 'lucia ver ayuda', 'lucia documentación',
            'lucia manual', 'lucia guía de uso', 'lucia soporte', 'lucia centro de ayuda'
        ],
        'cerrar_sesion': [
            'lucia cerrar sesión', 'lucia salir', 'lucia logout', 'lucia desconectar',
            'lucia cerrar mi sesión', 'lucia quiero salir', 'lucia desloguear'
        ],
        
        # === CONSULTAS ESPECÍFICAS ===
        'consultar_equipo': [
            'lucia estado del equipo', 'lucia disponibilidad', 'lucia está disponible',
            'lucia información del microscopio', 'lucia detalles del equipo', 'lucia ver equipo',
            'lucia consultar equipo', 'lucia buscar equipo', 'lucia información de',
            'lucia cómo está el', 'lucia estado del microscopio', 'lucia disponible el'
        ],
        
        'desconocido': [
            'asdfgh', 'xyz', 'no entiendo', 'qwerty', 'test', 'prueba'
        ]
    }
    
    # Respuestas predefinidas por intención
    RESPONSES = {
        # === INTERACCIÓN BÁSICA ===
        'saludo': '¡Hola! Soy LUCIA, tu asistente virtual del laboratorio. ¿En qué puedo ayudarte hoy?',
        'despedida': '¡Hasta luego! Fue un placer ayudarte. ¡Que tengas un excelente día!',
        'apagar_microfono': 'Entendido, me voy a descansar. ¡Llámame cuando me necesites! Apagando micrófono...',
        'ayuda': '''Puedo ayudarte con las siguientes acciones:
• Navegación: "Ir al dashboard", "Ver equipos", "Abrir reservas"
• Reservar equipos: "Quiero reservar el microscopio"
• Ver tus reservas: "Mostrar mis reservas"
• Cancelar reservas: "Cancelar mi reserva"
• Consultar equipos: "¿Está disponible el osciloscopio?"
• Ver inventario: "Mostrar equipos disponibles"
• Laboratorios: "Ver laboratorios"
• Reportes: "Ver estadísticas"
• IA: "Reconocer equipo", "Registro facial"
• Configuración: "Mi perfil", "Configuración"
¿Qué te gustaría hacer?''',
        
        # === NAVEGACIÓN - DASHBOARD ===
        'ir_dashboard': 'Abriendo el panel principal...',
        
        # === SECCIÓN GESTIÓN ===
        'ir_buscador': 'Abriendo el buscador de inventario...',
        'ir_usuarios': 'Abriendo gestión de usuarios...',
        'ir_roles': 'Abriendo configuración de roles y permisos...',
        'ir_programas': 'Abriendo programas de formación...',
        'listar_equipos': 'Consultando equipos disponibles...',
        'consultar_laboratorio': 'Consultando información de laboratorios...',
        'ir_practicas': 'Abriendo prácticas de laboratorio...',
        'ir_prestamos': 'Abriendo sección de préstamos...',
        'listar_reservas': 'Consultando tus préstamos activos...',
        'crear_reserva': 'Entendido, vamos a crear un préstamo. Te llevo a la sección de préstamos.',
        'cancelar_reserva': 'Te llevo a la sección de préstamos para cancelar.',
        'consultar_mantenimiento': 'Consultando estado de mantenimientos...',
        'ir_capacitaciones': 'Abriendo capacitaciones disponibles...',
        'reporte': 'Abriendo reportes y estadísticas...',
        
        # === SECCIÓN IA & AUTOMATIZACIÓN ===
        'ir_reconocimiento': 'Abriendo reconocimiento de equipos con IA...',
        'ir_registro_facial': 'Abriendo registro facial...',
        'ir_asistente': 'Ya estás hablando conmigo, LUCIA. ¿En qué puedo ayudarte?',
        'ir_ia_visual': 'Abriendo entrenamiento de IA visual...',
        'ir_nuevo_equipo_ia': 'Abriendo registro de nuevo equipo con IA...',
        'ir_gestionar_registros': 'Abriendo gestión de registros de IA...',
        
        # === SECCIÓN ADMINISTRACIÓN ===
        'ir_backup': 'Abriendo gestión de respaldos...',
        'ir_configuracion': 'Abriendo configuración del sistema...',
        
        # === SECCIÓN USUARIO ===
        'ir_perfil': 'Abriendo tu perfil de usuario...',
        'ir_ayuda': 'Abriendo centro de ayuda...',
        'cerrar_sesion': 'Cerrando tu sesión. ¡Hasta pronto!',
        
        # === CONSULTAS ESPECÍFICAS ===
        'consultar_equipo': 'Buscando información del equipo...',
        
        'desconocido': 'Lo siento, no entendí tu solicitud. ¿Podrías reformularla? Di "ayuda" para ver las opciones disponibles.'
    }
    
    def __new__(cls):
        """Singleton para reutilizar el clasificador"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa el clasificador NLU"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._pipeline = None
            self._intents = list(self.TRAINING_DATA.keys())
            
            if SKLEARN_AVAILABLE:
                self._load_or_train_model()
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para mejorar la clasificación"""
        # Convertir a minúsculas
        text = text.lower().strip()
        
        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r'[^\w\sáéíóúüñ]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _load_or_train_model(self) -> bool:
        """Carga el modelo existente o entrena uno nuevo"""
        # Intentar cargar modelo existente
        if os.path.exists(self.MODEL_PATH):
            try:
                self._pipeline = joblib.load(self.MODEL_PATH)
                print("✅ Modelo NLU cargado desde archivo")
                return True
            except Exception as e:
                print(f"⚠️ Error cargando modelo NLU: {e}")
        
        # Entrenar nuevo modelo
        return self._train_model()
    
    def _train_model(self) -> bool:
        """Entrena el modelo de clasificación"""
        if not SKLEARN_AVAILABLE:
            return False
        
        try:
            print("🔄 Entrenando modelo NLU...")
            
            # Preparar datos de entrenamiento
            X_train = []
            y_train = []
            
            for intent, examples in self.TRAINING_DATA.items():
                for example in examples:
                    X_train.append(self._preprocess_text(example))
                    y_train.append(intent)
            
            # Crear pipeline: TF-IDF + Naive Bayes
            self._pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=1000,
                    min_df=1
                )),
                ('clf', MultinomialNB(alpha=0.1))
            ])
            
            # Entrenar
            self._pipeline.fit(X_train, y_train)
            
            # Guardar modelo
            os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
            joblib.dump(self._pipeline, self.MODEL_PATH)
            
            print("✅ Modelo NLU entrenado y guardado")
            return True
            
        except Exception as e:
            print(f"❌ Error entrenando modelo NLU: {e}")
            return False
    
    def is_available(self) -> bool:
        """Verifica si el clasificador está disponible"""
        return SKLEARN_AVAILABLE and self._pipeline is not None
    
    def get_status(self) -> Dict:
        """Retorna el estado del clasificador"""
        return {
            'sklearn_installed': SKLEARN_AVAILABLE,
            'model_loaded': self._pipeline is not None,
            'model_path': os.path.abspath(self.MODEL_PATH),
            'intents_count': len(self._intents),
            'intents': self._intents,
            'ready': self.is_available()
        }
    
    def classify(self, text: str) -> Tuple[str, float, str]:
        """
        Clasifica la intención del texto
        
        Args:
            text: Texto a clasificar
        
        Returns:
            Tuple (intención, confianza, respuesta_sugerida)
        """
        if not self.is_available():
            return ('desconocido', 0.0, self.RESPONSES['desconocido'])
        
        if not text or not text.strip():
            return ('desconocido', 0.0, self.RESPONSES['desconocido'])
        
        try:
            # Preprocesar texto
            processed_text = self._preprocess_text(text)
            
            # Predecir intención
            intent = self._pipeline.predict([processed_text])[0]
            
            # Obtener probabilidades
            probas = self._pipeline.predict_proba([processed_text])[0]
            confidence = max(probas)
            
            # Si la confianza es muy baja, marcar como desconocido
            if confidence < 0.3:
                intent = 'desconocido'
                confidence = 1.0 - confidence
            
            # Obtener respuesta
            response = self.RESPONSES.get(intent, self.RESPONSES['desconocido'])
            
            return (intent, float(confidence), response)
            
        except Exception as e:
            print(f"❌ Error clasificando texto: {e}")
            return ('desconocido', 0.0, self.RESPONSES['desconocido'])
    
    def extract_entities(self, text: str, intent: str) -> Dict:
        """
        Extrae entidades del texto según la intención
        
        Args:
            text: Texto original
            intent: Intención clasificada
        
        Returns:
            Diccionario con entidades extraídas
        """
        entities = {}
        text_lower = text.lower()
        
        # Patrones de equipos comunes
        equipos = [
            'microscopio', 'osciloscopio', 'multímetro', 'multimetro',
            'fuente de poder', 'generador', 'analizador', 'espectrómetro',
            'balanza', 'centrífuga', 'centrifuga', 'pipeta', 'agitador',
            'termómetro', 'termometro', 'ph metro', 'phmetro'
        ]
        
        for equipo in equipos:
            if equipo in text_lower:
                entities['equipo'] = equipo
                break
        
        # Patrones de fechas
        if 'mañana' in text_lower:
            entities['fecha'] = 'mañana'
        elif 'hoy' in text_lower:
            entities['fecha'] = 'hoy'
        elif 'próxima semana' in text_lower or 'proxima semana' in text_lower:
            entities['fecha'] = 'próxima semana'
        
        # Patrones de laboratorios
        labs = ['química', 'quimica', 'física', 'fisica', 'biología', 'biologia', 'electrónica', 'electronica']
        for lab in labs:
            if lab in text_lower:
                entities['laboratorio'] = lab
                break
        
        return entities
    
    def retrain(self, new_examples: Dict[str, List[str]] = None) -> bool:
        """
        Reentrena el modelo con nuevos ejemplos
        
        Args:
            new_examples: Diccionario {intención: [ejemplos]}
        
        Returns:
            True si el reentrenamiento fue exitoso
        """
        if new_examples:
            for intent, examples in new_examples.items():
                if intent in self.TRAINING_DATA:
                    self.TRAINING_DATA[intent].extend(examples)
                else:
                    self.TRAINING_DATA[intent] = examples
                    self._intents.append(intent)
        
        return self._train_model()


# Instancia global del clasificador
nlu_classifier = NLUClassifier()
