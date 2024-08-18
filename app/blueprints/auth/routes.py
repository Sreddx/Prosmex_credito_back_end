from flask import Blueprint, request, current_app
from app.services.usuario_service import UsuarioService
from app.blueprints.helpers import *
from flask_jwt_extended import create_access_token,jwt_required, unset_jwt_cookies, set_access_cookies
from app import bcrypt,jwt
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@auth_blueprint.route('/login', methods=['POST'])
def login():
    def func():
        payload = request.json
        if not payload:
            return make_error_response('Payload vacío', 400)
        fields =validate_fields(payload, ['email', 'contrasena'])
        if len(fields) > 0:
            raise ValueError(f'Faltan los siguientes campos: {fields}')
        
        if request.method == 'POST':
            email = payload.get('email')
            password = payload.get('contrasena')
            # Init user service
            print(payload)
            
            user = UsuarioService.get_user_by_email(email)
            if user is None:
                raise ValueError('Usuario no encontrado')
            app.logger.debug(f'User: {user.serialize()}')
            
            if user and bcrypt.check_password_hash(user.contrasena, password):
                access_token = create_access_token(identity=user.id)
                response = create_response({
                    "message": "Inicio de sesión exitoso!",
                    "User": user.serialize()
                }, 200)
                set_access_cookies(response, access_token)
                return response
            
            else:
                app.logger.error('Credenciales invalidas', exc_info=True)
                return make_error_response('Credenciales inválidas', 401)
        
        else:
            app.logger.error('Método no permitido', exc_info=True)
            return make_error_response('Método no permitido', 405)
    return handle_exceptions(func)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    def func():
        payload = request.json
        if not payload:
            return make_error_response('Payload vacío', 400)
        fields = validate_fields(payload, ['nombre', 'apellido_paterno', 'apellido_materno', 'email', 'contrasena', 'rol_id'])
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
    # Init user service
    user_service = UsuarioService()
    current_user = user_service.get_user_from_jwt()
    access_token = create_access_token(identity=current_user)
    response = create_response({
        "message": "Token de acceso actualizado!"
    }, 200)
    set_access_cookies(response, access_token)
    return response