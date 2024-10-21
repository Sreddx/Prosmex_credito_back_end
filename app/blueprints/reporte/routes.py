from flask import Blueprint
from app.services.reporte_service import ReporteService
from app.blueprints.helpers import create_response, handle_exceptions
from flask_jwt_extended import jwt_required

reporte_blueprint = Blueprint('reporte', __name__, url_prefix='/reporte')

@reporte_blueprint.route('/general', methods=['GET'])
@jwt_required()
def obtener_reporte_general():
    def func():
        reporte = ReporteService.obtener_reporte()
        return create_response({'reporte': reporte}, 200)
    return handle_exceptions(func)
