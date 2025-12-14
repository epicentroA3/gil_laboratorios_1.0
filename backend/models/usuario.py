# Modelo de Usuario
# Centro Minero SENA
# Adaptado a schema.sql - tabla usuarios

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import Config
except ImportError:
    Config = None


# Mapeo de roles según schema.sql y data.sql
ROLES = {
    1: {'nombre': 'administrador', 'nivel': 5},
    2: {'nombre': 'instructor', 'nivel': 4},
    3: {'nombre': 'tecnico_laboratorio', 'nivel': 3},
    4: {'nombre': 'aprendiz', 'nivel': 2},
    5: {'nombre': 'monitor', 'nivel': 2},
    6: {'nombre': 'visitante', 'nivel': 1}
}

ESTADOS_USUARIO = ['activo', 'inactivo', 'suspendido']


@dataclass
class Usuario:
    """
    Modelo de datos para Usuario
    Corresponde a tabla 'usuarios' en schema.sql
    """
    
    # Campos obligatorios
    id: int
    documento: str
    nombres: str
    apellidos: str
    
    # Campos opcionales con defaults
    email: Optional[str] = None
    telefono: Optional[str] = None
    id_rol: int = 4  # Default: aprendiz
    password_hash: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    estado: str = 'activo'
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        if self.estado not in ESTADOS_USUARIO:
            raise ValueError(f"Estado inválido: {self.estado}. Debe ser uno de: {ESTADOS_USUARIO}")
        
        if self.id_rol not in ROLES:
            raise ValueError(f"Rol inválido: {self.id_rol}")
        
        if not self.fecha_registro:
            self.fecha_registro = datetime.now()
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def rol_nombre(self) -> str:
        """Retorna el nombre del rol"""
        return ROLES.get(self.id_rol, {}).get('nombre', 'desconocido')
    
    @property
    def nivel_acceso(self) -> int:
        """Retorna el nivel de acceso según el rol"""
        return ROLES.get(self.id_rol, {}).get('nivel', 1)
    
    @property
    def activo(self) -> bool:
        """Retorna si el usuario está activo"""
        return self.estado == 'activo'
    
    def to_dict(self) -> dict:
        """Convierte el usuario a diccionario"""
        return {
            'id': self.id,
            'documento': self.documento,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'telefono': self.telefono,
            'id_rol': self.id_rol,
            'rol_nombre': self.rol_nombre,
            'nivel_acceso': self.nivel_acceso,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'estado': self.estado,
            'activo': self.activo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Crea un usuario desde un diccionario (resultado de BD)"""
        # Manejar campo 'nombre' legacy que combina nombres y apellidos
        if 'nombre' in data and 'nombres' not in data:
            partes = data['nombre'].split(' ', 1)
            nombres = partes[0]
            apellidos = partes[1] if len(partes) > 1 else ''
        else:
            nombres = data.get('nombres', '')
            apellidos = data.get('apellidos', '')
        
        return cls(
            id=data.get('id', 0),
            documento=data.get('documento', str(data.get('id', ''))),
            nombres=nombres,
            apellidos=apellidos,
            email=data.get('email'),
            telefono=data.get('telefono'),
            id_rol=data.get('id_rol', 4),
            password_hash=data.get('password_hash'),
            fecha_registro=data.get('fecha_registro'),
            ultimo_acceso=data.get('ultimo_acceso'),
            estado=data.get('estado', 'activo')
        )
    
    def tiene_permiso(self, nivel_requerido: int) -> bool:
        """Verifica si el usuario tiene el nivel de acceso requerido"""
        return self.activo and self.nivel_acceso >= nivel_requerido
    
    def es_administrador(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.id_rol == 1 or self.nivel_acceso >= 5
    
    def es_instructor(self) -> bool:
        """Verifica si el usuario es instructor"""
        return self.id_rol in [1, 2] or self.nivel_acceso >= 4
    
    def es_tecnico(self) -> bool:
        """Verifica si el usuario es técnico de laboratorio"""
        return self.id_rol in [1, 2, 3] or self.nivel_acceso >= 3
    
    def puede_autorizar_prestamos(self) -> bool:
        """Verifica si puede autorizar préstamos"""
        return self.es_tecnico()
