from flask import Blueprint, request
from app.services.reporte_service import ReporteService
from app.blueprints.helpers import create_response, handle_exceptions
from flask_jwt_extended import get_jwt_identity, jwt_required


reporte_blueprint = Blueprint('reporte', __name__, url_prefix='/reporte')

@reporte_blueprint.route('/general', methods=['GET'])
@jwt_required()
def obtener_reporte_general():
    def func():
        # Obtener los parámetros de paginación de la solicitud
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Llamar al método `obtener_reporte` con los argumentos de paginación
        reporte = ReporteService.obtener_reporte(page=page, per_page=per_page)

        # Preparar la respuesta para el reporte general sin totales
        response_data = {
            'reporte': reporte['reporte'],
            'page': reporte['page'],
            'per_page': reporte['per_page'],
            'total_items': reporte['total_items'],
        }

        return create_response(response_data, 200)

    return handle_exceptions(func)


@reporte_blueprint.route('/general/totales', methods=['GET'])
@jwt_required()
def obtener_totales():
    def func():
        # Llamar al método `obtener_totales` para calcular los valores totales
        totales = ReporteService.obtener_totales()
        return create_response({'totales': totales}, 200)

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

@reporte_blueprint.route('/sobrante-total-usuario', methods=['GET'])
@jwt_required()
def obtener_sobrante_total_usuario():
    def func():
        # Obtener el ID del usuario autenticado desde el JWT
        user_id = get_jwt_identity()
        sobrante_total = ReporteService.obtener_sobrante_total_usuario_por_prestamo(user_id)
        return create_response({'sobrante_total': sobrante_total}, 200)
    return handle_exceptions(func)


# Bono de cada grupo para el titular dado
@reporte_blueprint.route('/bono-grupos-titular', methods=['GET'])
@jwt_required()
def obtener_bono_para_grupos_titular():
    def func():
        user_id = get_jwt_identity()  # Obtener el user_id del usuario autenticado
        reporte_bonos = ReporteService.calcular_bono_para_grupos_de_titular(user_id)
        return create_response({'reporte_bonos': reporte_bonos}, 200)
    return handle_exceptions(func)

# Bono total del titular dado
@reporte_blueprint.route('/bono-global-titular', methods=['GET'])
@jwt_required()
def obtener_bono_global_titular():
    def func():
        # Obtener el user_id del usuario autenticado
        user_id = get_jwt_identity()

        # Llamar a la función que calcula el bono global para el titular
        total_bono = ReporteService.calcular_bono_global_titular(user_id)

        # Devolver la respuesta con los detalles del bono global
        return create_response({'total_bono': total_bono}, 200)
    
    return handle_exceptions(func)


