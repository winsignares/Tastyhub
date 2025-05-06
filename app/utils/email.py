from flask import current_app, render_template
from flask_mail import Message, Mail

mail = Mail()

def enviar_email_recuperacion(destinatario, reset_url):
    """
    Envía un correo electrónico de recuperación de contraseña
    """
    msg = Message(
        'Recuperación de contraseña - Sistema de Recetas',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[destinatario]
    )
    
    msg.html = render_template(
        'emails/recuperar_password.html',
        reset_url=reset_url
    )
    
    mail.send(msg)

def enviar_email_bienvenida(destinatario, nombre):
    """
    Envía un correo electrónico de bienvenida al nuevo usuario
    """
    msg = Message(
        '¡Bienvenido a Sistema de Recetas!',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[destinatario]
    )
    
    msg.html = render_template(
        'emails/bienvenida.html',
        nombre=nombre
    )
    
    mail.send(msg)

def enviar_notificacion_nueva_receta(destinatario, autor, receta_titulo, receta_url):
    """
    Envía notificación a seguidores cuando un usuario publica una nueva receta
    """
    msg = Message(
        f'Nueva receta de {autor}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[destinatario]
    )
    
    msg.html = render_template(
        'emails/nueva_receta.html',
        autor=autor,
        receta_titulo=receta_titulo,
        receta_url=receta_url
    )
    
    mail.send(msg)