from flask import request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from email_validator import validate_email, EmailNotValidError
import re
from app.models.usuario import Usuario
from app.config.db import db
from . import api_bp

@api_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'GET':
        return render_template('register-page.html')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Lista para almacenar errores
            errores = []
            
            # Validación de nombre
            if not nombre:
                errores.append('El nombre es obligatorio')
            elif len(nombre) < 2:
                errores.append('El nombre debe tener al menos 2 caracteres')
            elif len(nombre) > 100:
                errores.append('El nombre no puede tener más de 100 caracteres')
            
            # Validación de email
            if not email:
                errores.append('El email es obligatorio')
            else:
                try:
                    # Validar formato del email
                    validate_email(email)
                    
                    # Verificar si el email ya existe
                    usuario_existente = Usuario.query.filter_by(email=email).first()
                    if usuario_existente:
                        errores.append('Este email ya está registrado')
                        
                except EmailNotValidError:
                    errores.append('El formato del email no es válido')
            
            # Validación de contraseña
            if not password:
                errores.append('La contraseña es obligatoria')
            elif len(password) < 6:
                errores.append('La contraseña debe tener al menos 6 caracteres')
            elif len(password) > 128:
                errores.append('La contraseña no puede tener más de 128 caracteres')
            else:
                # Validar que la contraseña tenga al menos una letra y un número
                if not re.search(r'[A-Za-z]', password):
                    errores.append('La contraseña debe contener al menos una letra')
                if not re.search(r'\d', password):
                    errores.append('La contraseña debe contener al menos un número')
            
            # Validación de confirmación de contraseña
            if not confirm_password:
                errores.append('Debes confirmar tu contraseña')
            elif password != confirm_password:
                errores.append('Las contraseñas no coinciden')
            
            # Si hay errores, mostrarlos
            if errores:
                for error in errores:
                    flash(error, 'error')
                return render_template('register-page.html', 
                                     nombre=nombre, 
                                     email=email)
            
            try:
                # Crear el nuevo usuario usando tu modelo existente
                nuevo_usuario = Usuario(
                    nombre=nombre,
                    email=email,
                    contrasena=password,  # El modelo ya maneja el hash en __init__
                    foto_perfil='default.jpg',
                    descripcion=''
                )
                
                db.session.add(nuevo_usuario)
                db.session.commit()
                
                # Iniciar sesión automáticamente después del registro
                login_user(nuevo_usuario)
                
                flash('¡Cuenta creada exitosamente! Bienvenido/a a Recetas Sencillas', 'success')
                return redirect(url_for('main.index'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error al crear usuario: {str(e)}")
                flash('Ocurrió un error al crear la cuenta. Por favor, intenta nuevamente.', 'error')
                return render_template('register-page.html', 
                                     nombre=nombre, 
                                     email=email)
                
        except Exception as e:
            current_app.logger.error(f"Error general en registro: {str(e)}")
            flash('Ocurrió un error inesperado. Por favor, intenta nuevamente.', 'error')
            return render_template('register-page.html')

@api_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'GET':
        return render_template('Iniciar-sesion-page.html')
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            # Validaciones básicas< 
            if not email:
                flash('El email es obligatorio', 'error')
                return render_template('Iniciar-sesion-page.html')
            
            if not password:
                flash('La contraseña es obligatoria', 'error')
                return render_template('Iniciar-sesion-page.html', email=email)
            
            # Buscar usuario
            usuario = Usuario.query.filter_by(email=email).first()  
            
            if usuario and usuario.check_password(password):
                login_user(usuario, remember=remember)
                
                # Redirigir a la página que intentaba acceder o al inicio
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.index'))
            else:
                flash('Email o contraseña incorrectos', 'error')
                return render_template('Iniciar-sesion-page.html', email=email)
                
        except Exception as e:
            current_app.logger.error(f"Error en login: {str(e)}")
            flash('Ocurrió un error al iniciar sesión. Por favor, intenta nuevamente.', 'error')
            return render_template('Iniciar-sesion-page.html')

@api_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('main.index'))

@api_bp.route('/auth/verificar-email')
def verificar_email():
    """Endpoint para verificar si un email ya está registrado (AJAX)"""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'disponible': False, 'mensaje': 'Email requerido'})
    
    try:
        validate_email(email)
        usuario_existente = Usuario.query.filter_by(email=email).first()
        
        if usuario_existente:
            return jsonify({'disponible': False, 'mensaje': 'Este email ya está registrado'})
        else:
            return jsonify({'disponible': True, 'mensaje': 'Email disponible'})
            
    except EmailNotValidError:
        return jsonify({'disponible': False, 'mensaje': 'Formato de email inválido'})