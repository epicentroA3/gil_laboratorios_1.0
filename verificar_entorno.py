def verificar_python():
    import sys
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Necesita 3.8+")
        return False

def verificar_pip():
    try:
        import pip
        print(f"✅ pip disponible - OK")
        return True
    except ImportError:
        print("❌ pip no encontrado")
        return False

def verificar_mysql():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        conn.close()
        print("✅ MySQL conexión exitosa - OK")
        return True
    except ImportError:
        print("❌ mysql-connector-python no instalado (se instalará después)")
        return True  # No es crítico en esta etapa
    except Exception as e:
        print(f"❌ MySQL no accesible: {e}")
        return False

def main():
    print("🔍 VERIFICANDO ENTORNO PARA SISTEMA DE LABORATORIOS")
    print("=" * 60)
    
    resultados = []
    resultados.append(verificar_python())
    resultados.append(verificar_pip())
    resultados.append(verificar_mysql())
    
    print("\n" + "=" * 60)
    if all(resultados):
        print("✅ ENTORNO LISTO PARA CONTINUAR")
        print("Siguiente paso: Instalar dependencias de Python")
    else:
        print("❌ RESOLVER PROBLEMAS ANTES DE CONTINUAR")
    print("=" * 60)

if __name__ == "__main__":
    main()