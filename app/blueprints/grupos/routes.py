from flask import Blueprint, request
from app.services import GrupoService
from app.blueprints.helpers import create_response, make_error_response, handle_exceptions, validate_fields


grupos_blueprint = Blueprint('grupos', __name__, url_prefix='/grupos')

@grupos_blueprint.route('/', methods=['GET'])
def list_grupos():
    def func():
        service = GrupoService()
        grupos = service.list_grupos()
        lista_grupos = [grupo.serialize() for grupo in grupos]
        return create_response(lista_grupos, 200)
    return handle_exceptions(func)

@grupos_blueprint.route('/', methods=['POST'])
def create_grupo():
    data = request.get_json()
    required_fields = ['nombre_grupo', 'ruta_id', 'usuario_id_titular']
    missing_fields = validate_fields(data, required_fields)
    if missing_fields:
        return make_error_response(f'Faltan campos requeridos: {", ".join(missing_fields)}', 400)

    def func():
        service = GrupoService()
        new_grupo = service.create_grupo(data)
        
        return create_response({'grupo': new_grupo.serialize()}, 201)
    return handle_exceptions(func)

@grupos_blueprint.route('/<int:grupo_id>', methods=['GET'])
def get_grupo(grupo_id):
    def func():
        service = GrupoService(grupo_id)
        grupo = service.get_grupo()
        grupo_data = {
            'grupo_id': grupo.grupo_id,
            'nombre': grupo.nombre_grupo,
            'ruta_id': grupo.ruta_id,
        }
        return create_response({'grupo': grupo_data}, 200)
    return handle_exceptions(func)

@grupos_blueprint.route('/<int:grupo_id>', methods=['PUT'])
def update_grupo(grupo_id):
    data = request.get_json()

    def func():
        service = GrupoService(grupo_id)
        updated_grupo = service.update_grupo(data)
        grupo_data = {
            'grupo_id': updated_grupo.grupo_id,
            'nombre_grupo': updated_grupo.nombre_grupo,
            'ruta_id': updated_grupo.ruta_id,
        }
        return create_response({'grupo': grupo_data}, 200)
    return handle_exceptions(func)

@grupos_blueprint.route('/<int:grupo_id>', methods=['DELETE'])
def delete_grupo(grupo_id):
    def func():
        service = GrupoService(grupo_id)
        service.delete_grupo()
        return create_response({'message': 'Grupo eliminado correctamente'}, 200)
    return handle_exceptions(func)
