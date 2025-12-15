# Rutas para agregar a app.py - Sistema de Recuperación de Contraseña

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Solicitar restablecimiento de contraseña"""
    try:
        import secrets
        from datetime import datetime, timedelta
        
        email = request.json.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email requerido'}), 400
        
        # Buscar usuario por email
        query = "SELECT id, documento, nombres, apellidos, email FROM usuarios WHERE LOWER(email) = %s AND estado = 'activo'"
        usuario = db_manager.obtener_uno(query, (email,))
        
        # Por seguridad, siempre responder lo mismo aunque el email no exista
        if not usuario:
            return jsonify({
                'success': True, 
                'message': 'Si el correo está registrado, recibirá instrucciones en breve.'
            })
        
        # Generar token único y seguro
        token = secrets.token_urlsafe(32)
        expira_en = datetime.now() + timedelta(hours=1)  # Token válido por 1 hora
        
        # Guardar token en BD
        insert_query = """
            INSERT INTO password_reset_tokens (id_usuario, token, email, expira_en, ip_solicitud)
            VALUES (%s, %s, %s, %s, %s)
        """
        db_manager.ejecutar_comando(insert_query, (
            usuario['id'],
            token,
            email,
            expira_en,
            request.remote_addr
        ))
        
        # Construir URL de restablecimiento
        reset_url = f"{request.url_root}reset-password/{token}"
        
        # TODO: Enviar email con el enlace (implementar con SMTP)
        # Por ahora, solo registrar en logs
        print(f"=== TOKEN DE RESTABLECIMIENTO ===")
        print(f"Usuario: {usuario['nombres']} {usuario['apellidos']}")
        print(f"Email: {email}")
        print(f"URL: {reset_url}")
        print(f"Expira: {expira_en}")
        print(f"================================")
        
        # Log en sistema
        log_query = """
            INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
            VALUES ('auth', 'INFO', %s, %s, %s)
        """
        db_manager.ejecutar_comando(log_query, (
            f'Solicitud de restablecimiento de contraseña para {email}',
            usuario['id'],
            request.remote_addr
        ))
        
        return jsonify({
            'success': True,
            'message': 'Si el correo está registrado, recibirá instrucciones en breve.',
            'debug_url': reset_url if app.debug else None  # Solo en desarrollo
        })
        
    except Exception as e:
        print(f"Error en forgot_password: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error al procesar solicitud'}), 500


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Restablecer contraseña con token"""
    from datetime import datetime
    
    if request.method == 'GET':
        # Verificar que el token sea válido
        query = """
            SELECT t.id, t.id_usuario, t.email, t.expira_en, t.usado,
                   u.nombres, u.apellidos, u.documento
            FROM password_reset_tokens t
            JOIN usuarios u ON t.id_usuario = u.id
            WHERE t.token = %s AND t.usado = FALSE
        """
        token_data = db_manager.obtener_uno(query, (token,))
        
        if not token_data:
            flash('Token inválido o ya utilizado', 'error')
            return redirect(url_for('login'))
        
        # Verificar si expiró
        if datetime.now() > token_data['expira_en']:
            flash('El enlace ha expirado. Solicite uno nuevo.', 'error')
            return redirect(url_for('login'))
        
        # Mostrar formulario de nueva contraseña
        return render_template('reset_password.html', 
                             token=token,
                             email=token_data['email'],
                             nombre=f"{token_data['nombres']} {token_data['apellidos']}")
    
    # POST - Cambiar contraseña
    try:
        nueva_password = request.form.get('nueva_password', '').strip()
        confirmar_password = request.form.get('confirmar_password', '').strip()
        
        if not nueva_password or not confirmar_password:
            flash('Todos los campos son requeridos', 'error')
            return redirect(url_for('reset_password', token=token))
        
        if nueva_password != confirmar_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('reset_password', token=token))
        
        if len(nueva_password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return redirect(url_for('reset_password', token=token))
        
        # Verificar token nuevamente
        query = """
            SELECT t.id, t.id_usuario, t.email, t.expira_en, t.usado
            FROM password_reset_tokens t
            WHERE t.token = %s AND t.usado = FALSE
        """
        token_data = db_manager.obtener_uno(query, (token,))
        
        if not token_data:
            flash('Token inválido o ya utilizado', 'error')
            return redirect(url_for('login'))
        
        if datetime.now() > token_data['expira_en']:
            flash('El enlace ha expirado. Solicite uno nuevo.', 'error')
            return redirect(url_for('login'))
        
        # Hashear nueva contraseña
        import bcrypt
        password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Actualizar contraseña
        update_query = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
        db_manager.ejecutar_comando(update_query, (password_hash, token_data['id_usuario']))
        
        # Marcar token como usado
        mark_used_query = "UPDATE password_reset_tokens SET usado = TRUE WHERE id = %s"
        db_manager.ejecutar_comando(mark_used_query, (token_data['id'],))
        
        # Log de seguridad
        log_query = """
            INSERT INTO logs_sistema (modulo, nivel_log, mensaje, id_usuario, ip_address)
            VALUES ('auth', 'INFO', %s, %s, %s)
        """
        db_manager.ejecutar_comando(log_query, (
            f'Contraseña restablecida exitosamente para {token_data["email"]}',
            token_data['id_usuario'],
            request.remote_addr
        ))
        
        flash('Contraseña restablecida exitosamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Error en reset_password: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al restablecer contraseña. Intente nuevamente.', 'error')
        return redirect(url_for('reset_password', token=token))
