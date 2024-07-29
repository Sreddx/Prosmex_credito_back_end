from flask import Blueprint, request, jsonify
from app.services import PrestamoService

prestamo_blueprint = Blueprint('prestamo', __name__, url_prefix='/prestamos')

@prestamo_blueprint.route('/', methods=['POST'])
def create_prestamo():
    data = request.get_json()
    new_prestamo = PrestamoService.create_prestamo(data)
    return jsonify({'message': 'Prestamo created successfully', 'prestamo': new_prestamo.prestamo_id}), 201
