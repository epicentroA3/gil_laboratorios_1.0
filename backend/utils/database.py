# Gestión de Base de Datos
# Centro Minero SENA
# Integrado con configuración centralizada

import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import sys
import os

# Agregar path para importar config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import Config
except ImportError:
    # Fallback si no se puede importar Config
    class Config:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = int(os.getenv('DB_PORT', 3306))
        DB_NAME = os.getenv('DB_NAME', 'gil_laboratorios')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
        DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
        DB_POOL_NAME = 'gil_pool'
        DB_POOL_SIZE = 5


class DatabaseManager:
    """Gestor de conexiones y operaciones de base de datos"""
    
    _pool = None  # Pool de conexiones compartido
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el gestor de base de datos usando Config centralizada
        
        Args:
            config: Diccionario con configuración de conexión (opcional, usa Config por defecto)
        """
        if config is None:
            config = {
                'host': Config.DB_HOST,
                'port': Config.DB_PORT,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD,
                'database': Config.DB_NAME,
                'charset': Config.DB_CHARSET,
                'use_unicode': True,
                'collation': 'utf8mb4_unicode_ci'
            }
        
        self.config = config
        self.connection = None
        self.use_pool = True
    
    def conectar(self) -> bool:
        """
        Establece conexión con la base de datos
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return True
            return False
        except Error as e:
            print(f"Error conectando a la base de datos: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_connection(self):
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            Objeto de conexión MySQL
        """
        if not self.connection or not self.connection.is_connected():
            self.conectar()
        # Refrescar conexión para evitar caché de datos
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=1)
        except:
            self.conectar()
        return self.connection
    
    def ejecutar_query(self, query: str, params: Optional[tuple] = None, 
            dictionary: bool = True) -> List[Dict]:
        """
        Ejecuta una consulta SELECT
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            dictionary: Si True, retorna diccionarios en lugar de tuplas
            
        Returns:
            Lista de resultados
        """
        try:
            # Crear nueva conexión para cada query para evitar caché
            conn = mysql.connector.connect(**self.config)
            conn.autocommit = True  # Asegurar que vea los cambios más recientes
            cursor = conn.cursor(dictionary=dictionary)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()  # Cerrar conexión después de cada query
            
            return resultados
            
        except Error as e:
            print(f"Error ejecutando query: {e}")
            return []
    
    def ejecutar_comando(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Ejecuta un comando INSERT, UPDATE o DELETE
        
        Args:
            query: Comando SQL
            params: Parámetros del comando
            
        Returns:
            True si el comando fue exitoso
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            cursor.close()
            
            # Forzar refresco de la conexión para ver cambios inmediatamente
            conn.commit()
            
            return True
            
        except Error as e:
            print(f"Error ejecutando comando: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def ejecutar_muchos(self, query: str, params_list: List[tuple]) -> bool:
        """
        Ejecuta múltiples comandos con diferentes parámetros
        
        Args:
            query: Comando SQL
            params_list: Lista de tuplas con parámetros
            
        Returns:
            True si todos los comandos fueron exitosos
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(query, params_list)
            conn.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"Error ejecutando múltiples comandos: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def obtener_uno(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """
        Ejecuta una consulta y retorna un solo resultado
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            Diccionario con el resultado o None
        """
        resultados = self.ejecutar_query(query, params)
        return resultados[0] if resultados else None
    
    def existe(self, tabla: str, condicion: str, params: Optional[tuple] = None) -> bool:
        """
        Verifica si existe un registro en una tabla
        
        Args:
            tabla: Nombre de la tabla
            condicion: Condición WHERE
            params: Parámetros de la condición
            
        Returns:
            True si existe al menos un registro
        """
        query = f"SELECT COUNT(*) as total FROM {tabla} WHERE {condicion}"
        resultado = self.obtener_uno(query, params)
        return resultado and resultado['total'] > 0
    
    def contar(self, tabla: str, condicion: Optional[str] = None, 
            params: Optional[tuple] = None) -> int:
        """
        Cuenta registros en una tabla
        
        Args:
            tabla: Nombre de la tabla
            condicion: Condición WHERE opcional
            params: Parámetros de la condición
            
        Returns:
            Número de registros
        """
        query = f"SELECT COUNT(*) as total FROM {tabla}"
        if condicion:
            query += f" WHERE {condicion}"
        
        resultado = self.obtener_uno(query, params)
        return resultado['total'] if resultado else 0
    
    def insertar(self, tabla: str, datos: Dict) -> Optional[int]:
        """
        Inserta un registro en una tabla
        
        Args:
            tabla: Nombre de la tabla
            datos: Diccionario con los datos a insertar
            
        Returns:
            ID del registro insertado o None
        """
        columnas = ', '.join(datos.keys())
        placeholders = ', '.join(['%s'] * len(datos))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query, tuple(datos.values()))
            conn.commit()
            
            last_id = cursor.lastrowid
            cursor.close()
            
            return last_id
            
        except Error as e:
            print(f"Error insertando en {tabla}: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def actualizar(self, tabla: str, datos: Dict, condicion: str, 
            params_condicion: Optional[tuple] = None) -> bool:
        """
        Actualiza registros en una tabla
        
        Args:
            tabla: Nombre de la tabla
            datos: Diccionario con los datos a actualizar
            condicion: Condición WHERE
            params_condicion: Parámetros de la condición
            
        Returns:
            True si la actualización fue exitosa
        """
        set_clause = ', '.join([f"{k} = %s" for k in datos.keys()])
        query = f"UPDATE {tabla} SET {set_clause} WHERE {condicion}"
        
        params = list(datos.values())
        if params_condicion:
            params.extend(params_condicion)
        
        return self.ejecutar_comando(query, tuple(params))
    
    def eliminar(self, tabla: str, condicion: str, params: Optional[tuple] = None) -> bool:
        """
        Elimina registros de una tabla
        
        Args:
            tabla: Nombre de la tabla
            condicion: Condición WHERE
            params: Parámetros de la condición
            
        Returns:
            True si la eliminación fue exitosa
        """
        query = f"DELETE FROM {tabla} WHERE {condicion}"
        return self.ejecutar_comando(query, params)
    
    def iniciar_transaccion(self):
        """Inicia una transacción"""
        conn = self.get_connection()
        conn.start_transaction()
    
    def commit(self):
        """Confirma la transacción actual"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Revierte la transacción actual"""
        if self.connection:
            self.connection.rollback()
    
    def __enter__(self):
        """Soporte para context manager"""
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager"""
        self.desconectar()
