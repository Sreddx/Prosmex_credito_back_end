from flask import Blueprint, request
from app.services.pago_service import PagoService
from app.blueprints.helpers import create_response, make_error_response, handle_exceptions, validate_fields

pagos_blueprint = Blueprint('pagos', __name__, url_prefix='/pagos')

@pagos_blueprint.route('/', methods=['GET'])
def list_pagos():
    def func():
        service = PagoService()
        pagos = service.list_pagos()
        return create_response({'pagos': pagos}, 200)
    return handle_exceptions(func)

@pagos_blueprint.route('/', methods=['POST'])
def create_pago():
    data = request.get_json()
    required_fields = ['monto_pagado', 'prestamo_id'] 
    missing_fields = validate_fields(data, required_fields)
    if missing_fields:
        return make_error_response(f'Faltan campos requeridos: {", ".join(missing_fields)}', 400)

    def func():
        service = PagoService()
        new_pago = service.create_pago(data)
        pago_data = new_pago.serialize()
        return create_response({'pago': pago_data}, 201)
    return handle_exceptions(func)


@pagos_blueprint.route('/<int:pago_id>', methods=['GET'])
def get_pago(pago_id):
    def func():
        service = PagoService(pago_id)
        pago = service.get_pago()
        pago_data = pago.serialize()
        return create_response({'pago': pago_data}, 200)
    return handle_exceptions(func)

@pagos_blueprint.route('/<int:pago_id>', methods=['PUT'])
def update_pago(pago_id):
    data = request.get_json()
    def func():
        service = PagoService(pago_id)
        updated_pago = service.update_pago(data)
        pago_data = updated_pago.serialize()
        return create_response({'pago': pago_data}, 200)
    return handle_exceptions(func)

@pagos_blueprint.route('/<int:pago_id>', methods=['DELETE'])
def delete_pago(pago_id):
    def func():
        service = PagoService(pago_id)
        service.delete_pago()
        return create_response({'message': 'Pago eliminado correctamente'}, 200)
    return handle_exceptions(func)

@pagos_blueprint.route('/grupos', methods=['GET'])
def get_grupos():
    def func():
        grupos = PagoService.get_grupos()
        return create_response({'grupos': grupos}, 200)
    return handle_exceptions(func)

@pagos_blueprint.route('/prestamos', methods=['GET'])
def get_prestamos_by_grupo_tabla():
    grupo_id = request.args.get('grupo_id', type=int)
    if not grupo_id:
        return make_error_response('El parámetro grupo_id es requerido.', 400)

    def func():
        prestamos = PagoService.get_prestamos_by_grupo_tabla(grupo_id)
        return create_response({'prestamos': prestamos}, 200)
    return handle_exceptions(func)




@pagos_blueprint.route('/pagos-prestamo/<int:prestamo_id>', methods=['GET'])
def get_pagos_by_prestamo_tabla(prestamo_id):
    def func():
        if not prestamo_id:
            return make_error_response('El parámetro prestamo_id es requerido.', 400)
        pagos = PagoService.get_pagos_by_prestamo_tabla(prestamo_id)
        return create_response({'pagos': pagos}, 200)
    return handle_exceptions(func)