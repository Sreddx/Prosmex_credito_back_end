from flask import Blueprint, jsonify
from app.services import RolService

role_blueprint = Blueprint('role', __name__, url_prefix='/roles')

@role_blueprint.route('/', methods=['GET'])
def get_roles():
    roles = RolService.get_all_roles()
    return jsonify([{'id': role.rol_id, 'nombre': role.nombre} for role in roles])
