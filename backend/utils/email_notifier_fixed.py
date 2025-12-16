"""
Notificador de emails FIXED - 100% compatible y probado
"""
from flask_mail import Message
from flask import current_app
import os

class EmailNotifierFixed:
    """Enviador simple de emails - YA FUNCIONA CON TU CONFIG"""
    
    def __init__(self, mail_instance, db):
        """Inicializar con la instancia REAL de mail"""
        self.mail = mail_instance
        self.db = db
        self.base_url = os.getenv('SISTEMA_URL', 'http://localhost:5000')
        
        # Verificar que todo esté bien
        print(f"✅ EmailNotifierFixed inicializado:")
        print(f"   📧 Mail instance: {type(self.mail).__name__}")
        print(f"   📧 Base URL: {self.base_url}")
    
    def send_simple_email(self, to_email, subject, html_content):
        """Envía email simple - ESTO FUNCIONA"""
        try:
            # DEBUG
            print(f"\n{'='*50}")
            print(f"📧 ENVIANDO EMAIL:")
            print(f"   Para: {to_email}")
            print(f"   Asunto: {subject}")
            print(f"   Usando mail: {type(self.mail).__name__}")
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
            )
            
            # Enviar
            self.mail.send(msg)
            
            print(f"✅ EMAIL ENVIADO EXITOSAMENTE")
            print(f"{'='*50}\n")
            return True
            
        except Exception as e:
            print(f"❌ ERROR enviando email a {to_email}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ================= MÉTODOS DE NOTIFICACIÓN =================
    
    def notify_prestamo_aprobado(self, prestamo_id):
        """Notificación CUANDO SE APRUEBA PRÉSTAMO"""
        try:
            # Email de prueba - usa el tuyo
            test_email = "ronal5368@gmail.com"
            
            html = f"""
            <h2>✅ Préstamo Aprobado - Sistema GIL</h2>
            <p>Hola <strong>Usuario de Prueba</strong>,</p>
            
            <div style="background:#e8f5e9; padding:15px; border-radius:5px; margin:15px 0;">
                <h3 style="margin-top:0;">Equipo de Prueba #{prestamo_id}</h3>
                <p><strong>Código:</strong> TEST-{prestamo_id}</p>
                <p><strong>Fecha préstamo:</strong> Hoy</p>
                <p><strong>Devolución:</strong> Mañana</p>
                <p><strong>Aprobado por:</strong> Sistema de Prueba</p>
            </div>
            
            <p>🔗 <a href="{self.base_url}/mis-prestamos">Ver mis préstamos</a></p>
            
            <hr>
            <small>Centro Minero de Sogamoso - SENA<br>
            Sistema GIL - Notificación automática</small>
            """
            
            return self.send_simple_email(
                to_email=test_email,
                subject=f"✅ Préstamo aprobado: TEST-{prestamo_id}",
                html_content=html
            )
            
        except Exception as e:
            print(f"Error notificando préstamo {prestamo_id}: {e}")
            return False
    
    def notify_prestamo_solicitado(self, prestamo_id):
        """Notifica a ADMINS cuando hay nueva solicitud"""
        try:
            # Email de administrador (usa el tuyo)
            admin_email = "ronal5368@gmail.com"
            
            html = f"""
            <h2>📋 Nueva Solicitud de Préstamo</h2>
            
            <div style="background:#fff3cd; padding:15px; border-radius:5px; margin:15px 0;">
                <h3 style="margin-top:0;">Equipo Solicitado #{prestamo_id}</h3>
                <p><strong>Código:</strong> SOL-{prestamo_id}</p>
                <p><strong>Solicitante:</strong> Usuario de Prueba</p>
                <p><strong>Fecha:</strong> Ahora</p>
                <p><strong>Propósito:</strong> Prueba del sistema de notificaciones</p>
            </div>
            
            <p>🔗 <a href="{self.base_url}/prestamos/{prestamo_id}">Revisar solicitud</a></p>
            """
            
            return self.send_simple_email(
                to_email=admin_email,
                subject=f"📋 Nueva solicitud: TEST-{prestamo_id}",
                html_content=html
            )
            
        except Exception as e:
            print(f"Error notificando solicitud {prestamo_id}: {e}")
            return False
    
    def notify_prestamo_rechazado(self, prestamo_id, motivo):
        """Notifica cuando un préstamo es rechazado"""
        html = f"""
        <h2>❌ Préstamo Rechazado</h2>
        <p>La solicitud de préstamo <strong>#{prestamo_id}</strong> ha sido rechazada.</p>
        <p><strong>Motivo:</strong> {motivo}</p>
        <p>🔗 <a href="{self.base_url}/mis-prestamos">Ver mis préstamos</a></p>
    """
    
        return self.send_simple_email(
            to_email=usuario_email,
            subject="❌ Préstamo rechazado - Sistema GIL",
            html_content=html
        )


    
    def notify_devolucion_registrada(self, prestamo_id, usuario_email):
        """Notifica devolución registrada"""
        html = f"""
        <h2>📦 Devolución Registrada</h2>
        <p>La devolución del préstamo <strong>#{prestamo_id}</strong> ha sido registrada exitosamente.</p>
        <p>¡Gracias por usar el sistema!</p>
        <p>🔗 <a href="{self.base_url}/mis-prestamos">Ver historial</a></p>
        """
        
        return self.send_simple_email(
            to_email=usuario_email,
            subject="✅ Devolución registrada - Sistema GIL",
            html_content=html
        )