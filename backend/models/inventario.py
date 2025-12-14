# Modelo de Inventario
# Centro Minero SENA

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Inventario:
    """Modelo de datos para Item de Inventario"""
    
    id: str
    nombre: str
    categoria: str
    cantidad_actual: int = 0
    cantidad_minima: int = 0
    unidad: str = 'unidades'
    proveedor: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    costo_unitario: Optional[float] = None
    ubicacion: Optional[str] = None
    descripcion: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones después de inicialización"""
        if self.cantidad_actual < 0:
            raise ValueError("La cantidad actual no puede ser negativa")
        
        if self.cantidad_minima < 0:
            raise ValueError("La cantidad mínima no puede ser negativa")
    
    def to_dict(self) -> dict:
        """Convierte el item a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'cantidad_actual': self.cantidad_actual,
            'cantidad_minima': self.cantidad_minima,
            'unidad': self.unidad,
            'proveedor': self.proveedor,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'costo_unitario': self.costo_unitario,
            'ubicacion': self.ubicacion,
            'descripcion': self.descripcion,
            'nivel_stock': self.obtener_nivel_stock()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Inventario':
        """Crea un item desde un diccionario"""
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            categoria=data['categoria'],
            cantidad_actual=data.get('cantidad_actual', 0),
            cantidad_minima=data.get('cantidad_minima', 0),
            unidad=data.get('unidad', 'unidades'),
            proveedor=data.get('proveedor'),
            fecha_vencimiento=data.get('fecha_vencimiento'),
            costo_unitario=data.get('costo_unitario'),
            ubicacion=data.get('ubicacion'),
            descripcion=data.get('descripcion')
        )
    
    def obtener_nivel_stock(self) -> str:
        """Obtiene el nivel de stock del item"""
        if self.cantidad_actual <= self.cantidad_minima:
            return 'critico'
        elif self.cantidad_actual <= self.cantidad_minima * 1.5:
            return 'bajo'
        else:
            return 'normal'
    
    def esta_en_stock_critico(self) -> bool:
        """Verifica si el item está en stock crítico"""
        return self.cantidad_actual <= self.cantidad_minima
    
    def esta_proximo_a_vencer(self, dias: int = 30) -> bool:
        """Verifica si el item está próximo a vencer"""
        if not self.fecha_vencimiento:
            return False
        
        from datetime import datetime, timedelta
        dias_restantes = (self.fecha_vencimiento - date.today()).days
        return 0 <= dias_restantes <= dias
    
    def agregar_cantidad(self, cantidad: int) -> bool:
        """Agrega cantidad al inventario"""
        if cantidad <= 0:
            return False
        
        self.cantidad_actual += cantidad
        return True
    
    def retirar_cantidad(self, cantidad: int) -> bool:
        """Retira cantidad del inventario"""
        if cantidad <= 0 or cantidad > self.cantidad_actual:
            return False
        
        self.cantidad_actual -= cantidad
        return True
    
    def calcular_valor_total(self) -> float:
        """Calcula el valor total del inventario"""
        if self.costo_unitario:
            return self.cantidad_actual * self.costo_unitario
        return 0.0
