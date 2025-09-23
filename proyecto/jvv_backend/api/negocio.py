def sifechaestadentrodeunrango(fecha, rango):
    """
    Verifica si una fecha está dentro de un rango dado.

    :param fecha: Fecha a verificar.
    :param rango: Tupla con la fecha de inicio y fin del rango (fecha_inicio, fecha_fin).
    :return: True si la fecha está dentro del rango, False en caso contrario.
    """
    fecha_inicio, fecha_fin = rango
    return fecha_inicio <= fecha <= fecha_fin