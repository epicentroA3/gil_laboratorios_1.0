# Modelos del Sistema GIL
# Centro Minero de Sogamoso - SENA
# Adaptados a schema.sql

from .usuario import Usuario, ROLES, ESTADOS_USUARIO
from .equipo import Equipo, ESTADOS_EQUIPO, ESTADOS_FISICOS
from .prestamo import Prestamo, ESTADOS_PRESTAMO, CALIFICACIONES_DEVOLUCION, Reserva
from .inventario import Inventario

__all__ = [
    # Usuario
    'Usuario',
    'ROLES',
    'ESTADOS_USUARIO',
    
    # Equipo
    'Equipo',
    'ESTADOS_EQUIPO',
    'ESTADOS_FISICOS',
    
    # Préstamo
    'Prestamo',
    'Reserva',  # Alias para compatibilidad
    'ESTADOS_PRESTAMO',
    'CALIFICACIONES_DEVOLUCION',
    
    # Inventario
    'Inventario'
]
