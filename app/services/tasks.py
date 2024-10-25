from datetime import datetime, timedelta
from app.models import Prestamo
from app.constants import TIMEZONE

def verificar_pagos_semanal():
    print("Cronjob ejecutado: Verificación de pagos semanal.")
    """
    Verifica todos los préstamos activos para ver si cumplieron con la cobranza ideal durante la semana anterior.
    """
    # Obtener la fecha y hora actuales en la zona horaria de Ciudad de México
    ahora = datetime.now(TIMEZONE)
    hoy = ahora.date()
    
    # Obtener el lunes de la semana anterior
    lunes_anterior = hoy - timedelta(days=hoy.weekday() + 7)

    # Obtener todos los préstamos activos
    prestamos_activos = Prestamo.query.filter_by(status='activo').all()

    # Verificar pagos semanales para cada préstamo
    for prestamo in prestamos_activos:
        prestamo.verificar_pagos_semana(lunes_anterior)
