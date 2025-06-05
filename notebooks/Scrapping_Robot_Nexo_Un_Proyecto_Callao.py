from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pandas as pd
import re

# 1. Función para extraer datos genéricos desde etiquetas HTML
def extraer_datos(soup, tag, attrs):
    """
    Extrae el texto de todas las etiquetas HTML coincidentes con el tag y los atributos dados.

    Parameters:
    soup (bs4.BeautifulSoup): Objeto BeautifulSoup del contenido HTML.
    tag (str): El nombre de la etiqueta HTML que deseas buscar.
    attrs (dict): Un diccionario de atributos para identificar las etiquetas.

    Returns:
    list: Lista con los textos extraídos.
    """
    elementos = soup.find_all(tag, attrs=attrs)
    return [elemento.text.strip() if elemento else None for elemento in elementos]

# 2. Función para normalizar nombres de columnas
def normalizar_nombres_columnas(df):
    """
    Normaliza los nombres de las columnas del DataFrame, convirtiéndolos a mayúsculas.
    """
    df.columns = df.columns.str.upper()
    return df

# 3. Función para Encontrar caracteres: Funcion genérica para adaptarla
def buscar_numero_en(df, col_donde_sebusca, antes_de=None, despues_de=None):
    """
    Busca un número en la columna `col_metraje` de un DataFrame, especificando un patrón antes y/o después del número.
    
    Parameters:
    df (pd.DataFrame): El DataFrame donde se realiza la búsqueda.
    col_metraje (str): El nombre de la columna donde buscar el patrón.
    antes_de (str): El patrón que aparece antes del número (opcional).
    despues_de (str): El patrón que aparece después del número (opcional).
    
    Returns:
    pd.Series: Serie con los números encontrados.
    """
    
    # Crear la expresión regular
    # Si no se especifica "antes_de", solo busca basado en "despues_de"
    # Si no se especifica "despues_de", solo busca basado en "antes_de"
    if antes_de and despues_de:
        regex = rf'{re.escape(despues_de)}\s*(\d+)\s*{re.escape(antes_de)}'
    elif despues_de:
        regex = rf'{re.escape(despues_de)}\s*(\d+)'
    elif antes_de:
        regex = rf'(\d+)\s*{re.escape(antes_de)}'
    else:
        raise ValueError("Debes especificar al menos 'antes_de' o 'despues_de'.")
    
    # Aplicar la búsqueda de la expresión regular en la columna especificada
    return df[col_donde_sebusca].apply(lambda x: re.search(regex, x).group(1) if re.search(regex, x) else None)

# 4. Función para buscar un número entre patrones opcionales
def buscar_numero_en_precio(df, col_donde_sebusca, antes_de=None, despues_de=None):
    """
    Busca un número en la columna `col_metraje` de un DataFrame, especificando un patrón antes y/o después del número.
    Convierte números con separadores de miles (e.g., "125,500") en enteros (125500).
    
    Parameters:
    df (pd.DataFrame): El DataFrame donde se realiza la búsqueda.
    col_metraje (str): El nombre de la columna donde buscar el patrón.
    antes_de (str): El patrón que aparece antes del número (opcional).
    despues_de (str): El patrón que aparece después del número (opcional).
    
    Returns:
    pd.Series: Serie con los números encontrados.
    """
    
    # Crear la expresión regular para encontrar el número, considerando los patrones antes y/o después
    if antes_de and despues_de:
        regex = rf'{re.escape(despues_de)}\s*(\d{{1,3}}(?:,\d{{3}})*)\s*{re.escape(antes_de)}'
    elif despues_de:
        regex = rf'{re.escape(despues_de)}\s*(\d{{1,3}}(?:,\d{{3}})*)'
    elif antes_de:
        regex = rf'(\d{{1,3}}(?:,\d{{3}})*)\s*{re.escape(antes_de)}'
    else:
        raise ValueError("Debes especificar al menos 'antes_de' o 'despues_de'.")

    # Aplicar la expresión regular y limpiar el número
    return df[col_donde_sebusca].apply(lambda x: int(re.sub(r',', '', re.search(regex, x).group(1))) if re.search(regex, x) else None)


# 5. Función para limpiar precios y extraer monedas
def limpiar_precio(df, col_precio='PRECIO_DESDE'):
    """
    Limpia la columna de precios, detectando la moneda (Soles o Dólares) y extrayendo los valores numéricos.
    """
    df['Precio'] = df[col_precio].astype(str)
    df['Moneda_soles'] = df['Precio'].apply(lambda x: "Soles" if 'S/' in x else None)
    df['Moneda_dolares'] = df['Precio'].apply(lambda x: "Dólares" if 'USD' in x else None)
    
    #df['Precio_soles'] = df['Precio'].apply(lambda x: re.findall(r'\d+', x)[0] if 'S/' in x else None)
    df['Precio_soles'] = df.apply(lambda x: re.findall(r'\d+', x['Precio'])[0] if x['Moneda_soles'] else None, axis=1)

    #df['Precio_dolares'] = df['Precio'].apply(lambda x: re.findall(r'\d+', x)[0] if 'USD' in x else None)
    df['Precio_dolares'] = buscar_numero_en_precio(df, col_donde_sebusca = col_precio, despues_de='USD')
    
    # Convertir a tipo numérico
    df['Precio_soles'] = pd.to_numeric(df['Precio_soles'], errors='coerce')*1000.0
    df['Precio_dolares'] = pd.to_numeric(df['Precio_dolares'], errors='coerce')
    
    # Eliminar cualquier columna adicional si es necesario
    if 'Precio' in df.columns:
        df.drop(columns=['Precio'], inplace=True)
    
    return df

# 6. Función para limpiar ubicación
def limpiar_ubicacion(df, col_ubicacion='UBICACION', distritos=None):
    """
    Limpia la columna de ubicación eliminando distritos no deseados y caracteres especiales.
    """
    if distritos is None:
        distritos = ['Callao','CALLAO','callao', 'San Miguel','san miguel', 'Lima', 'Peru', 'Perú', 'SAN MIGUEL', 'LIMA', 'PERU']
    
    def limpiar_calle(ubicacion, distritos):
        for distrito in distritos:
            ubicacion = re.sub(rf'\b{distrito}\b', '', ubicacion) # Usamos \b para asegurarnos de que elimine el distrito cuando sea una palabra completa
            ubicacion = re.sub(distrito, '', ubicacion) # Eliminamos los casos donde el distrito pueda estar pegado a otras palabras
        
        ubicacion = re.sub(r'[.,;:!?\s]+$', '', ubicacion).strip()  # Eliminar cualquier signo de puntuación al final de la cadena
        ubicacion = re.sub(r'\s+', ' ', ubicacion).strip() # Eliminar espacios extras
        return ubicacion if ubicacion else None

    df['Calle'] = df[col_ubicacion].apply(lambda x: limpiar_calle(x, distritos) if isinstance(x, str) else None)
    return df

# 7. Función para extraer metraje y características adicionales
def extraer_metraje(df, col_metraje='METRAJE'):
    """
    Extrae información de metraje, unidades y dormitorios de la columna metraje.
    """
    """ df['Metraje'] = df[col_metraje].apply(lambda x: re.search(r'\d+ m²', x).group() if isinstance(x, str) else None)
    df['Dormitorios'] = df[col_metraje].apply(lambda x: re.search(r'\d+ dorm.', x).group() if isinstance(x, str) else None)
    return df """
    # Usando la función genérica para extraer diferentes valores
    df['Unidades'] = buscar_numero_en(df, col_metraje, antes_de='un.')
    df['Dormitorios'] = buscar_numero_en(df, col_metraje, antes_de='dorm.')
    df['Metraje_desde'] = buscar_numero_en(df, col_metraje, antes_de='a', despues_de='dorm.')
    df['Metraje_hasta'] = buscar_numero_en(df, col_metraje, antes_de='m²')
    df['Baños'] = buscar_numero_en(df, col_metraje, antes_de='baño')
    df['Estacionamientos'] = buscar_numero_en(df, col_metraje, antes_de='esta')
    
    # Convertir los resultados a numéricos donde sea necesario
    df['Unidades'] = pd.to_numeric(df['Unidades'], errors='coerce')
    df['Dormitorios'] = pd.to_numeric(df['Dormitorios'], errors='coerce')
    df['Metraje_desde'] = pd.to_numeric(df['Metraje_desde'], errors='coerce')
    df['Metraje_hasta'] = pd.to_numeric(df['Metraje_hasta'], errors='coerce')
    df['Baños'] = pd.to_numeric(df['Baños'], errors='coerce')
    df['Estacionamientos'] = pd.to_numeric(df['Estacionamientos'], errors='coerce')

    print(df.info())
    return df

# 8. Función para Cálculos de S/ o $ por m2
def añadir_calculos(df):
    df['Precio por m2 soles ref desde'] = round(df['Precio_soles']/df['Metraje_hasta'],0)
    df['Precio por m2 soles ref hasta'] = round(df['Precio_soles']/df['Metraje_desde'],0)
    
    if df['Precio_dolares'] is not None:
        df['Precio por m2 dol ref desde'] = round(df['Precio_dolares']/df['Metraje_hasta'],0)
        df['Precio por m2 dol ref hasta'] = round(df['Precio_dolares']/df['Metraje_desde'],0)
    
    return df    

# 9. Función para exportar a Excel
def exportar_excel(df, nombre_file, proyecto):
    DATA_ANALYTICS = "C:/Users/diego.dinatale/OneDrive - Aenza/LOCAL_MACHINE/DATA_ANALYTICS/"
    #BDVIVA = "C:/Users/diego.dinatale/OneDrive - Aenza/LOCAL_MACHINE/DATA_ANALYTICS/BD VIVA/ESTUDIOS DE PROYECTOS/BUSINESS INTELLIGENCE CON SCRAPPING/SCRAPPING DE PDMAR/BD de Internet Jugadores/"
    nombre_file = nombre_file + " "+ proyecto
    ubicacion_final_baseglobal = DATA_ANALYTICS + "BD VIVA/DATA DEL MERCADO CON SCRAPPING/CALLAO/" + nombre_file + ".xlsx"
    ubicacion_final_carpeta_proyecto = DATA_ANALYTICS + "ESTUDIOS DE PROYECTOS/BUSINESS INTELLIGENCE CON SCRAPPING/SCRAPPING DE COMAS/BD de Internet Jugadores/" + nombre_file + ".xlsx"
    #DATA DEL MERCADO CON SCRAPPING
    print(f"Exportando archivo a: {ubicacion_final_baseglobal}")
    df.to_excel(ubicacion_final_baseglobal, index=False)
    print(f"Exportando archivo a: {ubicacion_final_carpeta_proyecto}")
    df.to_excel(ubicacion_final_carpeta_proyecto, index=False)
    print("Archivo exportado exitosamente.")


# 8. Función principal de scraping y creación del DataFrame
def scraping_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    
    contenido = driver.page_source
    soup = bs(contenido, 'html.parser')
    driver.quit() # Cerrar navegador
    
    # Extraer datos usando las funciones genéricas
    titulo_sucio = extraer_datos(soup, "div", {"class": "caption"}) # 1
    
    # Crear el DataFrame
    data = {
        "TITULO": titulo_sucio
    }
    df = pd.DataFrame(data)

    # Limpiar y procesar los datos
    df = normalizar_nombres_columnas(df)
    return df

# Ejecutar la función principal con la URL deseada

# NEXO INMOBILIARIA
#url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2411-terrazas-de-bellavista-bellavista-callao-callao-nadlan"
#url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2411-terrazas-de-bellavista-bellavista-callao-callao-nadlan"

#
url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2659-alto-bellavista-bellavista-callao-callao-imagina"

#url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-3621-pazea-bellavista-callao-callao-cosapi"
#url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-3621-pazea-bellavista-callao-callao-cosapi"
""" url = ""
url = ""
url = ""
url = ""
url = ""
url = ""
 """

df = scraping_selenium(url)

# Actualización de la función para manejar los dos patrones adicionales
def limpiar_titulo_actualizado(titulo):
        # Buscar número de unidades disponibles
        #unidades = re.search(r'(\d+) unidades?', titulo)
        unidades = re.search(r'(\d+) unidad?', titulo)
        unidades_disponibles = int(unidades.group(1)) if unidades else None
        
        # Buscar el modelo (secuencia de palabras hasta 'Piso')
        modelo = re.search(r'(\w+)\sPiso', titulo)
        modelo_nombre = modelo.group(1) if modelo else None

        # Caso 1: Patrón "Entre X al Y"
        # entre_pisos = re.search(r'Entre (\d+) al (\d+)', titulo)
        entre_pisos = re.search(r'Entre\s*(\d+)\s*al\s*(\d+)', titulo)
        if entre_pisos:
            piso_desde = int(entre_pisos.group(1))
            piso_hasta = int(entre_pisos.group(2))
            total_pisos = piso_hasta - piso_desde + 1
        else:
            # Caso 2: Patrón "Piso X, Y, Z"
            pisos_comas = re.findall(r'Piso (\d+(?:, \d+)*)', titulo)
            if pisos_comas:
                pisos = [int(piso) for piso in pisos_comas[0].split(', ')]
                piso_desde = min(pisos)
                piso_hasta = max(pisos)
                total_pisos = len(pisos)
            else:
                piso_desde, piso_hasta, total_pisos = None, None, None

        # Buscar dormitorios
        dormitorios = re.search(r'(\d+) Dormitorios?', titulo)
        dormitorios_num = int(dormitorios.group(1)) if dormitorios else None
        
        # Buscar área
        area = re.search(r'Área ([\d.]+)', titulo)
        area_m2 = float(area.group(1)) if area else None
        
        # Buscar precio
        precio = re.search(r'Precio desde S/ ([\d,]+)', titulo)
        precio_soles = float(precio.group(1).replace(',', '')) if precio else None
        
        return [unidades_disponibles, modelo_nombre, piso_desde, piso_hasta, total_pisos, dormitorios_num, area_m2, precio_soles]

    # Aplicar la función actualizada

df_comas_cleaned_actualizado = df['TITULO'].apply(limpiar_titulo_actualizado)
df_comas_cleaned_actualizado = pd.DataFrame(df_comas_cleaned_actualizado.tolist(), columns=[
    'Unidades_Disponibles', 'Modelo', 'Piso_Desde', 'Piso_Hasta', 'Total_Pisos', 'Dormitorios', 'Area_m2', 'Precio_Desde_Soles'
])

df_comas_cleaned_actualizado = df_comas_cleaned_actualizado.dropna(axis=0, how='all')

# Imagina
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Alto Bellavista_23.01")
exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Alto Bellavista_26_05_25")

# Cosapi
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Pazea")
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Pazea_26_05_25")

#
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Terrazas de Bellavista")

#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Terrazas de Bellavista")
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Alto Bellavista_23.01")


# Mostrar el DataFrame resultante
print(df.head())