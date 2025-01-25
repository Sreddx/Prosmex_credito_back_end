from flask import Blueprint, request, current_app
from app.services.usuario_service import UsuarioService
from app.blueprints.helpers import *
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, unset_jwt_cookies, set_access_cookies, set_refresh_cookies, get_jwt_identity
)
from app import bcrypt, jwt

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@auth_blueprint.route('/login', methods=['POST'])
def login():
    def func():
        payload = request.json
        if not payload:
            return make_error_response('Payload vacío', 400)
        fields = validate_fields(payload, ['usuario', 'contrasena'])
        if len(fields) > 0:
            raise ValueError(f'Faltan los siguientes campos: {fields}')
        
        if request.method == 'POST':
            usuario = payload.get('usuario')
            password = payload.get('contrasena')

            # Obtener usuario desde el servicio
            user = UsuarioService.get_user_by_usuario(usuario)
            if user is None:
                raise ValueError('Usuario no encontrado')
            
            if user and bcrypt.check_password_hash(user.contrasena, password):
                # Generar tokens
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))

                # Crear respuesta con ambos tokens
                response = create_response({
                    "message": "Inicio de sesión exitoso!",
                    "User": user.serialize(),
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200)

                # Opcional: Guardar tokens en cookies
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response
            
            else:
                current_app.logger.error('Credenciales inválidas', exc_info=True)
                return make_error_response('Credenciales inválidas', 401)
        
        else:
            current_app.logger.error('Método no permitido', exc_info=True)
            return make_error_response('Método no permitido', 405)
    return handle_exceptions(func)


@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    response = create_response({
        "message": "Cierre de sesión exitoso!",
    }, 200)
    unset_jwt_cookies(response)
    return response


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Obtener la identidad del usuario desde el refresh token
    current_user_id = get_jwt_identity()

    # Generar un nuevo access token
    access_token = create_access_token(identity=current_user_id)

    # Crear respuesta con el nuevo access token
    response = create_response({
        "message": "Token de acceso actualizado!",
        "access_token": access_token
    }, 200)

    # Opcional: Actualizar el access token en cookies
    set_access_cookies(response, access_token)
    return response


@auth_blueprint.route('/register', methods=['POST'])
def register():
    def func():
        payload = request.json
        if not payload:
            return make_error_response('Payload vacío', 400)
        fields = validate_fields(payload, ['nombre', 'apellido_paterno', 'apellido_materno', 'usuario', 'contrasena', 'rol_id'])
        if len(fields) > 0:
            return make_error_response(f'Faltan los siguientes campos: {fields}', 400)
        
        if request.method == 'POST':
            # Init user service

            user = UsuarioService.create_user(payload)
            return create_response({
                "message": "Usuario creado exitosamente!",
                "User": user.serialize()
            }, 201)
        else:
            app.logger.error('Método no permitido', exc_info=True)
            return make_error_response('Método no permitido', 405)
    return handle_exceptions(func)
