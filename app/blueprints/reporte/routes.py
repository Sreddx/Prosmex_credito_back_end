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
        print(reporte)
        return create_response({'reporte': reporte}, 200)
    return handle_exceptions(func)

@reporte_blueprint.route('/sobrante-grupo/<int:grupo_id>', methods=['GET'])
def obtener_sobrante_grupo(grupo_id):
    def func():
        sobrante_grupo = ReporteService.obtener_sobrante_por_grupo(grupo_id)
        return create_response({'sobrante_grupo': sobrante_grupo}, 200)
    return handle_exceptions(func)

@reporte_blueprint.route('/sobrante-semanal/<int:grupo_id>', methods=['GET'])
def obtener_sobrante_semanal(grupo_id):
    def func():
        sobrante_semanal = ReporteService.obtener_sobrante_semanal(grupo_id)
        return create_response({'sobrante_semanal': sobrante_semanal}, 200)
    return handle_exceptions(func)

