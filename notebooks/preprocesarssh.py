import pandas as pd
import re
import requests
import json
import os
import sys
from sqlalchemy import create_engine
import time 

GEOLOCALIZACION_PATH = '../data/geolocalizacion.json'
DB_ENGINE = "mysql+mysqlconnector://admin:admin@localhost:3306/logs"
CHUNKSIZE = 50000  

def procesar_csv(ruta):
    ids_existentes = cargar_ids_existentes()

    if os.path.isfile(ruta) and ruta.endswith(".csv"):
        archivos = [ruta]
    elif os.path.isdir(ruta):
        archivos = [os.path.join(ruta, f) for f in os.listdir(ruta) if f.endswith(".csv")]
    else:
        print(f"Ruta no válida o no es un archivo CSV: {ruta}")
        return

    for archivo in archivos:
        print(f"Procesando archivo: {archivo}")
        df_ids = pd.read_csv(archivo, sep=";", encoding="utf-8", usecols=["ID"])
        ids_csv = set(df_ids["ID"].dropna().astype(str))
        duplicados = ids_csv.intersection(ids_existentes)
        if duplicados:
            print(f"Archivo {archivo} ya fue procesado previamente (IDs duplicados detectados). Se cancela el procesamiento.")
            continue

        chunk_iter = pd.read_csv(archivo, sep=";", encoding="utf-8", chunksize=CHUNKSIZE)
        for chunk in chunk_iter:
            chunk["Evento"] = chunk["Descripción"].apply(categorizar_evento)
            df_extra = chunk.apply(extraer_columnas, axis=1, result_type='expand')
            chunk = pd.concat([chunk, df_extra], axis=1)
            chunk = geolocalizar_ips(chunk)
            chunk = transformar_datos(chunk)
            guardar_datos(chunk)
        ids_existentes.update(ids_csv)  

    print("Todos los datos nuevos guardados correctamente.")

def cargar_ids_existentes():
    engine = create_engine(DB_ENGINE)
    try:
        df_existente = pd.read_sql("SELECT ID FROM logs", con=engine)
        return set(df_existente["ID"].dropna().astype(str))
    except Exception as e:
        print(f"Error al cargar IDs existentes de la base de datos: {e}")
        return set()


def guardar_datos(df_nuevo):
    engine = create_engine(DB_ENGINE)
    try:
        df_nuevo.to_sql(name="logs", con=engine, if_exists="append", index=False, chunksize=CHUNKSIZE)
        print(f"Insertadas {len(df_nuevo)} filas en la base de datos")
    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")

def categorizar_evento(descripcion):
    mapeo_eventos = {
        '(Sesiones': lambda x: "CONEXION" if re.search(r'\bconectada\b', x.lower()) else "DESCONEXION",
        'Aceptar': "ACEPTAR_PRIVACIDAD",
        'Añadida': "AÑADIR_PIEZA",
        'Borrado': "BORRAR_DISEÑO",
        'Cambio': "CAMBIO_CONTRASEÑA",
        'Cargado': "CARGAR_DISENO",
        'Creado': "CREAR_DISENO",
        'Cuenta': "CUENTA",
        'Duración': "DURACION",
        'Error': "ERROR_SISTEMA",
        'Generar': lambda x: "GEN_PRESUPUESTO" if re.search(r'\bpresupuesto\b', x.lower()) else "GEN_PEDIDO",
        'Intento': "INTENTO_RESET",
        'Limpiar': "LIMPIAR_DATOS",
        'Login': "LOGIN",
        'Logout': "LOGOUT",
        'Nuevo': "NUEVO_LOGO",
        'Solicitud': "SOLICITUD_RESET",
        'Visualizar': lambda x: "VER_PRESUPUESTO" if re.search(r'\bpresupuesto\b', x.lower()) else "VER_PEDIDO",
    }
    descripcion = str(descripcion)
    primera_palabra = descripcion.split()[0]
    if primera_palabra in mapeo_eventos:
        if callable(mapeo_eventos[primera_palabra]):
            return mapeo_eventos[primera_palabra](descripcion)
        else:
            return mapeo_eventos[primera_palabra]
    else:
        return "OTRO"

def extraer_columnas(row):
    evento = row['Evento']
    desc = row['Descripción']
    if pd.isna(desc):
        return {}
    if evento == 'AÑADIR_PIEZA':
        catalogo_completo = buscar(r'catálogo (.*?) en el diseño', desc)
        if catalogo_completo and ' - ' in catalogo_completo:
            fabricante, catalogo = catalogo_completo.split(' - ', 1)
        else:
            fabricante, catalogo = None, catalogo_completo
        return {
            'pieza': buscar(r'pieza ([\w-]+)', desc),
            'piezaid': buscar(r'id (\d+)', desc),
            'fabricante': fabricante,
            'catalogo': catalogo,
            'diseñoid': buscar(r'diseño con id: (-?\d+)', desc)
        }
    elif evento in ['LOGIN', 'LOGOUT', 'SOLICITUD_RESET', 'ACEPTAR_PRIVACIDAD', 'CAMBIO_CONTRASEÑA']:
        return {'userid': buscar(r'userID: (\w+)', desc)}
    elif evento == 'GEN_PEDIDO':
        return {
            'diseñoid': buscar(r'diseño con id: (-?\d+)', desc),
            'fabricante': buscar(r'fabricante (.*)', desc)
        }
    elif evento in ['CREAR_DISENO', 'CARGAR_DISENO', 'GEN_PRESUPUESTO', 'VER_PRESUPUESTO', 'ERROR_SISTEMA', 'BORRAR_DISEÑO', 'VER_PEDIDO']:
        return {'diseñoid': buscar(r'diseño con id: (-?\d+)', desc)}
    elif evento == 'INTENTO_RESET':
        return {'email': buscar(r'email[:\s]+(\S+)', desc)}
    elif evento == 'DURACION':
        return {'minutos': buscar(r'Duración de la sesión:\s*([\d.]+)', desc)}
    elif evento == 'NUEVO_LOGO':
        return {'logo': buscar(r'logo[:\s]+(\w+)', desc)}
    elif evento in ['CONEXION', 'DESCONEXION']:
        return {'nsesiones': buscar(r'activas (\d+)', desc)}
    return {}

def buscar(patron, texto):
    match = re.search(patron, texto)
    return match.group(1) if match else None

def geolocalizar_ips(df):
    if os.path.exists(GEOLOCALIZACION_PATH) and os.path.getsize(GEOLOCALIZACION_PATH) > 0:
        with open(GEOLOCALIZACION_PATH, 'r') as f:
            geolocalizacion = json.load(f)
    else:
        geolocalizacion = {}
    ips = df['IP'].unique()
    for ip in ips:
        if ip not in geolocalizacion:
            geolocalizacion[ip] = geolocalizar(ip)
    with open(GEOLOCALIZACION_PATH, 'w') as f:
        json.dump(geolocalizacion, f)
    df['city'] = df['IP'].map(lambda ip: geolocalizacion.get(ip, {}).get('city'))
    df['region'] = df['IP'].map(lambda ip: geolocalizacion.get(ip, {}).get('region'))
    df['country'] = df['IP'].map(lambda ip: geolocalizacion.get(ip, {}).get('country'))
    df['lat'] = df['IP'].map(lambda ip: geolocalizacion.get(ip, {}).get('lat'))
    df['lng'] = df['IP'].map(lambda ip: geolocalizacion.get(ip, {}).get('lng'))
    return df

def geolocalizar(ip):
    url = f'https://ipinfo.io/{ip}?token=aff46df76e5e05'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        lat_str, lng_str = data['loc'].split(',')
        lat, lng = float(lat_str), float(lng_str)
        return {
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'lat': lat,
            'lng': lng
        }
    except Exception as e:
        print(f'Error con la IP: {ip}')
        return {'city': None, 'region': None, 'country': None, 'lat': None, 'lng': None}

def transformar_datos(df):
    df['Usuario'] = df['Usuario'].str.replace(r'^#\d+\s*-\s*', '', regex=True)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y/%m/%d %H:%M:%S', errors='coerce')
    df['Hora'] = df['Fecha'].dt.hour
    df['NombreDia'] = df['Fecha'].dt.day_name()
    df = df.sort_values('Fecha').reset_index(drop=True)

    tipos = {
        'Evento': 'string',
        'nsesiones': 'Int64',
        'pieza': 'string',
        'fabricante': 'string',
        'catalogo': 'string',
        'minutos': 'float32',
        'logo': 'string',
        'email': 'string',
        'city': 'category',
        'region': 'category',
        'country': 'category',
        'lat': 'float32',
        'lng': 'float32'
    }
    for col, tipo in tipos.items():
        if col in df.columns:
            df[col] = df[col].astype(tipo)
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python preprocesarssh.py <ruta_csv1> <ruta_csv2> ... o <ruta_carpeta>")
        sys.exit(1)
    rutas = sys.argv[1:]
    for ruta in rutas:
        procesar_csv(ruta)