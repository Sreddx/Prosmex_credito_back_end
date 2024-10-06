from flask import Blueprint, request
from app.services.ruta_service import RutaService
from app.blueprints.helpers import create_response, make_error_response, handle_exceptions, validate_fields

rutas_blueprint = Blueprint('rutas', __name__, url_prefix='/rutas')

@rutas_blueprint.route('/', methods=['GET'])
def list_rutas():
    def func():
        service = RutaService()
        rutas = service.list_rutas()
        return create_response({'rutas': rutas}, 200)
    return handle_exceptions(func)

@rutas_blueprint.route('/', methods=['POST'])
def create_ruta():
    data = request.get_json()
    required_fields = ['nombre_ruta', 'usuario_id_gerente', 'usuario_id_supervisor']
    missing_fields = validate_fields(data, required_fields)
    if missing_fields:
        return make_error_response(f'Faltan campos requeridos: {", ".join(missing_fields)}', 400)

    def func():
        service = RutaService()
        new_ruta = service.create_ruta(data)
        ruta_data = new_ruta.serialize()
        return create_response({'ruta': ruta_data}, 201)
    return handle_exceptions(func)

@rutas_blueprint.route('/<int:ruta_id>', methods=['GET'])
def get_ruta(ruta_id):
    def func():
        service = RutaService(ruta_id)
        ruta = service.get_ruta()
        ruta_data = ruta.serialize()
        return create_response({'ruta': ruta_data}, 200)
    return handle_exceptions(func)

@rutas_blueprint.route('/<int:ruta_id>', methods=['PUT'])
def update_ruta(ruta_id):
    data = request.get_json()
    def func():
        service = RutaService(ruta_id)
        updated_ruta = service.update_ruta(data)
        ruta_data = updated_ruta.serialize()
        return create_response({'ruta': ruta_data}, 200)
    return handle_exceptions(func)

@rutas_blueprint.route('/<int:ruta_id>', methods=['DELETE'])
def delete_ruta(ruta_id):
    def func():
        service = RutaService(ruta_id)
        service.delete_ruta()
        return create_response({'message': 'Ruta eliminada correctamente'}, 200)
    return handle_exceptions(func)
