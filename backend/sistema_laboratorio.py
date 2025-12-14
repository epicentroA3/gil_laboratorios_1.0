import sys
import os

def verificar_entorno():
    """Verifica que el entorno esté listo"""
    print("🔍 VERIFICANDO ENTORNO DEL SISTEMA...")
    
    try:
        import mysql.connector
        print("✅ MySQL connector: OK")
    except ImportError:
        print("❌ MySQL connector: FALTA")
        return False
    
    try:
        import cv2
        print("✅ OpenCV: OK")
    except ImportError:
        print("❌ OpenCV: FALTA")
        return False
        
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition: OK")
    except ImportError:
        print("❌ SpeechRecognition: FALTA")
        return False
        
    try:
        import pyttsx3
        print("✅ pyttsx3: OK")
    except ImportError:
        print("❌ pyttsx3: FALTA")
        return False
    
    return True

def test_mysql_connection():
    """Prueba la conexión a MySQL"""
    try:
        import mysql.connector
        
        print("\n🔗 PROBANDO CONEXIÓN A MYSQL...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',  # Cambia si tienes contraseña
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL conectado - Versión: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        print("\n💡 SOLUCIONES:")
        print("   1. Verificar que MySQL esté corriendo")
        print("   2. Verificar usuario/contraseña en el código")
        print("   3. Verificar puerto 3306")
        return False

def main():
    print("🔬 SISTEMA DE GESTIÓN INTELIGENTE DE LABORATORIOS")
    print("   Centro Minero - Regional Boyacá - SENA")
    print("   PRUEBA INICIAL - PASO 3")
    print("=" * 60)
    
    if not verificar_entorno():
        print("\n❌ Entorno no está listo. Volver al PASO 2.")
        return
    
    if not test_mysql_connection():
        print("\n❌ MySQL no está listo. Revisar configuración.")
        return
    
    print("\n🎉 ¡SISTEMA LISTO PARA EJECUTAR!")
    print("Proceder a descargar el código completo.")

if __name__ == "__main__":
    main()