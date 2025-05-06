from flask import request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
import os
import uuid
from datetime import datetime, timedelta
import jwt
from werkzeug.utils import secure_filename
from app.models import Usuario
from app.config.db import db
from app.utils.email import enviar_email_recuperacion
from . import api_bp
from app.utils.validaciones import allowed_file

# Rutas de autenticación
@api_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register-page.html')  # Cambiar aquí
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones básicas
        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('api.register'))
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('api.register'))
        
        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('El correo electrónico ya está registrado', 'error')
            return redirect(url_for('api.register'))
        
        # Procesar la foto de perfil si se proporcionó
        foto_perfil = 'default.jpg'
        if 'foto_perfil' in request.files:
            file = request.files['foto_perfil']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generar un nombre único para el archivo
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'perfiles', unique_filename)
                
                # Asegurarse de que la carpeta exista
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                foto_perfil = os.path.join('uploads', 'perfiles', unique_filename)
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=password,
            foto_perfil=foto_perfil,
            descripcion=request.form.get('descripcion', '')
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('api.login'))

@api_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('iniciar-sesion-page.html')  # Cambiar aquí
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor, completa todos los campos', 'error')
            return redirect(url_for('api.login'))
        
        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not usuario.check_password(password):
            flash('Credenciales inválidas', 'error')
            return redirect(url_for('api.login'))
        
        # Login exitoso
        login_user(usuario)
        flash('¡Inicio de sesión exitoso!', 'success')
        return redirect(url_for('main.index'))

@api_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('api.login'))

@api_bp.route('/auth/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'GET':
        return render_template('register-page.html')  # Cambiar aquí
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Por favor, ingresa tu correo electrónico', 'error')
            return redirect(url_for('api.recuperar_password'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            # Por seguridad, no informamos si el email existe o no
            flash('Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña', 'info')
            return redirect(url_for('api.login'))
        
        # Generar token para restablecer contraseña
        expiracion = datetime.utcnow() + timedelta(hours=1)
        reset_token = jwt.encode(
            {'reset_password': usuario.id, 'exp': expiracion},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Enviar email con el token
        reset_url = url_for('api.reset_password', token=reset_token, _external=True)
        enviar_email_recuperacion(usuario.email, reset_url)
        
        flash('Se han enviado instrucciones para restablecer tu contraseña', 'info')
        return redirect(url_for('api.login'))

@api_bp.route('/auth/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        usuario_id = data['reset_password']
    except:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado', 'error')
        return redirect(url_for('api.recuperar_password'))
    
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('api.recuperar_password'))
    
    if request.method == 'GET':
        return render_template('olvidar-contraseña-page.html')  # Cambiar aquí
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Por favor, completa todos los campos', 'error')
            return render_template('olvidar-contraseña-page.html')  # Cambiar aquí
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('olvidar-contraseña-page.html')  # Cambiar aquí
        
        # Actualizar contraseña
        usuario.set_password(password)
        db.session.commit()
        
        flash('Tu contraseña ha sido actualizada correctamente', 'success')
        return redirect(url_for('api.login'))