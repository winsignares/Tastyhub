from flask import request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import Receta, Instruccion, Categoria, RecetaCategoria, Ingrediente, RecetaIngrediente, MeGusta
from app.config.db import db
from . import api_bp
from app.utils.validaciones import allowed_file

@api_bp.route('/recetas')
def listar_recetas():
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 12
    
    # Filtros
    categoria_id = request.args.get('categoria', type=int)
    busqueda = request.args.get('q', '')
    
    # Consulta base
    query = Receta.query
    
    # Aplicar filtros
    if categoria_id:
        categoria = Categoria.query.get(categoria_id)
        if categoria:
            query = query.join(RecetaCategoria).filter(RecetaCategoria.categoria_id == categoria_id)
    
    if busqueda:
        query = query.filter(Receta.titulo.like(f'%{busqueda}%'))
    
    # Ordenar por fecha de creación (más recientes primero)
    query = query.order_by(Receta.fecha_creacion.desc())
    
    # Paginar resultados
    recetas = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
    
    categorias = Categoria.query.all()
    
    return render_template('recetas.html', 
                           recetas=recetas, 
                           categorias=categorias,
                           categoria_actual=categoria_id,
                           busqueda=busqueda)

@api_bp.route('/recetas/<int:receta_id>')
def ver_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    instrucciones = Instruccion.query.filter_by(id_receta=receta_id).order_by(Instruccion.numero_paso).all()
    
    # Ingredientes de la receta
    ingredientes = db.session.query(RecetaIngrediente, Ingrediente) \
        .join(Ingrediente, RecetaIngrediente.ingredientes_id == Ingrediente.id) \
        .filter(RecetaIngrediente.receta_id == receta_id).all()
    
    # Verificar si el usuario actual ha dado me gusta
    usuario_dio_like = False
    if current_user.is_authenticated:
        usuario_dio_like = MeGusta.query.filter_by(receta_id=receta_id, ususario_id=current_user.id).first() is not None
    
    return render_template('receta.html', 
                           receta=receta, 
                           instrucciones=instrucciones,
                           ingredientes=ingredientes,
                           usuario_dio_like=usuario_dio_like,
                           total_likes=receta.contar_me_gustas())

@api_bp.route('/recetas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_receta():
    if request.method == 'GET':
        categorias = Categoria.query.all()
        ingredientes = Ingrediente.query.all()
        return render_template('nueva_receta.html', categorias=categorias, ingredientes=ingredientes)
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        tiempo_preparacion = request.form.get('tiempo_preparacion')
        
        if not titulo:
            flash('El título es obligatorio', 'error')
            return redirect(url_for('api.nueva_receta'))
        
        # Procesar la imagen de portada
        imagen_portada = None
        if 'imagen_portada' in request.files:
            archivo = request.files['imagen_portada']
            if archivo and archivo.filename != '' and allowed_file(archivo.filename):
                filename = secure_filename(archivo.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'recetas', unique_filename)
                
                # Asegurarse de que exista la carpeta
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                archivo.save(file_path)
                imagen_portada = os.path.join('uploads', 'recetas', unique_filename)
        
        # Crear nueva receta
        nueva_receta = Receta(
            id_usuario=current_user.id,
            titulo=titulo,
            descripcion=descripcion,
            imagen_portada=imagen_portada,
            tiempor_pre=tiempo_preparacion
        )
        
        db.session.add(nueva_receta)
        db.session.flush()  # Para obtener el ID de la receta
        
        # Procesar categorías seleccionadas
        categorias_ids = request.form.getlist('categorias')
        for cat_id in categorias_ids:
            cat_id = int(cat_id)
            receta_categoria = RecetaCategoria(receta_id=nueva_receta.id, categoria_id=cat_id)
            db.session.add(receta_categoria)
        
        # Procesar ingredientes
        ingredientes_ids = request.form.getlist('ingrediente_id')
        cantidades = request.form.getlist('cantidad')
        
        for i, ing_id in enumerate(ingredientes_ids):
            if ing_id and cantidades[i]:
                ingrediente = RecetaIngrediente(
                    receta_id=nueva_receta.id,
                    ingredientes_id=int(ing_id),
                    cantidad=int(cantidades[i])
                )
                db.session.add(ingrediente)
        
        # Procesar instrucciones
        instrucciones = request.form.getlist('instruccion')
        for i, instruccion_texto in enumerate(instrucciones, start=1):
            if instruccion_texto.strip():
                instruccion = Instruccion(
                    id_receta=nueva_receta.id,
                    numero_paso=i,
                    descripcion=instruccion_texto
                )
                db.session.add(instruccion)
        
        db.session.commit()
        flash('¡Receta creada exitosamente!', 'success')
        return redirect(url_for('api.ver_receta', receta_id=nueva_receta.id))

@api_bp.route('/recetas/<int:receta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    
    # Verificar que el usuario sea el autor de la receta
    if receta.id_usuario != current_user.id:
        flash('No tienes permiso para editar esta receta', 'error')
        return redirect(url_for('api.ver_receta', receta_id=receta_id))
    
    if request.method == 'GET':
        categorias = Categoria.query.all()
        ingredientes = Ingrediente.query.all()
        
        # Obtener categorías de la receta
        categorias_seleccionadas = [cat.id for cat in receta.categorias]
        
        # Obtener ingredientes de la receta
        ingredientes_receta = RecetaIngrediente.query.filter_by(receta_id=receta_id).all()
        
        # Obtener instrucciones de la receta
        instrucciones = Instruccion.query.filter_by(id_receta=receta_id).order_by(Instruccion.numero_paso).all()
        
        return render_template('editar_receta.html', 
                               receta=receta, 
                               categorias=categorias,
                               ingredientes=ingredientes,
                               categorias_seleccionadas=categorias_seleccionadas,
                               ingredientes_receta=ingredientes_receta,
                               instrucciones=instrucciones)
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        tiempo_preparacion = request.form.get('tiempo_preparacion')
        
        if not titulo:
            flash('El título es obligatorio', 'error')
            return redirect(url_for('api.editar_receta', receta_id=receta_id))
        
        # Actualizar datos básicos
        receta.titulo = titulo
        receta.descripcion = descripcion
        receta.tiempor_pre = tiempo_preparacion
        
        # Procesar la imagen de portada si se proporciona una nueva
        if 'imagen_portada' in request.files:
            archivo = request.files['imagen_portada']
            if archivo and archivo.filename != '' and allowed_file(archivo.filename):
                filename = secure_filename(archivo.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'recetas', unique_filename)
                
                # Asegurarse de que exista la carpeta
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                archivo.save(file_path)
                
                # Eliminar imagen anterior si existe
                if receta.imagen_portada:
                    try:
                        old_path = os.path.join(current_app.static_folder, receta.imagen_portada)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        current_app.logger.error(f"Error al eliminar imagen anterior: {str(e)}")
                
                receta.imagen_portada = os.path.join('uploads', 'recetas', unique_filename)
        
        # Actualizar categorías
        # Primero eliminar todas las categorías existentes
        RecetaCategoria.query.filter_by(receta_id=receta_id).delete()
        
        # Agregar las nuevas categorías
        categorias_ids = request.form.getlist('categorias')
        for cat_id in categorias_ids:
            receta_categoria = RecetaCategoria(receta_id=receta_id, categoria_id=int(cat_id))
            db.session.add(receta_categoria)
        
        # Actualizar ingredientes
        # Primero eliminar todos los ingredientes existentes
        RecetaIngrediente.query.filter_by(receta_id=receta_id).delete()
        
        # Agregar los nuevos ingredientes
        ingredientes_ids = request.form.getlist('ingrediente_id')
        cantidades = request.form.getlist('cantidad')
        
        for i, ing_id in enumerate(ingredientes_ids):
            if ing_id and cantidades[i]:
                ingrediente = RecetaIngrediente(
                    receta_id=receta_id,
                    ingredientes_id=int(ing_id),
                    cantidad=int(cantidades[i])
                )
                db.session.add(ingrediente)
        
        # Actualizar instrucciones
        # Primero eliminar todas las instrucciones existentes
        Instruccion.query.filter_by(id_receta=receta_id).delete()
        
        # Agregar las nuevas instrucciones
        instrucciones = request.form.getlist('instruccion')
        for i, instruccion_texto in enumerate(instrucciones, start=1):
            if instruccion_texto.strip():
                instruccion = Instruccion(
                    id_receta=receta_id,
                    numero_paso=i,
                    descripcion=instruccion_texto
                )
                db.session.add(instruccion)
        
        db.session.commit()
        flash('¡Receta actualizada exitosamente!', 'success')
        return redirect(url_for('api.ver_receta', receta_id=receta_id))

@api_bp.route('/recetas/<int:receta_id>/eliminar', methods=['POST'])
@login_required
def eliminar_receta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    
    # Verificar que el usuario sea el autor de la receta
    if receta.id_usuario != current_user.id:
        flash('No tienes permiso para eliminar esta receta', 'error')
        return redirect(url_for('api.ver_receta', receta_id=receta_id))
    
    # Eliminar la receta (las relaciones se eliminarán en cascada)
    db.session.delete(receta)
    db.session.commit()
    
    flash('Receta eliminada correctamente', 'success')
    return redirect(url_for('api.listar_recetas'))

@api_bp.route('/recetas/<int:receta_id>/me-gusta', methods=['POST'])
@login_required
def dar_me_gusta(receta_id):
    receta = Receta.query.get_or_404(receta_id)
    
    # Verificar si el usuario ya dio me gusta
    me_gusta = MeGusta.query.filter_by(receta_id=receta_id, ususario_id=current_user.id).first()
    
    if me_gusta:
        # Si ya dio me gusta, eliminarlo (toggle)
        db.session.delete(me_gusta)
        db.session.commit()
        flash('Se ha quitado tu me gusta', 'info')
    else:
        # Si no ha dado me gusta, agregarlo
        nuevo_me_gusta = MeGusta(ususario_id=current_user.id, receta_id=receta_id)
        db.session.add(nuevo_me_gusta)
        db.session.commit()
        flash('¡Gracias por tu me gusta!', 'success')
    
    return redirect(url_for('api.ver_receta', receta_id=receta_id))