"""
Notificador de emails PROFESIONAL - Sistema GIL
Plantillas HTML mejoradas para notificaciones automáticas
"""
from flask_mail import Message
from flask import current_app
import os
import datetime

class EmailNotifier:
    """Enviador profesional de emails - Sistema GIL"""
    
    def __init__(self, mail, db):
        self.mail = mail
        self.db = db
        self.base_url = os.getenv('SISTEMA_URL', 'http://localhost:5000')
        print(f"✅ EmailNotifier Pro inicializado - Base URL: {self.base_url}")
    
    def send_simple_email(self, to_email, subject, html_content):
        """Envía email simple"""
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER') if current_app else None
            )
            self.mail.send(msg)
            print(f"📧 EMAIL ENVIADO a {to_email}: {subject}")
            return True
        except Exception as e:
            print(f"❌ Error email a {to_email}: {e}")
            return False
    
    # ================= PLANTILLAS DE ESTILO =================
    
    def _get_email_template(self, title, content, tipo="info"):
        """Plantilla base para todos los emails"""
        
        colores = {
            "info": {"primary": "#667eea", "secondary": "#764ba2"},
            "success": {"primary": "#10b981", "secondary": "#059669"},
            "warning": {"primary": "#f59e0b", "secondary": "#d97706"},
            "danger": {"primary": "#ef4444", "secondary": "#dc2626"}
        }
        
        color = colores.get(tipo, colores["info"])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - Sistema GIL</title>
            <style>
                /* ESTILOS BASE */
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #1e293b;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, {color['primary']} 0%, {color['secondary']} 100%);
                }}
                .email-container {{
                    max-width: 650px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
                }}
                .email-header {{
                    background: linear-gradient(135deg, {color['primary']} 0%, {color['secondary']} 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                    position: relative;
                }}
                .email-header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    background: rgba(255,255,255,0.3);
                }}
                .email-header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .email-header p {{
                    margin: 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .email-body {{
                    padding: 40px 30px;
                }}
                .email-footer {{
                    background: #f8fafc;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                }}
                .badge {{
                    display: inline-block;
                    padding: 6px 16px;
                    background: {color['primary']}15;
                    color: {color['primary']};
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 600;
                    margin: 5px;
                    border: 1px solid {color['primary']}30;
                }}
                .info-card {{
                    background: #f8fafc;
                    border-radius: 12px;
                    padding: 25px;
                    margin: 25px 0;
                    border-left: 4px solid {color['primary']};
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .info-item {{
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
                .info-label {{
                    font-size: 13px;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 600;
                    margin-bottom: 5px;
                }}
                .info-value {{
                    font-size: 16px;
                    color: #1e293b;
                    font-weight: 500;
                }}
                .action-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, {color['primary']} 0%, {color['secondary']} 100%);
                    color: white;
                    padding: 14px 32px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 15px;
                    transition: transform 0.2s, box-shadow 0.2s;
                    box-shadow: 0 4px 12px {color['primary']}40;
                }}
                .action-button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px {color['primary']}60;
                }}
                .warning-box {{
                    background: #fff7ed;
                    border-left: 4px solid #f59e0b;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 25px 0;
                }}
                .signature {{
                    margin-top: 40px;
                    padding-top: 25px;
                    border-top: 1px solid #e2e8f0;
                    color: #64748b;
                    font-size: 14px;
                }}
                @media (max-width: 600px) {{
                    .email-container {{
                        margin: 20px;
                        border-radius: 12px;
                    }}
                    .email-header, .email-body {{
                        padding: 25px 20px;
                    }}
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <h1>{title}</h1>
                    <p>Sistema de Gestión Integral de Laboratorios</p>
                </div>
                
                <div class="email-body">
                    {content}
                </div>
                
                <div class="email-footer">
                    <div style="margin-bottom: 20px;">
                        <span class="badge">Centro Minero</span>
                        <span class="badge">SENA</span>
                        <span class="badge">Sistema GIL</span>
                    </div>
                    <p style="margin: 0 0 10px 0; color: #475569; font-size: 14px;">
                        📍 Sogamoso, Boyacá · 📧 gil.soporte@centrominero.edu.co
                    </p>
                    <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                        Este es un correo automático. Por favor no responder directamente.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # ================= NOTIFICACIONES PROFESIONALES =================
    
    def notify_prestamo_aprobado(self, prestamo_id):
        """Notificación CUANDO SE APRUEBA PRÉSTAMO - VERSIÓN PRO"""
        try:
            query = """
                SELECT p.id, p.codigo, p.fecha, p.fecha_devolucion_programada,
                       p.proposito, p.observaciones,
                       e.nombre as equipo_nombre, e.codigo_interno, e.marca, e.modelo,
                       e.especificaciones_tecnicas,
                       CONCAT(u.nombres, ' ', u.apellidos) as usuario,
                       u.email,
                       CONCAT(ua.nombres, ' ', ua.apellidos) as autorizador,
                       ua.email as email_autorizador,
                       l.nombre as laboratorio, l.ubicacion
                FROM prestamos p
                JOIN equipos e ON p.id_equipo = e.id
                JOIN usuarios u ON p.id_usuario_solicitante = u.id
                JOIN usuarios ua ON p.id_usuario_autorizador = ua.id
                LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
                WHERE p.id = %s AND u.email IS NOT NULL
            """
            data = self.db.obtener_uno(query, (prestamo_id,))
            
            if not data:
                print(f"⚠️ No se encontró préstamo {prestamo_id} o usuario sin email")
                return False
            
            # Formatear fechas
            fecha_prestamo = data['fecha'].strftime('%d/%m/%Y %H:%M') if data['fecha'] else 'N/A'
            fecha_devolucion = data['fecha_devolucion_programada'].strftime('%d/%m/%Y %H:%M') if data['fecha_devolucion_programada'] else 'N/A'
            
            # Contenido del email
            content = f"""
            <h2 style="color: #1e293b; margin-top: 0;">¡Hola {data['usuario']}!</h2>
            <p style="font-size: 16px; color: #475569;">
                Tu solicitud de préstamo ha sido <strong>aprobada exitosamente</strong>. 
                A continuación encuentras todos los detalles:
            </p>
            
            <div class="info-card">
                <h3 style="color: #059669; margin-top: 0;">📦 Equipo Asignado</h3>
                <div style="font-size: 20px; font-weight: 600; color: #1e293b; margin: 10px 0;">
                    {data['equipo_nombre']}
                </div>
                <div style="color: #64748b; margin-bottom: 15px;">
                    {data['marca']} · {data['modelo']}
                </div>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Código Interno</div>
                        <div class="info-value">{data['codigo_interno']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Código Préstamo</div>
                        <div class="info-value">{data['codigo']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Ubicación</div>
                        <div class="info-value">{data['laboratorio'] or 'Por asignar'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Autorizado por</div>
                        <div class="info-value">{data['autorizador']}</div>
                    </div>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Fecha de Préstamo</div>
                    <div class="info-value">{fecha_prestamo}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Fecha de Devolución</div>
                    <div class="info-value">{fecha_devolucion}</div>
                </div>
            </div>
            
            <div class="warning-box">
                <h4 style="color: #d97706; margin-top: 0;">⚠️ Instrucciones Importantes</h4>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #78350f;">
                    <li>Presenta este correo o tu documento de identidad al recoger el equipo</li>
                    <li>El equipo debe recogerse en el laboratorio asignado</li>
                    <li>La devolución debe ser puntual para evitar sanciones</li>
                    <li>Reporta cualquier anomalía inmediatamente</li>
                </ul>
            </div>
            
            <div style="margin: 30px 0;">
                <p><strong>Propósito registrado:</strong></p>
                <div style="background: #f1f5f9; padding: 15px; border-radius: 8px; color: #475569;">
                    {data['proposito']}
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="{self.base_url}/mis-prestamos" class="action-button">
                    📋 Ver Mis Préstamos
                </a>
                <p style="color: #64748b; font-size: 14px; margin-top: 15px;">
                    Accede a tu panel personal para ver todos tus préstamos activos
                </p>
            </div>
            
            <div class="signature">
                <p style="margin: 0 0 10px 0;">
                    <strong>Para consultas o asistencia:</strong><br>
                    Contacta a {data['autorizador']} ({data['email_autorizador'] or 'N/A'})
                </p>
            </div>
            """
            
            # Crear email completo
            html = self._get_email_template(
                "✅ Préstamo Aprobado",
                content,
                tipo="success"
            )
            
            return self.send_simple_email(
                to_email=data['email'],
                subject=f"✅ Préstamo aprobado: {data['equipo_nombre'][:50]}",
                html_content=html
            )
            
        except Exception as e:
            print(f"❌ Error notificando préstamo {prestamo_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def notify_prestamo_solicitado(self, prestamo_id):
        """Notifica a ADMINS cuando hay nueva solicitud - VERSIÓN PRO"""
        try:
            # Datos detallados del préstamo
            query = """
                SELECT p.id, p.codigo, p.proposito, p.fecha_solicitud, 
                       p.fecha_devolucion_programada, p.observaciones,
                       e.nombre as equipo_nombre, e.codigo_interno, e.marca, e.modelo,
                       e.estado as estado_equipo, e.valor_adquisicion,
                       CONCAT(u.nombres, ' ', u.apellidos) as usuario,
                       u.documento, u.email as email_usuario, u.telefono,
                       l.nombre as laboratorio, l.ubicacion
                FROM prestamos p
                JOIN equipos e ON p.id_equipo = e.id
                JOIN usuarios u ON p.id_usuario_solicitante = u.id
                LEFT JOIN laboratorios l ON e.id_laboratorio = l.id
                WHERE p.id = %s
            """
            prestamo = self.db.obtener_uno(query, (prestamo_id,))
            
            if not prestamo:
                print(f"⚠️ No se encontró préstamo {prestamo_id}")
                return False
            
            # Emails de todos los administradores
            admin_query = """
                SELECT email, CONCAT(nombres, ' ', apellidos) as nombre 
                FROM usuarios 
                WHERE id_rol = 1 
                AND email IS NOT NULL 
                AND email != ''
                AND estado = 'activo'
            """
            admins = self.db.ejecutar_query(admin_query) or []
            
            if not admins:
                print("⚠️ No hay administradores con email configurado")
                return False
            
            # Formatear fechas
            fecha_solicitud = prestamo['fecha_solicitud'].strftime('%d/%m/%Y %H:%M') if prestamo['fecha_solicitud'] else 'N/A'
            fecha_devolucion = prestamo['fecha_devolucion_programada'].strftime('%d/%m/%Y %H:%M') if prestamo['fecha_devolucion_programada'] else 'N/A'
            
            # Contenido del email
            content = f"""
            <h2 style="color: #1e293b; margin-top: 0;">Nueva Solicitud Requiere Revisión</h2>
            <p style="font-size: 16px; color: #475569;">
                Se ha registrado una nueva solicitud de préstamo en el sistema. 
                Por favor revisa los detalles y toma la acción correspondiente.
            </p>
            
            <div class="info-card">
                <h3 style="color: #6366f1; margin-top: 0;">📋 Resumen de la Solicitud</h3>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Código Solicitud</div>
                        <div class="info-value">
                            <strong>{prestamo['codigo']}</strong>
                            <div style="font-size: 12px; color: #64748b;">ID: #{prestamo['id']}</div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Estado</div>
                        <div class="info-value">
                            <span style="color: #f59e0b; font-weight: 600;">PENDIENTE</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Fecha Solicitud</div>
                        <div class="info-value">{fecha_solicitud}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Fecha Devolución</div>
                        <div class="info-value">{fecha_devolucion}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin: 30px 0;">
                <h3 style="color: #475569; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
                    🧑‍🔬 Información del Solicitante
                </h3>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Nombre Completo</div>
                        <div class="info-value">{prestamo['usuario']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Documento</div>
                        <div class="info-value">{prestamo['documento']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Email</div>
                        <div class="info-value">{prestamo['email_usuario'] or 'No disponible'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Teléfono</div>
                        <div class="info-value">{prestamo['telefono'] or 'No disponible'}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin: 30px 0;">
                <h3 style="color: #475569; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
                    🔬 Información del Equipo
                </h3>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 20px; font-weight: 600; color: #0369a1; margin-bottom: 10px;">
                        {prestamo['equipo_nombre']}
                    </div>
                    <div style="color: #475569; margin-bottom: 15px;">
                        {prestamo['marca']} · {prestamo['modelo']}
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Código Interno</div>
                            <div class="info-value">{prestamo['codigo_interno']}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Estado Equipo</div>
                            <div class="info-value">{prestamo['estado_equipo'].upper()}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Valor</div>
                            <div class="info-value">${prestamo['valor_adquisicion']:,.0f}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Ubicación</div>
                            <div class="info-value">{prestamo['laboratorio'] or 'No asignado'}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin: 30px 0;">
                <h3 style="color: #475569; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">
                    📝 Detalles de la Solicitud
                </h3>
                <div style="background: #fefce8; padding: 20px; border-radius: 10px;">
                    <p><strong>Propósito:</strong></p>
                    <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0 20px 0;">
                        {prestamo['proposito']}
                    </div>
                    
                    {f'<p><strong>Observaciones:</strong></p><div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">{prestamo["observaciones"]}</div>' if prestamo['observaciones'] else ''}
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="{self.base_url}/prestamos/{prestamo_id}" class="action-button">
                    🔍 Revisar Solicitud Completa
                </a>
                <p style="color: #64748b; font-size: 14px; margin-top: 15px;">
                    Accede directamente al sistema para aprobar o rechazar esta solicitud
                </p>
            </div>
            
            <div class="warning-box">
                <h4 style="color: #d97706; margin-top: 0;">📋 Acciones Requeridas</h4>
                <ol style="margin: 10px 0 0 0; padding-left: 20px; color: #78350f;">
                    <li>Revisar disponibilidad del equipo</li>
                    <li>Verificar conflicto de horarios</li>
                    <li>Evaluar propósito de la solicitud</li>
                    <li>Aprobar o rechazar según corresponda</li>
                </ol>
            </div>
            """
            
            # Crear email completo
            html = self._get_email_template(
                "📋 Nueva Solicitud de Préstamo",
                content,
                tipo="info"
            )
            
            # Enviar a todos los administradores
            results = []
            admin_emails = []
            
            for admin in admins:
                if admin['email']:
                    admin_emails.append(admin['email'])
                    success = self.send_simple_email(
                        to_email=admin['email'],
                        subject=f"📋 Nueva solicitud: {prestamo['equipo_nombre'][:40]}...",
                        html_content=html
                    )
                    results.append(success)
            
            print(f"📧 Notificación enviada a {len(admin_emails)} administradores: {', '.join(admin_emails)}")
            return any(results)
            
        except Exception as e:
            print(f"❌ Error notificando solicitud {prestamo_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
        """Notifica cuando se completa mantenimiento - VERSIÓN PRO"""
        try:
            # Obtener datos del mantenimiento
            query = """
                SELECT hm.id, hm.descripcion, hm.fecha_inicio, hm.fecha_fin,
                       hm.costo_mantenimiento, hm.observaciones, hm.estado,
                       e.nombre as equipo_nombre, e.codigo_interno,
                       tm.nombre as tipo_mantenimiento,
                       CONCAT(u.nombres, ' ', u.apellidos) as tecnico
                FROM historial_mantenimiento hm
                JOIN equipos e ON hm.id_equipo = e.id
                JOIN tipos_mantenimiento tm ON hm.id_tipo_mantenimiento = tm.id
                JOIN usuarios u ON hm.tecnico_responsable_id = u.id
                WHERE hm.id = %s
            """
            mantenimiento = self.db.obtener_uno(query, (mantenimiento_id,))
            
            if not mantenimiento:
                return False
            
            # Formatear fechas
            fecha_inicio = mantenimiento['fecha_inicio'].strftime('%d/%m/%Y') if mantenimiento['fecha_inicio'] else 'N/A'
            fecha_fin = mantenimiento['fecha_fin'].strftime('%d/%m/%Y') if mantenimiento['fecha_fin'] else 'N/A'
            costo = f"${mantenimiento['costo_mantenimiento']:,.0f}" if mantenimiento['costo_mantenimiento'] else 'Sin costo'
            
            content = f"""
            <h2 style="color: #1e293b; margin-top: 0;">¡Mantenimiento Completado!</h2>
            <p style="font-size: 16px; color: #475569;">
                El mantenimiento ha sido registrado como <strong>completado exitosamente</strong>.
            </p>
            
            <div class="info-card">
                <h3 style="color: #059669; margin-top: 0;">🔧 Detalles del Mantenimiento</h3>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">ID Mantenimiento</div>
                        <div class="info-value">#{mantenimiento['id']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Estado</div>
                        <div class="info-value">
                            <span style="color: #059669; font-weight: 600;">COMPLETADO</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Tipo</div>
                        <div class="info-value">{mantenimiento['tipo_mantenimiento']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Costo</div>
                        <div class="info-value">{costo}</div>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Fecha Inicio</div>
                        <div class="info-value">{fecha_inicio}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Fecha Fin</div>
                        <div class="info-value">{fecha_fin}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin: 25px 0;">
                <h3 style="color: #475569;">📦 Equipo Intervenido</h3>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 18px; font-weight: 600; color: #0369a1;">
                        {mantenimiento['equipo_nombre']}
                    </div>
                    <div style="color: #475569; margin-top: 5px;">
                        Código: {mantenimiento['codigo_interno']}
                    </div>
                </div>
            </div>
            
            <div style="margin: 25px 0;">
                <h3 style="color: #475569;">👨‍🔬 Técnico Responsable</h3>
                <div style="background: #fefce8; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 18px; font-weight: 600; color: #d97706;">
                        {mantenimiento['tecnico']}
                    </div>
                    <p style="color: #475569; margin: 10px 0 0 0;">
                        Mantenimiento realizado y documentado exitosamente
                    </p>
                </div>
            </div>
            
            {f'''
            <div style="margin: 25px 0;">
                <h3 style="color: #475569;">📝 Observaciones</h3>
                <div style="background: #f8fafc; padding: 20px; border-radius: 10px;">
                    {mantenimiento['observaciones']}
                </div>
            </div>
            ''' if mantenimiento['observaciones'] else ''}
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="{self.base_url}/mantenimiento" class="action-button">
                    📊 Ver Historial de Mantenimientos
                </a>
                <p style="color: #64748b; font-size: 14px; margin-top: 15px;">
                    Accede al módulo de mantenimiento para ver todos los registros
                </p>
            </div>
            
            <div class="signature">
                <p style="margin: 0;">
                    <strong>¡Gracias por tu trabajo!</strong><br>
                    El mantenimiento preventivo prolonga la vida útil de los equipos.
                </p>
            </div>
            """
            
            html = self._get_email_template(
                "✅ Mantenimiento Completado",
                content,
                tipo="success"
            )
            
            return self.send_simple_email(
                to_email=tecnico_email,
                subject=f"✅ Mantenimiento #{mantenimiento_id} completado",
                html_content=html
            )
            
        except Exception as e:
            print(f"❌ Error notificando mantenimiento {mantenimiento_id}: {e}")
            return False
    
    def notify_devolucion_registrada(self, prestamo_id, usuario_email):
        """Notifica devolución registrada - VERSIÓN PRO"""
        try:
            # Obtener datos de la devolución
            query = """
                SELECT p.id, p.codigo, p.fecha, p.fecha_devolucion_real,
                    p.observaciones_devolucion,
                    e.nombre as equipo_nombre, e.codigo_interno,
                    CONCAT(u.nombres, ' ', u.apellidos) as usuario,
                    CONCAT(ur.nombres, ' ', ur.apellidos) as receptor
                FROM prestamos p
                JOIN equipos e ON p.id_equipo = e.id
                JOIN usuarios u ON p.id_usuario_solicitante = u.id
                LEFT JOIN usuarios ur ON p.id_usuario_receptor = ur.id
                WHERE p.id = %s
            """
            devolucion = self.db.obtener_uno(query, (prestamo_id,))
            
            if not devolucion:
                return False
            
            # Formatear fechas
            fecha_devolucion = devolucion['fecha_devolucion_real'].strftime('%d/%m/%Y %H:%M') if devolucion['fecha_devolucion_real'] else datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            
            content = f"""
            <h2 style="color: #1e293b; margin-top: 0;">¡Devolución Registrada Exitosamente!</h2>
            <p style="font-size: 16px; color: #475569;">
                Hola {devolucion['usuario']}, hemos registrado la devolución del equipo.
                <strong>¡Gracias por tu responsabilidad!</strong>
            </p>
            
            <div class="info-card">
                <h3 style="color: #059669; margin-top: 0;">📦 Resumen de la Devolución</h3>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Código Préstamo</div>
                        <div class="info-value">{devolucion['codigo']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Estado</div>
                        <div class="info-value">
                            <span style="color: #059669; font-weight: 600;">DEVUELTO</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Fecha Devolución</div>
                        <div class="info-value">{fecha_devolucion}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Receptor</div>
                        <div class="info-value">{devolucion['receptor'] or 'Sistema automático'}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin: 25px 0; text-align: center;">
                <div style="display: inline-block; background: #e8f5e9; padding: 30px; border-radius: 50%;">
                    <span style="font-size: 48px; color: #059669;">✓</span>
                </div>
                <h3 style="color: #059669; margin-top: 20px;">Equipo Devuelto y Verificado</h3>
            </div>
            
            <div style="margin: 25px 0;">
                <h3 style="color: #475569;">🔬 Equipo Devuelto</h3>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center;">
                    <div style="font-size: 20px; font-weight: 600; color: #0369a1;">
                        {devolucion['equipo_nombre']}
                    </div>
                    <div style="color: #475569; margin-top: 10px;">
                        Código: {devolucion['codigo_interno']}
                    </div>
                </div>
            </div>
            
            {f'''
            <div style="margin: 25px 0;">
                <h3 style="color: #475569;">📝 Observaciones</h3>
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
                    {devolucion['observaciones_devolucion']}
                </div>
            </div>
            ''' if devolucion['observaciones_devolucion'] else ''}
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="{self.base_url}/mis-prestamos" class="action-button">
                    📋 Ver Mi Historial
                </a>
                <p style="color: #64748b; font-size: 14px; margin-top: 15px;">
                    Revisa tu historial completo de préstamos en el sistema
                </p>
            </div>
            
            <div class="signature">
                <p style="margin: 0; color: #475569;">
                    <strong>Tu contribución es valiosa:</strong><br>
                    El cuidado responsable de los equipos beneficia a toda la comunidad académica.
                </p>
            </div>
            """
            
            html = self._get_email_template(
                "✅ Devolución Completada",
                content,
                tipo="success"
            )
            
            return self.send_simple_email(
                to_email=usuario_email,
                subject=f"✅ Devolución registrada - {devolucion['equipo_nombre'][:40]}...",
                html_content=html
            )
            
        except Exception as e:
            print(f"❌ Error notificando devolución {prestamo_id}: {e}")
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