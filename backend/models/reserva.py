# Modelo de Reserva
# Centro Minero SENA

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Reserva:
    """Modelo de datos para Reserva de equipo"""
    
    id: str
    usuario_id: str
    equipo_id: str
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str = 'programada'  # 'programada', 'activa', 'completada', 'cancelada'
    observaciones: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        estados_validos = ['programada', 'activa', 'completada', 'cancelada']
        if self.estado not in estados_validos:
            raise ValueError(f"Estado inválido: {self.estado}")
        
        if self.fecha_inicio >= self.fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now()
    
    def to_dict(self) -> dict:
        """Convierte la reserva a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'equipo_id': self.equipo_id,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'estado': self.estado,
            'observaciones': self.observaciones,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'duracion_horas': self.calcular_duracion_horas()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Reserva':
        """Crea una reserva desde un diccionario"""
        return cls(
            id=data['id'],
            usuario_id=data['usuario_id'],
            equipo_id=data['equipo_id'],
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            estado=data.get('estado', 'programada'),
            observaciones=data.get('observaciones'),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def calcular_duracion_horas(self) -> float:
        """Calcula la duración de la reserva en horas"""
        duracion = self.fecha_fin - self.fecha_inicio
        return duracion.total_seconds() / 3600
    
    def esta_activa(self) -> bool:
        """Verifica si la reserva está activa"""
        return self.estado == 'activa'
    
    def puede_cancelarse(self) -> bool:
        """Verifica si la reserva puede cancelarse"""
        return self.estado in ['programada', 'activa']
    
    def puede_extenderse(self) -> bool:
        """Verifica si la reserva puede extenderse"""
        return self.estado == 'activa' and datetime.now() < self.fecha_fin
    
    def cambiar_estado(self, nuevo_estado: str) -> bool:
        """Cambia el estado de la reserva"""
        estados_validos = ['programada', 'activa', 'completada', 'cancelada']
        if nuevo_estado not in estados_validos:
            return False
        
        # Validar transiciones de estado
        transiciones_validas = {
            'programada': ['activa', 'cancelada'],
            'activa': ['completada', 'cancelada'],
            'completada': [],
            'cancelada': []
        }
        
        if nuevo_estado not in transiciones_validas.get(self.estado, []):
            return False
        
        self.estado = nuevo_estado
        return True
    
    def extender_reserva(self, nueva_fecha_fin: datetime) -> bool:
        """Extiende la fecha de fin de la reserva"""
        if not self.puede_extenderse():
            return False
        
        if nueva_fecha_fin <= self.fecha_fin:
            return False
        
        self.fecha_fin = nueva_fecha_fin
        return True
    
    def esta_en_conflicto(self, otra_fecha_inicio: datetime, otra_fecha_fin: datetime) -> bool:
        """Verifica si hay conflicto con otro rango de fechas"""
        if self.estado in ['completada', 'cancelada']:
            return False
        
        return not (otra_fecha_fin <= self.fecha_inicio or otra_fecha_inicio >= self.fecha_fin)
