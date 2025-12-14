# Modelo de Equipo
# Centro Minero SENA
# Adaptado a schema.sql - tabla equipos

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict
from decimal import Decimal
import json

# Estados válidos según schema.sql
ESTADOS_EQUIPO = ['disponible', 'prestado', 'mantenimiento', 'reparacion', 'dado_baja']
ESTADOS_FISICOS = ['excelente', 'bueno', 'regular', 'malo']


@dataclass
class Equipo:
    """
    Modelo de datos para Equipo de laboratorio
    Corresponde a tabla 'equipos' en schema.sql
    """
    
    # Campos obligatorios
    id: int
    codigo_interno: str
    nombre: str
    
    # Campos opcionales
    codigo_qr: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    id_categoria: Optional[int] = None
    id_laboratorio: Optional[int] = None
    descripcion: Optional[str] = None
    especificaciones_tecnicas: Optional[Dict] = None
    valor_adquisicion: Optional[Decimal] = None
    fecha_adquisicion: Optional[date] = None
    proveedor: Optional[str] = None
    garantia_meses: int = 12
    vida_util_anos: int = 5
    imagen_url: Optional[str] = None
    imagen_hash: Optional[str] = None
    estado: str = 'disponible'
    estado_fisico: str = 'bueno'
    ubicacion_especifica: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        if self.estado not in ESTADOS_EQUIPO:
            raise ValueError(f"Estado inválido: {self.estado}. Debe ser uno de: {ESTADOS_EQUIPO}")
        
        if self.estado_fisico not in ESTADOS_FISICOS:
            raise ValueError(f"Estado físico inválido: {self.estado_fisico}. Debe ser uno de: {ESTADOS_FISICOS}")
        
        if self.especificaciones_tecnicas is None:
            self.especificaciones_tecnicas = {}
        elif isinstance(self.especificaciones_tecnicas, str):
            try:
                self.especificaciones_tecnicas = json.loads(self.especificaciones_tecnicas)
            except:
                self.especificaciones_tecnicas = {}
        
        if not self.fecha_registro:
            self.fecha_registro = datetime.now()
    
    @property
    def tipo(self) -> str:
        """Retorna tipo compuesto de marca y modelo (compatibilidad)"""
        partes = [self.marca or '', self.modelo or '']
        return ' '.join(p for p in partes if p).strip() or 'Sin especificar'
    
    def to_dict(self) -> dict:
        """Convierte el equipo a diccionario"""
        return {
            'id': self.id,
            'codigo_interno': self.codigo_interno,
            'codigo_qr': self.codigo_qr,
            'nombre': self.nombre,
            'marca': self.marca,
            'modelo': self.modelo,
            'tipo': self.tipo,
            'numero_serie': self.numero_serie,
            'id_categoria': self.id_categoria,
            'id_laboratorio': self.id_laboratorio,
            'descripcion': self.descripcion,
            'especificaciones_tecnicas': self.especificaciones_tecnicas,
            'valor_adquisicion': float(self.valor_adquisicion) if self.valor_adquisicion else None,
            'fecha_adquisicion': self.fecha_adquisicion.isoformat() if self.fecha_adquisicion else None,
            'proveedor': self.proveedor,
            'garantia_meses': self.garantia_meses,
            'vida_util_anos': self.vida_util_anos,
            'imagen_url': self.imagen_url,
            'estado': self.estado,
            'estado_fisico': self.estado_fisico,
            'ubicacion_especifica': self.ubicacion_especifica,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'disponible': self.esta_disponible()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Equipo':
        """Crea un equipo desde un diccionario (resultado de BD)"""
        # Manejar campos legacy
        especificaciones = data.get('especificaciones_tecnicas') or data.get('especificaciones')
        if isinstance(especificaciones, str):
            try:
                especificaciones = json.loads(especificaciones)
            except:
                especificaciones = {}
        
        # Mapear estado legacy si existe
        estado = data.get('estado', 'disponible')
        if estado == 'en_uso':
            estado = 'prestado'
        elif estado == 'fuera_servicio':
            estado = 'dado_baja'
        
        return cls(
            id=data.get('id', 0),
            codigo_interno=data.get('codigo_interno', str(data.get('id', ''))),
            nombre=data.get('nombre') or data.get('nombre_equipo', ''),
            codigo_qr=data.get('codigo_qr'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            id_categoria=data.get('id_categoria'),
            id_laboratorio=data.get('id_laboratorio'),
            descripcion=data.get('descripcion'),
            especificaciones_tecnicas=especificaciones,
            valor_adquisicion=data.get('valor_adquisicion'),
            fecha_adquisicion=data.get('fecha_adquisicion'),
            proveedor=data.get('proveedor'),
            garantia_meses=data.get('garantia_meses', 12),
            vida_util_anos=data.get('vida_util_anos', 5),
            imagen_url=data.get('imagen_url') or data.get('imagen_path'),
            imagen_hash=data.get('imagen_hash'),
            estado=estado,
            estado_fisico=data.get('estado_fisico', 'bueno'),
            ubicacion_especifica=data.get('ubicacion_especifica') or data.get('ubicacion'),
            observaciones=data.get('observaciones'),
            fecha_registro=data.get('fecha_registro'),
            fecha_actualizacion=data.get('fecha_actualizacion')
        )
    
    def esta_disponible(self) -> bool:
        """Verifica si el equipo está disponible para préstamo"""
        return self.estado == 'disponible'
    
    def esta_prestado(self) -> bool:
        """Verifica si el equipo está prestado"""
        return self.estado == 'prestado'
    
    def puede_prestarse(self) -> bool:
        """Verifica si el equipo puede prestarse"""
        return self.estado == 'disponible' and self.estado_fisico in ['excelente', 'bueno', 'regular']
    
    def cambiar_estado(self, nuevo_estado: str) -> bool:
        """Cambia el estado del equipo"""
        if nuevo_estado not in ESTADOS_EQUIPO:
            return False
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.now()
        return True
    
    def marcar_prestado(self) -> bool:
        """Marca el equipo como prestado"""
        return self.cambiar_estado('prestado')
    
    def marcar_disponible(self) -> bool:
        """Marca el equipo como disponible"""
        return self.cambiar_estado('disponible')
    
    def marcar_mantenimiento(self) -> bool:
        """Marca el equipo en mantenimiento"""
        return self.cambiar_estado('mantenimiento')
    
    def agregar_especificacion(self, clave: str, valor: str):
        """Agrega una especificación al equipo"""
        if self.especificaciones_tecnicas is None:
            self.especificaciones_tecnicas = {}
        self.especificaciones_tecnicas[clave] = valor
