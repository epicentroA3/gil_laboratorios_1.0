def test_mysql():
    """Prueba conexión a MySQL"""
    try:
        import mysql.connector
        print("✅ mysql-connector-python: INSTALADO")
        
        # Probar conexión básica
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                connect_timeout=5
            )
            conn.close()
            print("✅ MySQL: CONEXIÓN EXITOSA")
            return True
        except mysql.connector.Error as e:
            print(f"⚠️ MySQL: INSTALADO pero conexión falló: {e}")
            print("   (Esto se puede configurar después)")
            return True
    except ImportError:
        print("❌ mysql-connector-python: NO INSTALADO")
        return False

def test_opencv():
    """Prueba OpenCV"""
    try:
        import cv2
        print(f"✅ OpenCV: INSTALADO (versión {cv2.__version__})")
        
        # Probar funcionalidad básica
        import numpy as np
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("✅ OpenCV: FUNCIONALIDAD BÁSICA OK")
        return True
    except ImportError:
        print("❌ OpenCV: NO INSTALADO")
        return False
    except Exception as e:
        print(f"⚠️ OpenCV: INSTALADO pero error en funcionalidad: {e}")
        return False

def test_speech_recognition():
    """Prueba reconocimiento de voz"""
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition: INSTALADO")
        
        # Probar inicialización básica
        r = sr.Recognizer()
        print("✅ SpeechRecognition: INICIALIZACIÓN OK")
        return True
    except ImportError:
        print("❌ SpeechRecognition: NO INSTALADO")
        return False
    except Exception as e:
        print(f"⚠️ SpeechRecognition: INSTALADO pero error: {e}")
        return False

def test_pyttsx3():
    """Prueba síntesis de voz"""
    try:
        import pyttsx3
        print("✅ pyttsx3: INSTALADO")
        
        # Probar inicialización básica
        engine = pyttsx3.init()
        print("✅ pyttsx3: INICIALIZACIÓN OK")
        engine.stop()
        return True
    except ImportError:
        print("❌ pyttsx3: NO INSTALADO")
        return False
    except Exception as e:
        print(f"⚠️ pyttsx3: INSTALADO pero error: {e}")
        print("   (Puede funcionar en el sistema real)")
        return True

def test_pillow():
    """Prueba Pillow (PIL)"""
    try:
        from PIL import Image
        import PIL
        print(f"✅ Pillow: INSTALADO (versión {PIL.__version__})")
        
        # Probar funcionalidad básica
        img = Image.new('RGB', (100, 100), color='red')
        print("✅ Pillow: FUNCIONALIDAD BÁSICA OK")
        return True
    except ImportError:
        print("❌ Pillow: NO INSTALADO")
        return False

def test_numpy():
    """Prueba NumPy"""
    try:
        import numpy as np
        print(f"✅ NumPy: INSTALADO (versión {np.__version__})")
        
        # Probar funcionalidad básica
        arr = np.array([1, 2, 3, 4, 5])
        print("✅ NumPy: FUNCIONALIDAD BÁSICA OK")
        return True
    except ImportError:
        print("❌ NumPy: NO INSTALADO")
        return False

def test_utilidades():
    """Prueba utilidades adicionales"""
    try:
        from datetime import datetime
        import dateutil.parser
        import pytz
        print("✅ Utilidades de fecha/hora: INSTALADAS")
        return True
    except ImportError as e:
        print(f"⚠️ Utilidades de fecha/hora: {e}")
        return False

def test_hardware():
    """Prueba acceso a hardware"""
    print("\n🔍 PROBANDO ACCESO A HARDWARE:")
    
    # Probar cámara
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Cámara: ACCESIBLE")
            cap.release()
        else:
            print("⚠️ Cámara: NO ACCESIBLE (será opcional)")
    except Exception as e:
        print(f"⚠️ Cámara: ERROR - {e}")
    
    # Probar micrófono
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
        print("✅ Micrófono: ACCESIBLE")
    except Exception as e:
        print(f"⚠️ Micrófono: ERROR - {e}")

def main():
    print("🧪 VERIFICACIÓN DE DEPENDENCIAS - SISTEMA LABORATORIO SENA")
    print("=" * 70)
    
    tests = [
        ("MySQL Connector", test_mysql),
        ("OpenCV", test_opencv),
        ("SpeechRecognition", test_speech_recognition),
        ("pyttsx3", test_pyttsx3),
        ("Pillow", test_pillow),
        ("NumPy", test_numpy),
        ("Utilidades", test_utilidades)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n🔍 Probando {nombre}:")
        resultado = test_func()
        resultados.append(resultado)
    
    # Probar hardware
    test_hardware()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN:")
    exitos = sum(resultados)
    total = len(resultados)
    
    if exitos == total:
        print("🎉 ¡TODAS LAS DEPENDENCIAS INSTALADAS CORRECTAMENTE!")
        print("✅ Sistema listo para ejecutar")
    elif exitos >= total - 1:
        print("✅ Dependencias principales OK")
        print("⚠️ Algunos componentes opcionales pueden fallar")
    else:
        print("❌ Faltan dependencias críticas")
        print("🔧 Revisar e instalar dependencias faltantes")
    
    print(f"📈 Éxito: {exitos}/{total} dependencias")
    print("=" * 70)

if __name__ == "__main__":
    main()