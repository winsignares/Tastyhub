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
import sqlalchemy.exc
from app.utils.validaciones import allowed_file, validate_email, validate_password

# Endpoint para el registro de usuarios ✅
@api_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'GET':
            formato = request.args.get('format', 'html')
            
            if formato == 'json':
                return jsonify({
                    'status': 'success',
                    'message': 'Formulario de registro',
                    'required_fields': ['nombre', 'email', 'password', 'confirm_password'],
                    'optional_fields': ['descripcion', 'foto_perfil']
                }), 200
            else:
                return render_template('register-page.html')
        
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                nombre = data.get('nombre')
                email = data.get('email')
                password = data.get('password')
                confirm_password = data.get('confirm_password')
                descripcion = data.get('descripcion', '')
            else:
                nombre = request.form.get('nombre')
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                descripcion = request.form.get('descripcion', '')
            errores = {}
            
            if not nombre:
                errores['nombre'] = 'El nombre es obligatorio'
            
            if not email:
                errores['email'] = 'El email es obligatorio'
            elif not validate_email(email):
                errores['email'] = 'El formato del email es inválido'
            
            if not password:
                errores['password'] = 'La contraseña es obligatoria'
            elif not validate_password(password):
                errores['password'] = 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'
            
            if password != confirm_password:
                errores['confirm_password'] = 'Las contraseñas no coinciden'
            
            if errores:
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Hay errores en el formulario',
                        'errors': errores
                    }), 400
                else:
                    for campo, mensaje in errores.items():
                        flash(mensaje, 'error')
                    return redirect(url_for('api.register'))
            
            try:
                usuario_existente = Usuario.query.filter_by(email=email).first()
                if usuario_existente:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'El correo electrónico ya está registrado',
                            'error_type': 'duplicate_email'
                        }), 409  # 409 Conflict
                    else:
                        flash('El correo electrónico ya está registrado', 'error')
                        return redirect(url_for('api.register'))
                
                foto_perfil = 'default.jpg'
                if request.files and 'foto_perfil' in request.files:
                    file = request.files['foto_perfil']
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            filename = secure_filename(file.filename)
                            unique_filename = f"{uuid.uuid4().hex}_{filename}"
                            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'perfiles', unique_filename)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            
                            file.save(file_path)
                            foto_perfil = os.path.join('uploads', 'perfiles', unique_filename)
                        except Exception as e:
                            current_app.logger.error(f"Error al guardar imagen de perfil: {str(e)}")
                
                try:
                    nuevo_usuario = Usuario(
                        nombre=nombre,
                        email=email,
                        contrasena=password,
                        foto_perfil=foto_perfil,
                        descripcion=descripcion
                    )
                    
                    db.session.add(nuevo_usuario)
                    db.session.commit()
                    
                    # Iniciar sesión automáticamente (falta implementar)
                    # login_user(nuevo_usuario)
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'success',
                            'message': '¡Registro exitoso!',
                            'usuario': {
                                'id': nuevo_usuario.id,
                                'nombre': nuevo_usuario.nombre,
                                'email': nuevo_usuario.email
                            },
                            'redirect_url': url_for('api.login', _external=True)
                        }), 201  # 201 Created
                    else:
                        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
                        return redirect(url_for('api.login'))
                
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error de integridad al crear usuario: {str(e)}")
                    
                    if 'Duplicate entry' in str(e) and 'email' in str(e):
                        if request.is_json:
                            return jsonify({
                                'status': 'error',
                                'message': 'El correo electrónico ya está registrado',
                                'error_type': 'duplicate_email'
                            }), 409  # 409 Conflict
                        else:
                            flash('El correo electrónico ya está registrado', 'error')
                            return redirect(url_for('api.register'))
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al registrar usuario',
                            'error_type': 'database_error',
                            'details': str(e) if current_app.debug else 'Error en la base de datos'
                        }), 500
                    else:
                        flash('Error al registrar usuario', 'error')
                        return redirect(url_for('api.register'))
                
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error al crear usuario: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al registrar usuario',
                            'error_type': 'server_error',
                            'details': str(e) if current_app.debug else 'Error interno del servidor'
                        }), 500
                    else:
                        flash('Error al registrar usuario', 'error')
                        return redirect(url_for('api.register'))
            
            except Exception as e:
                current_app.logger.error(f"Error general en el registro: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al procesar la solicitud',
                        'error_type': 'server_error',
                        'details': str(e) if current_app.debug else 'Error interno del servidor'
                    }), 500
                else:
                    flash('Error al procesar la solicitud', 'error')
                    return redirect(url_for('api.register'))
    
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general en endpoint register: {str(e)}")
        
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.register'))

# Endpoint para el inicio de sesión de usuarios ✅
@api_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            # Determinar el formato de respuesta
            formato = request.args.get('format', 'html')
            
            if formato == 'json':
                return jsonify({
                    'status': 'success',
                    'message': 'Formulario de inicio de sesión',
                    'required_fields': ['email', 'password']
                }), 200
            else:
                return render_template('iniciar-sesion-page.html')
        
        if request.method == 'POST':
            # Determinar si es JSON o form-data
            if request.is_json:
                data = request.get_json()
                email = data.get('email')
                password = data.get('password')
            else:
                email = request.form.get('email')
                password = request.form.get('password')
            
            # Validaciones básicas
            errores = {}
            
            if not email:
                errores['email'] = 'El email es obligatorio'
            
            if not password:
                errores['password'] = 'La contraseña es obligatoria'
            
            if errores:
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Hay errores en el formulario',
                        'errors': errores
                    }), 400
                else:
                    for campo, mensaje in errores.items():
                        flash(mensaje, 'error')
                    return redirect(url_for('api.login'))
            
            try:
                # Buscar usuario por email
                usuario = Usuario.query.filter_by(email=email).first()
                
                if not usuario or not usuario.check_password(password):
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Credenciales inválidas',
                            'error_type': 'invalid_credentials'
                        }), 401
                    else:
                        flash('Credenciales inválidas', 'error')
                        return redirect(url_for('api.login'))
                
                # Login exitoso
                login_user(usuario)
                
                if request.is_json:
                    return jsonify({
                        'status': 'success',
                        'message': '¡Inicio de sesión exitoso!',
                        'usuario': {
                            'id': usuario.id,
                            'nombre': usuario.nombre,
                            'email': usuario.email
                        },
                        'redirect_url': url_for('main.index', _external=True)
                    }), 200
                else:
                    flash('¡Inicio de sesión exitoso!', 'success')
                    return redirect(url_for('main.index'))
            
            except Exception as e:
                current_app.logger.error(f"Error al iniciar sesión: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al iniciar sesión',
                        'error_type': 'server_error',
                        'details': str(e) if current_app.debug else 'Error interno del servidor'
                    }), 500
                else:
                    flash('Error al iniciar sesión', 'error')
                    return redirect(url_for('api.login'))
    
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general en endpoint login: {str(e)}")
        
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.login'))

@api_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('api.login'))

# Endpoint para la recuperación de contraseña ✅
@api_bp.route('/auth/recuperar-password', methods=['GET', 'POST'])
def recuperar_password():
    try:
        if request.method == 'GET':
            # Determinar el formato de respuesta
            formato = request.args.get('format', 'html')
            
            if formato == 'json':
                return jsonify({
                    'status': 'success',
                    'message': 'Formulario de recuperación de contraseña',
                    'required_fields': ['email']
                }), 200
            else:
                return render_template('olvidar-contraseña-page.html')
        
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                email = data.get('email')
            else:
                email = request.form.get('email')
            
            # Validación del email
            if not email:
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'El correo electrónico es obligatorio',
                        'error_type': 'validation_error',
                        'errors': {'email': 'El correo electrónico es obligatorio'}
                    }), 400
                else:
                    flash('Por favor, ingresa tu correo electrónico', 'error')
                    return redirect(url_for('api.recuperar_password'))
            
            try:
                usuario = Usuario.query.filter_by(email=email).first()
                if usuario:
                    try:
                        # Generar token para restablecer contraseña
                        expiracion = datetime.utcnow() + timedelta(hours=1)
                        reset_token = jwt.encode(
                            {'reset_password': usuario.id, 'exp': expiracion},
                            current_app.config['SECRET_KEY'],
                            algorithm='HS256'
                        )
                        
                        reset_url = url_for('api.reset_password', token=reset_token, _external=True)
                        enviar_email_recuperacion(usuario.email, reset_url)
                        
                        current_app.logger.info(f"Email de recuperación enviado a: {email}")
                    except Exception as e:
                        current_app.logger.error(f"Error al enviar email de recuperación a {email}: {str(e)}")
                else:
                    current_app.logger.info(f"Intento de recuperación para un email no registrado: {email}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'success',
                        'message': 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña'
                    }), 200
                else:
                    flash('Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña', 'info')
                    return redirect(url_for('api.login'))
                
            except Exception as e:
                current_app.logger.error(f"Error al procesar solicitud de recuperación para {email}: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'success',
                        'message': 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña'
                    }), 200
                else:
                    flash('Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña', 'info')
                    return redirect(url_for('api.login'))
    
    except Exception as e:
        current_app.logger.error(f"Error general en endpoint recuperar_password: {str(e)}")
        
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.recuperar_password'))

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
        return render_template('olvidar-contraseña-page.html')  
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Por favor, completa todos los campos', 'error')
            return render_template('olvidar-contraseña-page.html')  
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('olvidar-contraseña-page.html')  
        
        # Actualizar contraseña
        usuario.set_password(password)
        db.session.commit()
        
        flash('Tu contraseña ha sido actualizada correctamente', 'success')
        return redirect(url_for('api.login'))