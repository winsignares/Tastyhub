from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user
from app.models import Ingrediente
from app.config.db import db
from . import api_bp

# Endpoint para listar ingredientes ✅
@api_bp.route('/ingredientes')
def listar_ingredientes():
    try:
        ingredientes = Ingrediente.query.all()
        formato = request.args.get('format', 'json')
        if formato == 'html':
            return render_template('ingredientes.html', ingredientes=ingredientes)
        else:
            respuesta = {
                'status': 'success',
                'total': len(ingredientes),
                'ingredientes': [
                    {
                        'id': ingrediente.id,
                        'nombre': ingrediente.nombre,
                        'unidad_medida': ingrediente.unidad_medida,
                        'recetas_count': len(ingrediente.recetas_ingredientes) if hasattr(ingrediente, 'recetas_ingredientes') else 0
                    } for ingrediente in ingredientes
                ]
            }
            
            return jsonify(respuesta), 200
            
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f"Error de base de datos al listar ingredientes: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'Error al obtener ingredientes desde la base de datos',
            'error_type': 'database_error',
            'details': str(e) if current_app.debug else 'Error en la consulta a la base de datos'
        }), 500
        
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general al listar ingredientes: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'error_type': 'server_error',
            'details': str(e) if current_app.debug else 'Error interno del servidor'
        }), 500

# Enpoint para agregar ingredientes (admin) ✅
@api_bp.route('/admin/ingredientes', methods=['GET', 'POST'])
# @login_required
def admin_ingredientes():
    try:
        if request.method == 'GET':
            try:
                ingredientes = Ingrediente.query.all()
                formato = request.args.get('format', 'json')
                if formato == 'html':
                    return render_template('home-page.html', ingredientes=ingredientes)
                else:
                    respuesta = {
                        'status': 'success',
                        'total': len(ingredientes),
                        'ingredientes': [
                            {
                                'id': ingrediente.id,
                                'nombre': ingrediente.nombre,
                                'unidad_medida': ingrediente.unidad_medida,
                                'recetas_count': len(ingrediente.recetas_ingredientes) if hasattr(ingrediente, 'recetas_ingredientes') else 0
                            } for ingrediente in ingredientes
                        ]
                    }
                    
                    return jsonify(respuesta), 200
                    
            except Exception as e:
                current_app.logger.error(f"Error al obtener ingredientes para administración: {str(e)}")
                
                if request.args.get('format') == 'html':
                    flash('Error al cargar ingredientes', 'error')
                    return render_template('home-page.html', ingredientes=[])
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al obtener ingredientes',
                        'error_type': 'data_retrieval_error',
                        'details': str(e) if current_app.debug else 'Error al recuperar datos'
                    }), 500
        
        elif request.method == 'POST':
            try:
                if request.is_json:
                    data = request.get_json()
                    nombre = data.get('nombre')
                    unidad_medida = data.get('unidad_medida')
                else:
                    nombre = request.form.get('nombre')
                    unidad_medida = request.form.get('unidad_medida')
                
                if not nombre:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'El nombre del ingrediente es obligatorio',
                            'error_type': 'validation_error',
                            'field': 'nombre'
                        }), 400
                    else:
                        flash('El nombre del ingrediente es obligatorio', 'error')
                        return redirect(url_for('api.admin_ingredientes'))
                
                ingrediente_existente = Ingrediente.query.filter_by(nombre=nombre).first()
                if ingrediente_existente:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Ya existe un ingrediente con ese nombre',
                            'error_type': 'duplicate_error',
                            'field': 'nombre',
                            'existing_id': ingrediente_existente.id
                        }), 409  # 409 Conflict
                    else:
                        flash('Ya existe un ingrediente con ese nombre', 'error')
                        return redirect(url_for('api.admin_ingredientes'))
                
                try:
                    nuevo_ingrediente = Ingrediente(nombre=nombre, unidad_medida=unidad_medida)
                    db.session.add(nuevo_ingrediente)
                    db.session.commit()
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'success',
                            'message': 'Ingrediente creado exitosamente',
                            'ingrediente': {
                                'id': nuevo_ingrediente.id,
                                'nombre': nuevo_ingrediente.nombre,
                                'unidad_medida': nuevo_ingrediente.unidad_medida
                            }
                        }), 201  # 201 Created
                    else:
                        flash('Ingrediente creado exitosamente', 'success')
                        return redirect(url_for('api.admin_ingredientes'))
                        
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error de integridad al crear ingrediente: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error de integridad en la base de datos',
                            'error_type': 'integrity_error',
                            'details': str(e) if current_app.debug else 'Error al guardar en la base de datos'
                        }), 400
                    else:
                        flash('Error al crear el ingrediente: posible duplicado', 'error')
                        return redirect(url_for('api.admin_ingredientes'))
                        
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error al crear ingrediente: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al crear el ingrediente',
                            'error_type': 'database_error',
                            'details': str(e) if current_app.debug else 'Error en la base de datos'
                        }), 500
                    else:
                        flash('Error al crear el ingrediente', 'error')
                        return redirect(url_for('api.admin_ingredientes'))
                        
            except Exception as e:
                current_app.logger.error(f"Error general al procesar solicitud POST de ingrediente: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al procesar la solicitud',
                        'error_type': 'request_processing_error',
                        'details': str(e) if current_app.debug else 'Error interno del servidor'
                    }), 500
                else:
                    flash('Error al procesar la solicitud', 'error')
                    return redirect(url_for('api.admin_ingredientes'))
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'Método no permitido',
                'error_type': 'method_not_allowed'
            }), 405
            
    except Exception as e:
        current_app.logger.error(f"Error general en endpoint admin_ingredientes: {str(e)}")
        if request.method == 'GET' and request.args.get('format') == 'html':
            flash('Error del servidor', 'error')
            return render_template('home-page.html', ingredientes=[])
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500

# Endpoint para editar ingredientes (admin) ✅
@api_bp.route('/admin/ingredientes/<int:ingrediente_id>/editar', methods=['GET', 'POST'])
# @login_required
def editar_ingrediente(ingrediente_id):
    try:
        ingrediente = Ingrediente.query.get(ingrediente_id)
        if not ingrediente:
            if request.method == 'GET' and request.args.get('format') == 'html':
                flash('Ingrediente no encontrado', 'error')
                return redirect(url_for('api.admin_ingredientes'))
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Ingrediente no encontrado',
                    'error_type': 'not_found',
                    'ingrediente_id': ingrediente_id
                }), 404
        
        if request.method == 'GET':
            formato = request.args.get('format', 'json')
            if formato == 'html':
                return render_template('admin/editar_ingrediente.html', ingrediente=ingrediente)
            else:
                respuesta = {
                    'status': 'success',
                    'ingrediente': {
                        'id': ingrediente.id,
                        'nombre': ingrediente.nombre,
                        'unidad_medida': ingrediente.unidad_medida
                    }
                }
                
                return jsonify(respuesta), 200
        
        elif request.method == 'POST':
            try:
                if request.is_json:
                    data = request.get_json()
                    nombre = data.get('nombre')
                    unidad_medida = data.get('unidad_medida')
                else:
                    nombre = request.form.get('nombre')
                    unidad_medida = request.form.get('unidad_medida')
                
                if not nombre:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'El nombre del ingrediente es obligatorio',
                            'error_type': 'validation_error',
                            'field': 'nombre'
                        }), 400
                    else:
                        flash('El nombre del ingrediente es obligatorio', 'error')
                        return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
                
                # Verificar si el nombre ya existe y no es el mismo ingrediente
                ingrediente_existente = Ingrediente.query.filter_by(nombre=nombre).first()
                if ingrediente_existente and ingrediente_existente.id != ingrediente_id:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Ya existe un ingrediente con ese nombre',
                            'error_type': 'duplicate_error',
                            'field': 'nombre',
                            'existing_id': ingrediente_existente.id
                        }), 409  # 409 Conflict
                    else:
                        flash('Ya existe un ingrediente con ese nombre', 'error')
                        return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
                
                try:
                    # Guardar datos actualizados
                    ingrediente.nombre = nombre
                    ingrediente.unidad_medida = unidad_medida
                    db.session.commit()
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'success',
                            'message': 'Ingrediente actualizado exitosamente',
                            'ingrediente': {
                                'id': ingrediente.id,
                                'nombre': ingrediente.nombre,
                                'unidad_medida': ingrediente.unidad_medida
                            }
                        }), 200
                    else:
                        flash('Ingrediente actualizado exitosamente', 'success')
                        return redirect(url_for('api.admin_ingredientes'))
                
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error de integridad al actualizar ingrediente {ingrediente_id}: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error de integridad en la base de datos',
                            'error_type': 'integrity_error',
                            'details': str(e) if current_app.debug else 'Error al guardar en la base de datos'
                        }), 400
                    else:
                        flash('Error al actualizar el ingrediente: posible duplicado', 'error')
                        return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
                
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error al actualizar ingrediente {ingrediente_id}: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al actualizar el ingrediente',
                            'error_type': 'database_error',
                            'details': str(e) if current_app.debug else 'Error en la base de datos'
                        }), 500
                    else:
                        flash('Error al actualizar el ingrediente', 'error')
                        return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
            
            except Exception as e:
                current_app.logger.error(f"Error general al procesar solicitud POST para editar ingrediente {ingrediente_id}: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al procesar la solicitud',
                        'error_type': 'request_processing_error',
                        'details': str(e) if current_app.debug else 'Error interno del servidor'
                    }), 500
                else:
                    flash('Error al procesar la solicitud', 'error')
                    return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
        
        else:
            # Método no permitido
            return jsonify({
                'status': 'error',
                'message': 'Método no permitido',
                'error_type': 'method_not_allowed'
            }), 405
    
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general en endpoint editar_ingrediente para ID {ingrediente_id}: {str(e)}")
        
        if request.method == 'GET' and request.args.get('format') == 'html':
            flash('Error del servidor', 'error')
            return redirect(url_for('api.admin_ingredientes'))
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500

# Endpoint para eliminar ingredientes (admin) ✅
@api_bp.route('/admin/ingredientes/<int:ingrediente_id>/eliminar', methods=['POST', 'DELETE'])
# @login_required
def eliminar_ingrediente(ingrediente_id):
    try:
        ingrediente = Ingrediente.query.get(ingrediente_id)
        if not ingrediente:
            if request.is_json or request.method == 'DELETE':
                return jsonify({
                    'status': 'error',
                    'message': 'Ingrediente no encontrado',
                    'error_type': 'not_found',
                    'ingrediente_id': ingrediente_id
                }), 404
            else:
                flash('Ingrediente no encontrado', 'error')
                return redirect(url_for('api.admin_ingredientes'))
        
        try:
            recetas_con_ingrediente = ingrediente.recetas_ingredientes if hasattr(ingrediente, 'recetas_ingredientes') else []
            if recetas_con_ingrediente:
                recetas_ids = [ri.receta_id for ri in recetas_con_ingrediente]
                current_app.logger.info(f"Intento de eliminar ingrediente {ingrediente_id} usado en recetas: {recetas_ids}")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'No se puede eliminar el ingrediente porque está siendo utilizado por recetas',
                        'error_type': 'constraint_violation',
                        'ingrediente_id': ingrediente_id,
                        'recetas_ids': recetas_ids,
                        'recetas_count': len(recetas_ids)
                    }), 409
                else:
                    flash('No se puede eliminar el ingrediente porque está siendo utilizado por recetas', 'error')
                    return redirect(url_for('api.admin_ingredientes'))
            
            try:
                nombre_ingrediente = ingrediente.nombre  # Guardar para el mensaje
                db.session.delete(ingrediente)
                db.session.commit()
                current_app.logger.info(f"Ingrediente {ingrediente_id} ({nombre_ingrediente}) eliminado exitosamente")
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'success',
                        'message': 'Ingrediente eliminado exitosamente',
                        'ingrediente_id': ingrediente_id,
                        'ingrediente_nombre': nombre_ingrediente
                    }), 200
                else:
                    flash('Ingrediente eliminado exitosamente', 'success')
                    return redirect(url_for('api.admin_ingredientes'))
                
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                current_app.logger.error(f"Error de integridad al eliminar ingrediente {ingrediente_id}: {str(e)}")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'Error de integridad en la base de datos',
                        'error_type': 'integrity_error',
                        'details': str(e) if current_app.debug else 'Error al eliminar de la base de datos'
                    }), 400
                else:
                    flash('Error al eliminar el ingrediente: violación de integridad', 'error')
                    return redirect(url_for('api.admin_ingredientes'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error al eliminar ingrediente {ingrediente_id}: {str(e)}")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al eliminar el ingrediente',
                        'error_type': 'database_error',
                        'details': str(e) if current_app.debug else 'Error en la base de datos'
                    }), 500
                else:
                    flash('Error al eliminar el ingrediente', 'error')
                    return redirect(url_for('api.admin_ingredientes'))
                
        except Exception as e:
            current_app.logger.error(f"Error al verificar uso del ingrediente {ingrediente_id}: {str(e)}")
            
            if request.is_json or request.method == 'DELETE':
                return jsonify({
                    'status': 'error',
                    'message': 'Error al verificar uso del ingrediente',
                    'error_type': 'verification_error',
                    'details': str(e) if current_app.debug else 'Error al verificar relaciones'
                }), 500
            else:
                flash('Error al verificar uso del ingrediente', 'error')
                return redirect(url_for('api.admin_ingredientes'))
                
    except Exception as e:
        current_app.logger.error(f"Error general en endpoint eliminar_ingrediente para ID {ingrediente_id}: {str(e)}")
        
        if request.is_json or request.method == 'DELETE':
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.admin_ingredientes'))

# Endpoint para buscar ingredientes por nombre ✅
@api_bp.route('/api/ingredientes/buscar')
def buscar_ingredientes():
    try:
        # Obtener el término de búsqueda
        termino = request.args.get('term', '')
        
        if not termino:
            return jsonify({
                'status': 'error',
                'message': 'El término de búsqueda es obligatorio',
                'error_type': 'validation_error'
            }), 400
        
        try:
            # Buscar ingredientes que coincidan con el término
            ingredientes = Ingrediente.query.filter(
                Ingrediente.nombre.like(f'%{termino}%')
            ).limit(10).all()
            
            # Crear resultado para autocomplete
            resultado = [
                {
                    'id': ing.id,
                    'value': ing.nombre,
                    'label': f"{ing.nombre} ({ing.unidad_medida})",
                    'unidad_medida': ing.unidad_medida
                } for ing in ingredientes
            ]
            
            return jsonify(resultado), 200
            
        except sqlalchemy.exc.SQLAlchemyError as e:
            # Error específico de SQLAlchemy
            current_app.logger.error(f"Error de base de datos al buscar ingredientes con término '{termino}': {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Error al buscar ingredientes en la base de datos',
                'error_type': 'database_error',
                'details': str(e) if current_app.debug else 'Error en la consulta a la base de datos'
            }), 500
            
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general al buscar ingredientes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'error_type': 'server_error',
            'details': str(e) if current_app.debug else 'Error interno del servidor'
        }), 500