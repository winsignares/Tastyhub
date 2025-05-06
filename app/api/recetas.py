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

# Endpoint para listar recetas y aplicar filtros ✅
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
    recetas_paginadas = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
    
    # Obtener categorías
    categorias = Categoria.query.all()
    
    # Crear respuesta JSON
    respuesta = {
        'status': 'success',
        'total_recetas': recetas_paginadas.total,
        'pagina_actual': recetas_paginadas.page,
        'total_paginas': recetas_paginadas.pages,
        'recetas_por_pagina': por_pagina,
        'recetas': [
            {
                'id': receta.id,
                'titulo': receta.titulo,
                'descripcion': receta.descripcion,
                'imagen_portada': receta.imagen_portada,
                'tiempo_preparacion': receta.tiempor_pre,
                'fecha_creacion': receta.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                'autor_id': receta.id_usuario,
                'autor_nombre': receta.autor.nombre if hasattr(receta, 'autor') else None,
                'total_me_gustas': receta.contar_me_gustas(),
                'categorias': [{'id': cat.id, 'nombre': cat.nombre} for cat in receta.categorias]
            }
            for receta in recetas_paginadas.items
        ],
        'categorias': [
            {
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion
            }
            for categoria in categorias
        ],
        'filtros': {
            'busqueda': busqueda,
            'categoria_id': categoria_id
        }
    }
    
    return jsonify(respuesta), 200
    # return render_template('home-page.html', 
    #                        recetas=recetas, 
    #                        categorias=categorias,
    #                        categoria_actual=categoria_id,
    #                        busqueda=busqueda)

# Endpoint para ver una receta específica ✅
@api_bp.route('/recetas/<int:receta_id>')
def ver_receta(receta_id):
    try:
        # Intentar obtener la receta por ID
        receta = Receta.query.get(receta_id)
        
        # Verificar si la receta existe
        if not receta:
            return jsonify({
                'status': 'error',
                'message': 'Receta no encontrada',
                'error_type': 'not_found',
                'receta_id': receta_id
            }), 404
        
        try:
            # Obtener instrucciones
            instrucciones = Instruccion.query.filter_by(id_receta=receta_id).order_by(Instruccion.numero_paso).all()
            
            # Obtener ingredientes de la receta
            ingredientes = db.session.query(RecetaIngrediente, Ingrediente) \
                .join(Ingrediente, RecetaIngrediente.ingredientes_id == Ingrediente.id) \
                .filter(RecetaIngrediente.receta_id == receta_id).all()
            
            # Verificar si el usuario actual ha dado me gusta
            usuario_dio_like = False
            if current_user.is_authenticated:
                usuario_dio_like = MeGusta.query.filter_by(receta_id=receta_id, ususario_id=current_user.id).first() is not None
            
            # Intentar obtener el autor
            try:
                autor_nombre = receta.autor.nombre if hasattr(receta, 'autor') and receta.autor else "Autor desconocido"
            except Exception as e:
                current_app.logger.warning(f"Error al obtener autor de receta {receta_id}: {str(e)}")
                autor_nombre = "Autor desconocido"
            
            # Intentar obtener categorías
            try:
                categorias = [
                    {
                        'id': cat.id, 
                        'nombre': cat.nombre
                    } for cat in receta.categorias
                ] if hasattr(receta, 'categorias') else []
            except Exception as e:
                current_app.logger.warning(f"Error al obtener categorías de receta {receta_id}: {str(e)}")
                categorias = []
            
            # Crear respuesta JSON
            respuesta = {
                'status': 'success',
                'receta': {
                    'id': receta.id,
                    'titulo': receta.titulo,
                    'descripcion': receta.descripcion,
                    'imagen_portada': receta.imagen_portada,
                    'tiempo_preparacion': receta.tiempor_pre,
                    'fecha_creacion': receta.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'autor_id': receta.id_usuario,
                    'autor_nombre': autor_nombre,
                    'total_me_gustas': receta.contar_me_gustas(),
                    'usuario_dio_like': usuario_dio_like,
                    'categorias': categorias,
                    'ingredientes': [
                        {
                            'id': ingrediente.id,
                            'nombre': ing.nombre,
                            'cantidad': ingrediente.cantidad,
                            'unidad_medida': ing.unidad_medida
                        } for ingrediente, ing in ingredientes
                    ],
                    'instrucciones': [
                        {
                            'numero_paso': instruccion.numero_paso,
                            'descripcion': instruccion.descripcion
                        } for instruccion in instrucciones
                    ]
                }
            }
            
            return jsonify(respuesta), 200
            
        except Exception as e:
            # Error al obtener datos relacionados
            current_app.logger.error(f"Error al obtener datos relacionados de receta {receta_id}: {str(e)}")
            
            # Crear una respuesta parcial con los datos principales de la receta
            respuesta_parcial = {
                'status': 'partial_success',
                'message': 'Receta encontrada pero hubo problemas al obtener algunos detalles',
                'receta': {
                    'id': receta.id,
                    'titulo': receta.titulo,
                    'descripcion': receta.descripcion,
                    'imagen_portada': receta.imagen_portada,
                    'tiempo_preparacion': receta.tiempor_pre,
                    'fecha_creacion': receta.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                    'autor_id': receta.id_usuario
                },
                'error_details': str(e) if current_app.debug else 'Error al obtener datos relacionados'
            }
            
            return jsonify(respuesta_parcial), 206  # 206 Partial Content
        
    except sqlalchemy.exc.SQLAlchemyError as e:
        # Error específico de SQLAlchemy
        current_app.logger.error(f"Error de base de datos al obtener receta {receta_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error de base de datos',
            'error_type': 'database_error',
            'details': str(e) if current_app.debug else 'Error en la consulta a la base de datos'
        }), 500
        
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general al obtener receta {receta_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'error_type': 'server_error',
            'details': str(e) if current_app.debug else 'Error interno del servidor'
        }), 500

# Endpoint para crear una nueva receta ✅
@api_bp.route('/recetas/nueva', methods=['GET', 'POST'])
def nueva_receta():
    try:
        if request.method == 'GET':
            categorias = Categoria.query.all()
            ingredientes = Ingrediente.query.all()
            
            # Crear respuesta JSON para GET
            respuesta_get = {
                'status': 'success',
                'message': 'Formulario para crear nueva receta',
                'data': {
                    'categorias': [
                        {
                            'id': categoria.id,
                            'nombre': categoria.nombre,
                            'descripcion': categoria.descripcion
                        } for categoria in categorias
                    ],
                    'ingredientes': [
                        {
                            'id': ingrediente.id,
                            'nombre': ingrediente.nombre,
                            'unidad_medida': ingrediente.unidad_medida
                        } for ingrediente in ingredientes
                    ]
                }
            }
            return jsonify(respuesta_get), 200
        
        if request.method == 'POST':
            # Verificar autenticación
            if not current_user.is_authenticated:
                return jsonify({
                    'status': 'error',
                    'message': 'Debes iniciar sesión para crear recetas',
                    'code': 401
                }), 401
            
            # Obtener datos del JSON o form-data
            if request.is_json:
                data = request.get_json()
                titulo = data.get('titulo')
                descripcion = data.get('descripcion')
                tiempo_preparacion = data.get('tiempo_preparacion')
                categorias_ids = data.get('categorias', [])
                ingredientes_data = data.get('ingredientes', [])
                instrucciones_data = data.get('instrucciones', [])
            else:
                titulo = request.form.get('titulo')
                descripcion = request.form.get('descripcion')
                tiempo_preparacion = request.form.get('tiempo_preparacion')
                categorias_ids = request.form.getlist('categorias')
                ingredientes_ids = request.form.getlist('ingrediente_id')
                cantidades = request.form.getlist('cantidad')
                instrucciones = request.form.getlist('instruccion')
            
            # Validación de datos
            if not titulo:
                return jsonify({
                    'status': 'error',
                    'message': 'El título es obligatorio',
                    'errors': {'titulo': 'Este campo es obligatorio'}
                }), 400
            
            # Verificar que el usuario exista
            usuario = Usuario.query.get(current_user.id)
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': 'El usuario no existe en la base de datos',
                    'code': 404
                }), 404
            
            # Procesar la imagen de portada
            imagen_portada = None
            if 'imagen_portada' in request.files:
                archivo = request.files['imagen_portada']
                if archivo and archivo.filename != '' and allowed_file(archivo.filename):
                    try:
                        filename = secure_filename(archivo.filename)
                        unique_filename = f"{uuid.uuid4().hex}_{filename}"
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'recetas', unique_filename)
                        
                        # Asegurarse de que exista la carpeta
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        archivo.save(file_path)
                        imagen_portada = os.path.join('uploads', 'recetas', unique_filename)
                    except Exception as e:
                        current_app.logger.error(f"Error al guardar imagen: {str(e)}")
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al procesar la imagen',
                            'details': str(e)
                        }), 500
            
            try:
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
                
                # Procesar categorías, ingredientes, instrucciones
                if request.is_json:
                    # Procesar categorías (JSON)
                    for cat_id in categorias_ids:
                        receta_categoria = RecetaCategoria(receta_id=nueva_receta.id, categoria_id=int(cat_id))
                        db.session.add(receta_categoria)
                    
                    # Procesar ingredientes (JSON)
                    for ingrediente_data in ingredientes_data:
                        ingrediente = RecetaIngrediente(
                            receta_id=nueva_receta.id,
                            ingredientes_id=int(ingrediente_data['id']),
                            cantidad=int(ingrediente_data['cantidad'])
                        )
                        db.session.add(ingrediente)
                    
                    # Procesar instrucciones (JSON)
                    for i, instruccion_data in enumerate(instrucciones_data, start=1):
                        instruccion = Instruccion(
                            id_receta=nueva_receta.id,
                            numero_paso=i,
                            descripcion=instruccion_data['descripcion']
                        )
                        db.session.add(instruccion)
                else:
                    # Procesar categorías (form-data)
                    for cat_id in categorias_ids:
                        receta_categoria = RecetaCategoria(receta_id=nueva_receta.id, categoria_id=int(cat_id))
                        db.session.add(receta_categoria)
                    
                    # Procesar ingredientes (form-data)
                    for i, ing_id in enumerate(ingredientes_ids):
                        if ing_id and cantidades[i]:
                            ingrediente = RecetaIngrediente(
                                receta_id=nueva_receta.id,
                                ingredientes_id=int(ing_id),
                                cantidad=int(cantidades[i])
                            )
                            db.session.add(ingrediente)
                    
                    # Procesar instrucciones (form-data)
                    for i, instruccion_texto in enumerate(instrucciones, start=1):
                        if instruccion_texto.strip():
                            instruccion = Instruccion(
                                id_receta=nueva_receta.id,
                                numero_paso=i,
                                descripcion=instruccion_texto
                            )
                            db.session.add(instruccion)
                
                # Guardar todos los cambios
                db.session.commit()
                
                # Crear respuesta JSON para POST exitoso
                respuesta_post = {
                    'status': 'success',
                    'message': '¡Receta creada exitosamente!',
                    'data': {
                        'receta_id': nueva_receta.id,
                        'titulo': nueva_receta.titulo,
                        'descripcion': nueva_receta.descripcion,
                        'imagen_portada': nueva_receta.imagen_portada,
                        'tiempo_preparacion': nueva_receta.tiempor_pre,
                        'fecha_creacion': nueva_receta.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                        'url': url_for('api.ver_receta', receta_id=nueva_receta.id, _external=True)
                    }
                }
                
                return jsonify(respuesta_post), 201  # 201 Created
                
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                current_app.logger.error(f"Error de integridad: {str(e)}")
                
                if "foreign key constraint fails" in str(e).lower() and "id_usuario" in str(e):
                    return jsonify({
                        'status': 'error',
                        'message': 'El usuario no existe en la base de datos',
                        'details': 'Debes crear un usuario válido antes de crear recetas',
                        'error_type': 'foreign_key_constraint'
                    }), 400
                
                return jsonify({
                    'status': 'error',
                    'message': 'Error de integridad en la base de datos',
                    'details': str(e),
                    'error_type': 'integrity_error'
                }), 400
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error al crear receta: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': 'Error al crear receta',
                    'details': str(e),
                    'error_type': 'general_error'
                }), 500
                
    except Exception as e:
        current_app.logger.error(f"Error general: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error en el servidor',
            'details': str(e) if current_app.debug else 'Error interno del servidor',
            'error_type': 'server_error'
        }), 500

@api_bp.route('/recetas/<int:receta_id>/editar', methods=['GET', 'POST'])
# @login_required
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
# @login_required
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
# @login_required
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