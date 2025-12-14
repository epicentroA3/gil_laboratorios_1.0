# Modelo de Préstamo
# Centro Minero SENA
# Adaptado a schema.sql - tabla prestamos

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Estados válidos según schema.sql
ESTADOS_PRESTAMO = ['solicitado', 'aprobado', 'rechazado', 'activo', 'devuelto', 'vencido']
CALIFICACIONES_DEVOLUCION = ['excelente', 'bueno', 'regular', 'malo']


@dataclass
class Prestamo:
    """
    Modelo de datos para Préstamo de equipo
    Corresponde a tabla 'prestamos' en schema.sql
    """
    
    # Campos obligatorios
    id: int
    codigo: str
    id_equipo: int
    id_usuario_solicitante: int
    
    # Campos opcionales
    id_usuario_autorizador: Optional[int] = None
    fecha_solicitud: Optional[datetime] = None
    fecha: Optional[datetime] = None  # Fecha de inicio del préstamo
    fecha_devolucion_programada: Optional[datetime] = None
    fecha_devolucion_real: Optional[datetime] = None
    proposito: Optional[str] = None
    observaciones: Optional[str] = None
    observaciones_devolucion: Optional[str] = None
    estado: str = 'solicitado'
    calificacion_devolucion: Optional[str] = None
    
    # Datos relacionados (para vistas)
    equipo_nombre: Optional[str] = None
    equipo_codigo: Optional[str] = None
    usuario_solicitante_nombre: Optional[str] = None
    usuario_autorizador_nombre: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        if self.estado not in ESTADOS_PRESTAMO:
            raise ValueError(f"Estado inválido: {self.estado}. Debe ser uno de: {ESTADOS_PRESTAMO}")
        
        if self.calificacion_devolucion and self.calificacion_devolucion not in CALIFICACIONES_DEVOLUCION:
            raise ValueError(f"Calificación inválida: {self.calificacion_devolucion}")
        
        if not self.fecha_solicitud:
            self.fecha_solicitud = datetime.now()
    
    @property
    def esta_activo(self) -> bool:
        """Verifica si el préstamo está activo"""
        return self.estado == 'activo'
    
    @property
    def esta_vencido(self) -> bool:
        """Verifica si el préstamo está vencido"""
        if self.estado == 'vencido':
            return True
        if self.estado == 'activo' and self.fecha_devolucion_programada:
            return datetime.now() > self.fecha_devolucion_programada
        return False
    
    @property
    def dias_restantes(self) -> Optional[int]:
        """Calcula días restantes para devolución"""
        if not self.fecha_devolucion_programada or self.estado in ['devuelto', 'rechazado']:
            return None
        delta = self.fecha_devolucion_programada - datetime.now()
        return delta.days
    
    def to_dict(self) -> dict:
        """Convierte el préstamo a diccionario"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'id_equipo': self.id_equipo,
            'id_usuario_solicitante': self.id_usuario_solicitante,
            'id_usuario_autorizador': self.id_usuario_autorizador,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'fecha_devolucion_programada': self.fecha_devolucion_programada.isoformat() if self.fecha_devolucion_programada else None,
            'fecha_devolucion_real': self.fecha_devolucion_real.isoformat() if self.fecha_devolucion_real else None,
            'proposito': self.proposito,
            'observaciones': self.observaciones,
            'observaciones_devolucion': self.observaciones_devolucion,
            'estado': self.estado,
            'calificacion_devolucion': self.calificacion_devolucion,
            'esta_activo': self.esta_activo,
            'esta_vencido': self.esta_vencido,
            'dias_restantes': self.dias_restantes,
            # Datos relacionados
            'equipo_nombre': self.equipo_nombre,
            'equipo_codigo': self.equipo_codigo,
            'usuario_solicitante_nombre': self.usuario_solicitante_nombre,
            'usuario_autorizador_nombre': self.usuario_autorizador_nombre
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Prestamo':
        """Crea un préstamo desde un diccionario (resultado de BD)"""
        # Mapear estados legacy de 'reserva' a 'prestamo'
        estado = data.get('estado', 'solicitado')
        mapeo_estados = {
            'programada': 'solicitado',
            'activa': 'activo',
            'completada': 'devuelto',
            'cancelada': 'rechazado'
        }
        estado = mapeo_estados.get(estado, estado)
        
        return cls(
            id=data.get('id', 0),
            codigo=data.get('codigo', ''),
            id_equipo=data.get('id_equipo', 0),
            id_usuario_solicitante=data.get('id_usuario_solicitante', 0),
            id_usuario_autorizador=data.get('id_usuario_autorizador'),
            fecha_solicitud=data.get('fecha_solicitud'),
            fecha=data.get('fecha') or data.get('fecha_inicio'),
            fecha_devolucion_programada=data.get('fecha_devolucion_programada') or data.get('fecha_fin'),
            fecha_devolucion_real=data.get('fecha_devolucion_real'),
            proposito=data.get('proposito'),
            observaciones=data.get('observaciones'),
            observaciones_devolucion=data.get('observaciones_devolucion'),
            estado=estado,
            calificacion_devolucion=data.get('calificacion_devolucion'),
            equipo_nombre=data.get('equipo_nombre'),
            equipo_codigo=data.get('equipo_codigo') or data.get('codigo_interno'),
            usuario_solicitante_nombre=data.get('usuario_solicitante_nombre') or data.get('usuario_nombre'),
            usuario_autorizador_nombre=data.get('usuario_autorizador_nombre')
        )
    
    def puede_aprobarse(self) -> bool:
        """Verifica si el préstamo puede aprobarse"""
        return self.estado == 'solicitado'
    
    def puede_rechazarse(self) -> bool:
        """Verifica si el préstamo puede rechazarse"""
        return self.estado == 'solicitado'
    
    def puede_activarse(self) -> bool:
        """Verifica si el préstamo puede activarse"""
        return self.estado == 'aprobado'
    
    def puede_devolverse(self) -> bool:
        """Verifica si el préstamo puede devolverse"""
        return self.estado == 'activo'
    
    def aprobar(self, id_autorizador: int) -> bool:
        """Aprueba el préstamo"""
        if not self.puede_aprobarse():
            return False
        self.estado = 'aprobado'
        self.id_usuario_autorizador = id_autorizador
        return True
    
    def rechazar(self, id_autorizador: int, motivo: str = None) -> bool:
        """Rechaza el préstamo"""
        if not self.puede_rechazarse():
            return False
        self.estado = 'rechazado'
        self.id_usuario_autorizador = id_autorizador
        if motivo:
            self.observaciones = motivo
        return True
    
    def activar(self) -> bool:
        """Activa el préstamo (entrega del equipo)"""
        if not self.puede_activarse():
            return False
        self.estado = 'activo'
        self.fecha = datetime.now()
        return True
    
    def devolver(self, calificacion: str = None, observaciones: str = None) -> bool:
        """Registra la devolución del préstamo"""
        if not self.puede_devolverse():
            return False
        self.estado = 'devuelto'
        self.fecha_devolucion_real = datetime.now()
        if calificacion and calificacion in CALIFICACIONES_DEVOLUCION:
            self.calificacion_devolucion = calificacion
        if observaciones:
            self.observaciones_devolucion = observaciones
        return True
    
    def marcar_vencido(self) -> bool:
        """Marca el préstamo como vencido"""
        if self.estado != 'activo':
            return False
        self.estado = 'vencido'
        return True


# Alias para compatibilidad con código legacy
Reserva = Prestamo
