from sqlalchemy import func, case, and_, text
from sqlalchemy.orm import aliased
from app.models import (
    Grupo,
    Ruta,
    Usuario,
    ClienteAval,
    Prestamo,
    TipoPrestamo,
    Pago,
    Rol
)
from app import db
from flask_jwt_extended import get_jwt_identity
from app.models.bono import Bono
from app.models.falta import Falta
from app.services.usuario_service import UsuarioService
from datetime import datetime, timedelta
import pytz
from app.constants import TIMEZONE
from app.services import PrestamoService

class ReporteService:
    @staticmethod
    def obtener_reporte(page=1, per_page=10):
        # Configuración inicial y obtención del usuario
        user = UsuarioService.get_user_from_jwt()
        user_role_id = user.rol_id

        if user_role_id == 1:
            return []

        # Definir filtros según rol de usuario
        filters = []
        if user_role_id == 4:
            filters.append(Ruta.usuario_id_gerente == user.id)
        elif user_role_id == 3:
            filters.append(Ruta.usuario_id_supervisor == user.id)
        elif user_role_id == 2:
            filters.append(Grupo.usuario_id_titular == user.id)

        # Definición de subconsultas y configuración de fechas
        usuarios_gerente = aliased(Usuario)
        usuarios_supervisor = aliased(Usuario)
        usuarios_titular = aliased(Usuario)
        mexico_city_tz = pytz.timezone('America/Mexico_City')
        current_date = datetime.now(mexico_city_tz).date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Subconsulta para pagos por grupo
        pagos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(Pago.monto_pagado).label('total_pagos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
            .filter(
                Pago.fecha_pago >= start_of_week,
                Pago.fecha_pago <= end_of_week
            )
            .group_by(Grupo.grupo_id)
        ).subquery()

        # Calcular cobranza ideal
        cobranza_ideal_case = Prestamo.monto_prestamo * TipoPrestamo.porcentaje_semanal

        # Construcción del query principal sin el campo de bono
        query = db.session.query(
            Grupo.grupo_id,
            Ruta.ruta_id,
            func.coalesce(func.concat(usuarios_gerente.nombre, ' ', usuarios_gerente.apellido_paterno), '').label('gerente'),
            func.coalesce(func.concat(usuarios_supervisor.nombre, ' ', usuarios_supervisor.apellido_paterno), '').label('supervisor'),
            func.coalesce(func.concat(usuarios_titular.nombre, ' ', usuarios_titular.apellido_paterno), '').label('titular'),
            Ruta.nombre_ruta.label('ruta'),
            Grupo.nombre_grupo.label('grupo'),
            func.coalesce(func.sum(cobranza_ideal_case.distinct()), 0).label('cobranza_ideal'),
            func.coalesce(pagos_por_grupo.c.total_pagos, 0).label('cobranza_real'),
            func.coalesce(func.sum(Prestamo.monto_prestamo.distinct()), 0).label('prestamo_real'),
            (func.coalesce(func.sum(Prestamo.monto_prestamo.distinct()), 0) - 
            func.coalesce(func.sum(Pago.monto_pagado.distinct()), 0)).label('prestamo_papel'),
            func.count(func.distinct(Prestamo.prestamo_id)).label('numero_de_creditos')
        ).select_from(Grupo)

        # Joins
        query = query.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)
        query = query.outerjoin(usuarios_supervisor, Ruta.usuario_id_supervisor == usuarios_supervisor.id)
        query = query.outerjoin(usuarios_gerente, Ruta.usuario_id_gerente == usuarios_gerente.id)
        query = query.outerjoin(usuarios_titular, Grupo.usuario_id_titular == usuarios_titular.id)
        query = query.outerjoin(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
        query = query.outerjoin(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
        query = query.outerjoin(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
        query = query.outerjoin(pagos_por_grupo, pagos_por_grupo.c.grupo_id == Grupo.grupo_id)

        # Aplicar filtros si existen
        if filters:
            query = query.filter(*filters)

        # Agrupamiento de datos
        query = query.group_by(
            Grupo.grupo_id,
            Ruta.ruta_id,
            usuarios_gerente.nombre,
            usuarios_gerente.apellido_paterno,
            usuarios_supervisor.nombre,
            usuarios_supervisor.apellido_paterno,
            usuarios_titular.nombre,
            usuarios_titular.apellido_paterno,
            Ruta.nombre_ruta,
            Grupo.nombre_grupo,
            pagos_por_grupo.c.total_pagos
        )

        # Obtener el total de resultados antes de la paginación
        total_items = query.count()

        # Agregar paginación
        paginated_query = query.limit(per_page).offset((page - 1) * per_page)

        # Procesar los resultados de la consulta paginada
        results = paginated_query.all()
        report_data = []
        for row in results:
            # Obtener el bono para cada grupo
            bono_data = ReporteService.calcular_bono_por_grupo(row.grupo_id)
            bono = bono_data['bono_aplicado']['monto'] if bono_data['bono_aplicado'] else 0

            # Cálculos adicionales
            cobranza_ideal = float(row.cobranza_ideal or 0)
            cobranza_real = float(row.cobranza_real or 0)
            prestamo_real = float(row.prestamo_real or 0)
            prestamo_papel = float(row.prestamo_papel or 0)
            numero_de_creditos = row.numero_de_creditos or 0

            # Cálculo de la morosidad basado en la diferencia entre cobranza ideal y pagos reales
            morosidad_monto = max(cobranza_ideal - cobranza_real, 0)
            morosidad_porcentaje = morosidad_monto / cobranza_ideal if cobranza_ideal != 0 else None
            porcentaje_prestamo = prestamo_papel / cobranza_real if cobranza_real != 0 else None
            sobrante = cobranza_real - prestamo_papel - bono

            # Agregar datos al reporte
            report_data.append({
                'grupo_id': row.grupo_id,
                'gerente': row.gerente,
                'supervisor': row.supervisor,
                'titular': row.titular,
                'ruta': row.ruta,
                'grupo': row.grupo,
                'cobranza_ideal': cobranza_ideal,
                'cobranza_real': cobranza_real,
                'prestamo_papel': prestamo_papel,
                'prestamo_real': prestamo_real,
                'numero_de_creditos': numero_de_creditos,
                'morosidad_monto': morosidad_monto,
                'morosidad_porcentaje': morosidad_porcentaje,
                'porcentaje_prestamo': porcentaje_prestamo,
                'sobrante': sobrante,
                'numero_de_prestamos': numero_de_creditos,
                'bono': bono
            })

        return {
            'reporte': report_data,
            'page': page,
            'per_page': per_page,
            'total_items': total_items
        }

    @staticmethod
    def obtener_totales():
        # Configuración inicial y obtención del usuario
        user = UsuarioService.get_user_from_jwt()
        user_role_id = user.rol_id

        # Filtros basados en el rol del usuario
        filters = []
        if user_role_id == 4:  # Gerente
            filters.append(Ruta.usuario_id_gerente == user.id)
        elif user_role_id == 3:  # Supervisor
            filters.append(Ruta.usuario_id_supervisor == user.id)
        elif user_role_id == 2:  # Titular
            filters.append(Grupo.usuario_id_titular == user.id)

        # Calcular la semana actual
        from datetime import datetime, timedelta
        start_of_week = datetime.now().date() - timedelta(days=datetime.now().weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Subconsulta para pagos agrupados por grupo (con filtro de semana actual)
        pagos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(func.distinct(Pago.monto_pagado)).label('total_pagos')  # Asegurar no duplicar pagos
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
            .filter(Pago.fecha_pago >= start_of_week, Pago.fecha_pago <= end_of_week)  # Filtro por semana
            .group_by(Grupo.grupo_id)
        ).subquery()

        # Calcular cobranza ideal basada en el tipo de préstamo
        cobranza_ideal_case = Prestamo.monto_prestamo * TipoPrestamo.porcentaje_semanal

        # Query principal para los totales
        query_totales = db.session.query(
            func.sum(func.coalesce(cobranza_ideal_case, 0)).label('total_cobranza_ideal'),
            func.sum(func.distinct(func.coalesce(pagos_por_grupo.c.total_pagos, 0))).label('total_cobranza_real'),
            func.sum(func.coalesce(Prestamo.monto_prestamo, 0)).label('total_prestamo_real'),
            func.sum(
                func.coalesce(Prestamo.monto_prestamo, 0) - 
                func.coalesce(pagos_por_grupo.c.total_pagos, 0)
            ).label('total_prestamo_papel'),
            func.count(func.distinct(Prestamo.prestamo_id)).label('total_numero_de_creditos'),
            func.count(func.distinct(Prestamo.prestamo_id)).label('total_numero_de_prestamos'),
            func.array_agg(Grupo.grupo_id).label('grupo_ids')  # Listado de IDs de grupo
        ).select_from(Grupo)

        # Agregar los joins necesarios
        query_totales = query_totales.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)
        query_totales = query_totales.outerjoin(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
        query_totales = query_totales.outerjoin(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
        query_totales = query_totales.outerjoin(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
        query_totales = query_totales.outerjoin(pagos_por_grupo, pagos_por_grupo.c.grupo_id == Grupo.grupo_id)

        # Aplicar filtros de usuario si existen
        if filters:
            query_totales = query_totales.filter(*filters)

        # Ejecutar la consulta
        result_totales = query_totales.one()

        # Calcular el bono si es titular
        total_bono = 0
        if user_role_id == 2:  # Titular
            grupo_ids = result_totales.grupo_ids or []
            for grupo_id in grupo_ids:
                bono_data = ReporteService.calcular_bono_por_grupo(grupo_id)
                total_bono += bono_data['bono_aplicado']['monto'] if bono_data['bono_aplicado'] else 0

        # Extraer resultados y calcular adicionales
        total_cobranza_ideal = result_totales.total_cobranza_ideal or 0
        total_cobranza_real = float(result_totales.total_cobranza_real or 0)
        total_prestamo_real = float(result_totales.total_prestamo_real or 0)
        total_prestamo_papel = float(result_totales.total_prestamo_papel or 0)
        total_numero_de_creditos = result_totales.total_numero_de_creditos or 0
        total_numero_de_prestamos = result_totales.total_numero_de_prestamos or 0

        # Morosidad y métricas relacionadas
        morosidad_monto = max(total_cobranza_ideal - total_cobranza_real, 0)
        morosidad_porcentaje = (morosidad_monto / total_cobranza_ideal) * 100 if total_cobranza_ideal != 0 else 0
        porcentaje_prestamo = (total_prestamo_real / total_cobranza_ideal) * 100 if total_cobranza_ideal != 0 else 0
        sobrante = total_cobranza_real - total_prestamo_papel

        # Construir el resultado
        return {
            'total_cobranza_ideal': total_cobranza_ideal,
            'total_cobranza_real': total_cobranza_real,
            'total_prestamo_real': total_prestamo_real,
            'total_prestamo_papel': total_prestamo_papel,
            'total_numero_de_creditos': total_numero_de_creditos,
            'total_numero_de_prestamos': total_numero_de_prestamos,
            'morosidad_monto': morosidad_monto,
            'morosidad_porcentaje': morosidad_porcentaje,
            'porcentaje_prestamo': porcentaje_prestamo,
            'sobrante': sobrante,
            'total_bono': total_bono
        }




    
    @staticmethod
    def obtener_sobrante_total_usuario_por_prestamo(user_id):
        # Filtrar grupos por rol del usuario
        usuario = UsuarioService.get_user_by_id(user_id)
        user_role_id = usuario.rol_id
        filters = []

        if user_role_id in [5, 6]:
            pass
        elif user_role_id == 4:
            filters.append(Ruta.usuario_id_gerente == user_id)
        elif user_role_id == 3:
            filters.append(Ruta.usuario_id_supervisor == user_id)
        elif user_role_id == 2:
            filters.append(Grupo.usuario_id_titular == user_id)
        
        # Subconsulta para calcular el sobrante por préstamo en cada grupo del usuario
        sobrante_por_prestamo = (
            db.session.query(
                Prestamo.prestamo_id,
                (func.coalesce(func.sum(Pago.monto_pagado), 0) - Prestamo.monto_prestamo).label('sobrante')
            )
            .join(ClienteAval, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(Grupo, ClienteAval.grupo_id == Grupo.grupo_id)
            .outerjoin(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
            .filter(*filters)
            .group_by(Prestamo.prestamo_id)
        ).subquery()

        # Consulta para sumar el sobrante total de todos los préstamos del usuario
        total_sobrante = (
            db.session.query(func.coalesce(func.sum(sobrante_por_prestamo.c.sobrante), 0).label('total_sobrante'))
            .scalar()
        )

        # Devuelve el total de sobrante por usuario
        return total_sobrante
        
    # CALCULO DE BONOS --------------------------------------------------------------------------
    @staticmethod
    def calcular_bono_por_grupo(grupo_id):
        
        current_date = datetime.now(TIMEZONE).date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Obtener la cobranza real de la semana sumando los pagos de los préstamos en esa semana
        cobranza_real_semanal = (
            db.session.query(func.sum(Pago.monto_pagado).label('cobranza_real'))
            .join(Prestamo, Pago.prestamo_id == Prestamo.prestamo_id)
            .join(ClienteAval, Prestamo.cliente_id == ClienteAval.cliente_id)
            .filter(
                ClienteAval.grupo_id == grupo_id,
                Pago.fecha_pago >= start_of_week,
                Pago.fecha_pago <= end_of_week
            )
        ).scalar() or 0  # Asegurarse de que sea al menos 0

        # Contar las faltas del grupo en la semana
        faltas_de_grupo = (
            db.session.query(func.count(Falta.id).label('faltas'))
            .join(Prestamo, Falta.prestamo_id == Prestamo.prestamo_id)
            .join(ClienteAval, Prestamo.cliente_id == ClienteAval.cliente_id)
            .filter(
                ClienteAval.grupo_id == grupo_id,
                Falta.fecha >= start_of_week,
                Falta.fecha <= end_of_week
            )
        ).scalar() or 0  # Asegurarse de que sea al menos 0

        # Iterar sobre los posibles bonos y verificar si el grupo cumple con los criterios
        bonos = db.session.query(Bono).all()
        bono_aplicado = None
        for bono in bonos:
            if bono.regla_bono(cobranza_real_semanal, faltas_de_grupo):
                bono_aplicado = bono
                break

        # Retornar el bono y la cobranza real de la semana
        return {
            'grupo_id': grupo_id,
            'cobranza_real_semanal': cobranza_real_semanal,
            'faltas_de_grupo': faltas_de_grupo,
            'bono_aplicado': bono_aplicado.serialize() if bono_aplicado else None
        }

    @staticmethod
    def calcular_bono_para_grupos_de_titular(user_id):
        # Obtener los grupos donde el usuario es el titular
        grupos = db.session.query(Grupo).filter(Grupo.usuario_id_titular == user_id).all()
        report_data = []

        # Calcular bono y cobranza real para cada grupo del titular
        for grupo in grupos:
            reporte_grupo = ReporteService.calcular_bono_por_grupo(grupo.grupo_id)
            report_data.append(reporte_grupo)

        return report_data
    
    @staticmethod
    def calcular_bono_global_titular(user_id):
        # Obtener los grupos donde el usuario es el titular
        grupos = db.session.query(Grupo).filter(Grupo.usuario_id_titular == user_id).all()
        total_bono = 0
        

        # Calcular bono para cada grupo y sumar los montos de los bonos aplicados
        for grupo in grupos:
            reporte_grupo = ReporteService.calcular_bono_por_grupo(grupo.grupo_id)
            
            
            # Si el grupo tiene un bono aplicado, sumar el monto del bono
            if reporte_grupo['bono_aplicado']:
                total_bono += reporte_grupo['bono_aplicado']['monto']

        # Retornar el total del bono para todos los grupos del titular
        return total_bono
    
    # CALCULO DE BONOS --------------------------------------------------------------------------
    
    
    
    
    
    