from flask import request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
import os
import uuid
from werkzeug.utils import secure_filename
from app.models import Usuario, Receta
from app.config.db import db
from . import api_bp
from app.utils.validaciones import allowed_file

@api_bp.route('/usuarios/<int:usuario_id>')
def ver_perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    recetas = Receta.query.filter_by(id_usuario=usuario_id).order_by(Receta.fecha_creacion.desc()).all()
    
    es_seguidor = False
    if current_user.is_authenticated:
        es_seguidor = current_user.is_following(usuario)
    
    return render_template('perfil-page.html', 
                           usuario=usuario, 
                           recetas=recetas, 
                           es_seguidor=es_seguidor,
                           total_seguidores=usuario.seguidores.count(),
                           total_seguidos=usuario.seguidos.count())

@api_bp.route('/usuarios/editar-perfil', methods=['GET', 'POST'])
# @login_required
def editar_perfil():
    if request.method == 'GET':
        return render_template('perfil-page.html', usuario=current_user)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return redirect(url_for('api.editar_perfil'))
        
        # Actualizar datos del usuario
        current_user.nombre = nombre
        current_user.descripcion = descripcion
        
        # Procesar la foto de perfil si se proporcionó
        if 'foto_perfil' in request.files:
            file = request.files['foto_perfil']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generar un nombre único para el archivo
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'perfiles', unique_filename)
                
                # Asegurarse de que la carpeta exista
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                
                # Eliminar la foto anterior si no es la default
                if current_user.foto_perfil != 'default.jpg':
                    try:
                        old_file_path = os.path.join(current_app.static_folder, current_user.foto_perfil)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    except Exception as e:
                        current_app.logger.error(f"Error al eliminar foto anterior: {str(e)}")
                
                current_user.foto_perfil = os.path.join('uploads', 'perfiles', unique_filename)
        
        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('api.ver_perfil', usuario_id=current_user.id))

@api_bp.route('/usuarios/<int:usuario_id>/seguir', methods=['POST'])
# @login_required
def seguir_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.id == current_user.id:
        flash('No puedes seguirte a ti mismo', 'error')
        return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))
    
    if current_user.seguir(usuario):
        db.session.commit()
        flash(f'Ahora sigues a {usuario.nombre}', 'success')
    else:
        flash('Ya sigues a este usuario', 'info')
    
    return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))

@api_bp.route('/usuarios/<int:usuario_id>/dejar-de-seguir', methods=['POST'])
# @login_required
def dejar_de_seguir(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if current_user.dejar_de_seguir(usuario):
        db.session.commit()
        flash(f'Has dejado de seguir a {usuario.nombre}', 'info')
    else:
        flash('No sigues a este usuario', 'info')
    
    return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))

@api_bp.route('/usuarios/<int:usuario_id>/seguidores')
def ver_seguidores(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    seguidores = usuario.get_seguidores()
    
    return render_template('seguidores.html', 
                           usuario=usuario, 
                           seguidores=seguidores,
                           es_seguidor=True if current_user.is_authenticated else False)

@api_bp.route('/usuarios/<int:usuario_id>/siguiendo')
def ver_siguiendo(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    siguiendo = usuario.get_seguidos()
    
    return render_template('siguiendo.html', 
                           usuario=usuario, 
                           siguiendo=siguiendo,
                           es_seguidor=True if current_user.is_authenticated else False)