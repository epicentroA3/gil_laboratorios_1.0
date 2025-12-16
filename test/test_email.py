"""
Script para probar la configuración de email
"""
import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Cargar variables de entorno
load_dotenv()

# Crear app temporal
app = Flask(__name__)

# Configurar Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

print("=" * 60)
print("PRUEBA DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)
print(f"\n📧 Configuración:")
print(f"  MAIL_SERVER: {app.config['MAIL_SERVER']}")
print(f"  MAIL_PORT: {app.config['MAIL_PORT']}")
print(f"  MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
print(f"  MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
print(f"  MAIL_PASSWORD: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'NO CONFIGURADA'}")
print(f"  MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("\n❌ ERROR: Credenciales no configuradas en .env")
    exit(1)

mail = Mail(app)

print("\n🔄 Intentando enviar email de prueba...")

with app.app_context():
    try:
        msg = Message(
            'Prueba de Email - Sistema GIL',
            recipients=[app.config['MAIL_USERNAME']]  # Enviar a ti mismo
        )
        msg.body = 'Este es un email de prueba del Sistema GIL. Si recibes este mensaje, la configuración es correcta.'
        msg.html = '''
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">✅ Prueba Exitosa</h2>
            <p>Este es un email de prueba del <strong>Sistema GIL</strong>.</p>
            <p>Si recibes este mensaje, la configuración de email es correcta.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Centro Minero de Sogamoso - SENA</p>
        </body>
        </html>
        '''
        
        mail.send(msg)
        print(f"\n✅ Email enviado exitosamente a {app.config['MAIL_USERNAME']}")
        print("\n📬 Revisa tu bandeja de entrada (o SPAM)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error al enviar email:")
        print(f"   {str(e)}")
        print("\n🔍 Detalles del error:")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que la App Password sea correcta (16 caracteres)")
        print("   2. Asegúrate de que la verificación en 2 pasos esté activa")
        print("   3. Verifica que no haya espacios extra en .env")
        print("   4. Intenta generar una nueva App Password")
        print("=" * 60)
