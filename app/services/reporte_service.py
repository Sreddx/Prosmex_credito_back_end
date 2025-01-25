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

        # Definición de alias para usuarios
        usuarios_gerente = aliased(Usuario)
        usuarios_supervisor = aliased(Usuario)
        usuarios_titular = aliased(Usuario)

        # Configuración de fechas para la semana actual
        mexico_city_tz = pytz.timezone('America/Mexico_City')
        current_date = datetime.now(mexico_city_tz).date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Subconsulta para pagos por grupo (cobranza real) - sólo préstamos activos
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
                Pago.fecha_pago <= end_of_week,
                Prestamo.completado == False
            )
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Subconsulta para cobranza ideal por grupo - sólo préstamos activos
        cobranza_ideal_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(Prestamo.monto_prestamo * TipoPrestamo.porcentaje_semanal).label('cobranza_ideal')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
            .filter(Prestamo.completado == False)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Subconsulta para número de créditos por grupo
        numero_de_creditos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.count(Prestamo.prestamo_id).label('numero_de_creditos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Subconsulta para número de préstamos activos por grupo
        numero_de_prestamos_activos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.count(Prestamo.prestamo_id).label('numero_de_prestamos_activos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .filter(Prestamo.completado == False)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Construcción de la consulta principal
        query = db.session.query(
            Grupo.grupo_id,
            Ruta.ruta_id,
            func.coalesce(func.concat(usuarios_gerente.nombre, ' ', usuarios_gerente.apellido_paterno), '').label('gerente'),
            func.coalesce(func.concat(usuarios_supervisor.nombre, ' ', usuarios_supervisor.apellido_paterno), '').label('supervisor'),
            func.coalesce(func.concat(usuarios_titular.nombre, ' ', usuarios_titular.apellido_paterno), '').label('titular'),
            Ruta.nombre_ruta.label('ruta'),
            Grupo.nombre_grupo.label('grupo'),
            func.coalesce(cobranza_ideal_por_grupo.c.cobranza_ideal, 0).label('cobranza_ideal'),
            func.coalesce(pagos_por_grupo.c.total_pagos, 0).label('cobranza_real'),
            func.coalesce(numero_de_creditos_por_grupo.c.numero_de_creditos, 0).label('numero_de_creditos'),
            func.coalesce(numero_de_prestamos_activos_por_grupo.c.numero_de_prestamos_activos, 0).label('prestamos_activos')
        ).select_from(Grupo)

        # Joins necesarios
        query = query.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)
        query = query.outerjoin(usuarios_supervisor, Ruta.usuario_id_supervisor == usuarios_supervisor.id)
        query = query.outerjoin(usuarios_gerente, Ruta.usuario_id_gerente == usuarios_gerente.id)
        query = query.outerjoin(usuarios_titular, Grupo.usuario_id_titular == usuarios_titular.id)
        query = query.outerjoin(pagos_por_grupo, pagos_por_grupo.c.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(cobranza_ideal_por_grupo, cobranza_ideal_por_grupo.c.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(numero_de_creditos_por_grupo, numero_de_creditos_por_grupo.c.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(numero_de_prestamos_activos_por_grupo, numero_de_prestamos_activos_por_grupo.c.grupo_id == Grupo.grupo_id)

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
            pagos_por_grupo.c.total_pagos,
            cobranza_ideal_por_grupo.c.cobranza_ideal,
            numero_de_creditos_por_grupo.c.numero_de_creditos,
            numero_de_prestamos_activos_por_grupo.c.numero_de_prestamos_activos
        )

        # Obtener el total de resultados antes de la paginación
        total_items = query.count()

        # Agregar paginación
        paginated_query = query.limit(per_page).offset((page - 1) * per_page)

        # Procesar los resultados de la consulta paginada
        results = paginated_query.all()
        report_data = []
        
        for row in results:
            # Obtener los valores de prestamo_real y prestamo_papel desde PrestamoService
            prestamo_real, prestamo_papel = PrestamoService().get_prestamo_real_y_papel_by_grupo(row.grupo_id)

            # Obtener el bono para cada grupo (si aplica)
            bono_data = ReporteService.calcular_bono_por_grupo(row.grupo_id)
            bono = bono_data['bono_aplicado']['monto'] if bono_data['bono_aplicado'] else 0

            # Cálculos adicionales
            cobranza_ideal = float(row.cobranza_ideal or 0)
            cobranza_real = float(row.cobranza_real or 0)

            morosidad_monto = cobranza_ideal - cobranza_real if cobranza_ideal else 0
            morosidad_porcentaje = (morosidad_monto / cobranza_ideal) if cobranza_ideal != 0 else None
            porcentaje_prestamo = (prestamo_real / cobranza_real) if cobranza_real != 0 else None
            sobrante = cobranza_real - prestamo_papel - bono
            sobrante_logico = float(Grupo.calcular_sobrante_grupo(row.grupo_id) - bono)
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
                'morosidad_monto': morosidad_monto,
                'morosidad_porcentaje': morosidad_porcentaje,
                'porcentaje_prestamo': porcentaje_prestamo,
                'sobrante': sobrante,
                'sobrante_logico': sobrante_logico,
                'bono': bono,
                'numero_de_creditos': row.numero_de_creditos,
                'prestamos_activos': row.prestamos_activos
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
        import pytz
        mexico_city_tz = pytz.timezone('America/Mexico_City')
        current_date = datetime.now(mexico_city_tz).date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Subconsulta para pagos agrupados por grupo (cobranza real)
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
            .subquery()
        )

        # Subconsulta para calcular cobranza ideal por grupo
        cobranza_ideal_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(Prestamo.monto_prestamo * TipoPrestamo.porcentaje_semanal).label('cobranza_ideal')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
            .filter(Prestamo.completado == False)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        """
        # Subconsulta para total de prestamo_papel y prestamo_real por grupo usando propiedades híbridas
        prestamo_totales_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(func.coalesce(ClienteAval.prestamo_papel, 0)).label('total_prestamo_papel'),
                func.sum(func.coalesce(ClienteAval.prestamo_real, 0)).label('total_prestamo_real')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Imprimir los resultados de prestamo_totales_por_grupo
        resultados_prestamo_totales = db.session.query(
            prestamo_totales_por_grupo.c.grupo_id,
            prestamo_totales_por_grupo.c.total_prestamo_papel,
            prestamo_totales_por_grupo.c.total_prestamo_real
        ).all()

        for resultado in resultados_prestamo_totales:
            grupo_id = resultado.grupo_id
            total_prestamo_papel = resultado.total_prestamo_papel
            total_prestamo_real = resultado.total_prestamo_real
            print(f"Grupo ID: {grupo_id}, Total Prestamo Papel: {total_prestamo_papel}, Total Prestamo Real: {total_prestamo_real}")
        """
        
        # Subconsulta para número de créditos por grupo
        numero_de_creditos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.count(Prestamo.prestamo_id).label('numero_de_creditos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .group_by(Grupo.grupo_id)
            .subquery()
        )
        
        # Subconsulta para total numero de prestamos activos por grupo
        numero_de_prestamos_activos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.count(Prestamo.prestamo_id).label('numero_de_prestamos_activos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .filter(Prestamo.completado == False)
            .group_by(Grupo.grupo_id)
            .subquery()
        )

        # Construcción de la consulta principal para los totales
        query_totales = db.session.query(
            func.sum(cobranza_ideal_por_grupo.c.cobranza_ideal).label('total_cobranza_ideal'),
            func.sum(pagos_por_grupo.c.total_pagos).label('total_cobranza_real'),
            #func.sum(prestamo_totales_por_grupo.c.total_prestamo_papel).label('total_prestamo_papel'),
            #func.sum(prestamo_totales_por_grupo.c.total_prestamo_real).label('total_prestamo_real'),
            func.sum(numero_de_creditos_por_grupo.c.numero_de_creditos).label('total_numero_de_creditos'),
            func.sum(numero_de_prestamos_activos_por_grupo.c.numero_de_prestamos_activos).label('total_numero_de_prestamos_activos'),
            #func.sum(morosidad_por_grupo.c.morosidad).label('total_morosidad'),
            func.array_agg(Grupo.grupo_id).label('grupo_ids')  # Listado de IDs de grupo
        ).select_from(Grupo)

        # Unir las subconsultas
        query_totales = query_totales.outerjoin(cobranza_ideal_por_grupo, cobranza_ideal_por_grupo.c.grupo_id == Grupo.grupo_id)
        query_totales = query_totales.outerjoin(pagos_por_grupo, pagos_por_grupo.c.grupo_id == Grupo.grupo_id)
        #query_totales = query_totales.outerjoin(prestamo_totales_por_grupo, prestamo_totales_por_grupo.c.grupo_id == Grupo.grupo_id)
        query_totales = query_totales.outerjoin(numero_de_creditos_por_grupo, numero_de_creditos_por_grupo.c.grupo_id == Grupo.grupo_id)
        query_totales = query_totales.outerjoin(numero_de_prestamos_activos_por_grupo, numero_de_prestamos_activos_por_grupo.c.grupo_id == Grupo.grupo_id)
        #query_totales = query_totales.outerjoin(morosidad_por_grupo, morosidad_por_grupo.c.grupo_id == Grupo.grupo_id)
        query_totales = query_totales.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)

        # Aplicar filtros de usuario si existen
        if filters:
            query_totales = query_totales.filter(*filters)

        # Ejecutar la consulta
        result_totales = query_totales.one()

        # Calcular el bono
        total_bono = 0
        
        #Calcular sobrante lógico
        total_sobrante_logico = 0

        #Calcular prestamo real y papel
        total_prestamo_real = 0
        total_prestamo_papel = 0
        
        grupo_ids = result_totales.grupo_ids or []
        for grupo_id in grupo_ids:
            #print(f'Grupo ID: {grupo_id}')
            bono_data = ReporteService.calcular_bono_por_grupo(grupo_id)
            total_bono += bono_data['bono_aplicado']['monto'] if bono_data['bono_aplicado'] else 0
            sobrante_logico = float(Grupo.calcular_sobrante_grupo(grupo_id)) - float(total_bono)
            total_sobrante_logico += sobrante_logico
            prestamo_real_grupo, prestamo_papel_grupo = PrestamoService().get_prestamo_real_y_papel_by_grupo(grupo_id)
            total_prestamo_papel += prestamo_papel_grupo
            total_prestamo_real += prestamo_real_grupo

        # Extraer resultados y calcular adicionales
        total_cobranza_ideal = float(result_totales.total_cobranza_ideal or 0)
        total_cobranza_real = float(result_totales.total_cobranza_real or 0)
        #total_prestamo_papel = float(result_totales.total_prestamo_papel or 0)
        #total_prestamo_real = float(result_totales.total_prestamo_real or 0)
        total_numero_de_creditos = int(result_totales.total_numero_de_creditos or 0)
        total_prestamos_activos = int(result_totales.total_numero_de_prestamos_activos or 0)
        
        # Morosidad y métricas relacionadas
        morosidad_monto = float(total_cobranza_ideal - total_cobranza_real)
        morosidad_porcentaje = round((morosidad_monto / total_cobranza_ideal) * 100, 2) if total_cobranza_ideal != 0 else 0
        porcentaje_prestamo = round((total_prestamo_real / total_cobranza_real) * 100, 2) if total_cobranza_real != 0 else 0
        sobrante = total_cobranza_real - total_prestamo_papel - total_bono

        # Construir el resultado
        return {
            'total_cobranza_ideal': total_cobranza_ideal,
            'total_cobranza_real': total_cobranza_real,
            'total_prestamo_real': total_prestamo_real,
            'total_prestamo_papel': total_prestamo_papel,
            'total_numero_de_creditos': total_numero_de_creditos,
            'total_prestamos_activos': total_prestamos_activos,
            'morosidad_monto': morosidad_monto,
            'morosidad_porcentaje': morosidad_porcentaje,
            'porcentaje_prestamo': porcentaje_prestamo,
            'sobrante': sobrante,
            'total_sobrante_logico': total_sobrante_logico,
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
                (func.coalesce(func.sum(Pago.monto_pagado), 0) - Prestamo.monto_utilidad).label('sobrante')
            )
            .join(ClienteAval, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(Grupo, ClienteAval.grupo_id == Grupo.grupo_id)
            .outerjoin(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
            .filter(*filters)
            .group_by(Prestamo.prestamo_id)
        ).subquery()

        # Imprimir los resultados de la consulta sobrante_por_prestamo
        results = db.session.query(sobrante_por_prestamo).all()
        for result in results:
            print(result.prestamo_id, result.sobrante)

        # Consulta para sumar el sobrante total de todos los préstamos del usuario
        total_sobrante = (
            db.session.query(func.coalesce(func.sum(sobrante_por_prestamo.c.sobrante), 0).label('total_sobrante'))
            .scalar()
        )

        print(total_sobrante)        

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
    
    
    
    
    
    
    
    