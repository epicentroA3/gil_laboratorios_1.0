# Validadores
# Centro Minero SENA

import re
from datetime import datetime, date
from typing import Any, Optional

class Validator:
    """Clase con métodos de validación"""
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            True si el formato es válido
        """
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))
    
    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """
        Valida formato de teléfono colombiano
        
        Args:
            telefono: Teléfono a validar
            
        Returns:
            True si el formato es válido
        """
        # Formato: 10 dígitos, puede empezar con 3
        patron = r'^3\d{9}$|^\d{10}$'
        return bool(re.match(patron, telefono))
    
    @staticmethod
    def validar_fecha(fecha_str: str, formato: str = '%Y-%m-%d') -> bool:
        """
        Valida formato de fecha
        
        Args:
            fecha_str: Fecha en string
            formato: Formato esperado
            
        Returns:
            True si el formato es válido
        """
        try:
            datetime.strptime(fecha_str, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_fecha_hora(fecha_hora_str: str, formato: str = '%Y-%m-%d %H:%M:%S') -> bool:
        """
        Valida formato de fecha y hora
        
        Args:
            fecha_hora_str: Fecha y hora en string
            formato: Formato esperado
            
        Returns:
            True si el formato es válido
        """
        try:
            datetime.strptime(fecha_hora_str, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_rango_fechas(fecha_inicio: datetime, fecha_fin: datetime) -> bool:
        """
        Valida que fecha_inicio sea anterior a fecha_fin
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            True si el rango es válido
        """
        return fecha_inicio < fecha_fin
    
    @staticmethod
    def validar_numero_positivo(numero: Any) -> bool:
        """
        Valida que un número sea positivo
        
        Args:
            numero: Número a validar
            
        Returns:
            True si es positivo
        """
        try:
            return float(numero) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_entero_positivo(numero: Any) -> bool:
        """
        Valida que un número sea entero positivo
        
        Args:
            numero: Número a validar
            
        Returns:
            True si es entero positivo
        """
        try:
            return int(numero) > 0 and float(numero) == int(numero)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validar_longitud(texto: str, min_len: int = 0, max_len: Optional[int] = None) -> bool:
        """
        Valida la longitud de un texto
        
        Args:
            texto: Texto a validar
            min_len: Longitud mínima
            max_len: Longitud máxima (opcional)
            
        Returns:
            True si la longitud es válida
        """
        longitud = len(texto)
        if longitud < min_len:
            return False
        if max_len and longitud > max_len:
            return False
        return True
    
    @staticmethod
    def validar_enum(valor: str, valores_validos: list) -> bool:
        """
        Valida que un valor esté en una lista de valores válidos
        
        Args:
            valor: Valor a validar
            valores_validos: Lista de valores válidos
            
        Returns:
            True si el valor es válido
        """
        return valor in valores_validos
    
    @staticmethod
    def validar_id_formato(id_str: str, prefijo: str, longitud: int) -> bool:
        """
        Valida formato de ID con prefijo
        
        Args:
            id_str: ID a validar
            prefijo: Prefijo esperado (ej: 'USR', 'EQP')
            longitud: Longitud total esperada
            
        Returns:
            True si el formato es válido
        """
        if len(id_str) != longitud:
            return False
        if not id_str.startswith(prefijo):
            return False
        return True
    
    @staticmethod
    def validar_cantidad_stock(cantidad_actual: int, cantidad_minima: int) -> str:
        """
        Valida el nivel de stock
        
        Args:
            cantidad_actual: Cantidad actual
            cantidad_minima: Cantidad mínima
            
        Returns:
            Nivel de stock: 'critico', 'bajo', 'normal'
        """
        if cantidad_actual <= cantidad_minima:
            return 'critico'
        elif cantidad_actual <= cantidad_minima * 1.5:
            return 'bajo'
        else:
            return 'normal'
    
    @staticmethod
    def sanitizar_texto(texto: str) -> str:
        """
        Sanitiza un texto removiendo caracteres peligrosos
        
        Args:
            texto: Texto a sanitizar
            
        Returns:
            Texto sanitizado
        """
        # Remover caracteres potencialmente peligrosos para SQL
        texto = texto.replace("'", "''")
        texto = texto.replace('"', '""')
        return texto.strip()
    
    @staticmethod
    def validar_json_string(json_str: str) -> bool:
        """
        Valida si un string es JSON válido
        
        Args:
            json_str: String JSON
            
        Returns:
            True si es JSON válido
        """
        import json
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
