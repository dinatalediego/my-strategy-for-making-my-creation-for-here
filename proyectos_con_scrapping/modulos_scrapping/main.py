import pandas as pd
# Klaus tiene que crear
# "AGENTE" "ROBOT DE COCINA" - LAVA, FUNCION: ProyectoScraper

from src.scraper import ProyectoScraper
# "AGENTE" "ROBOT DE COCINA" - CORTA LAS PAPAS
from src.exporter import ExcelExporter


def main():
    # 1. Leer Excel con proyectos
    df_proyectos = pd.read_excel('inputs/proyectos.xlsx', sheet_name=0)
    # Espera columnas: 'nombre_file' y 'url'

    # 2. Crear exportador
    exporter = ExcelExporter(output_dir='outputs')

    # 3. Iterar cada fila de proyectos
    for _, row in df_proyectos.iterrows():
        nombre = str(row['proyecto']).strip()
        url = str(row['url']).strip()

        # Scraping
        scraper = ProyectoScraper(url)
        df = scraper.scrapear()

        # Agregar fila de ubicación al final, columna A
        if 'DIRECCION' in df.columns and not df['DIRECCION'].isnull().all():
            dir_ultima = df['DIRECCION'].iloc[-1]
            df = df.drop(columns=['DIRECCION'])
            fila_ubi = {df.columns[0]: dir_ultima}
            df = pd.concat([df, pd.DataFrame([fila_ubi])], ignore_index=True)

        # Exportar
        exporter.exportar(df, nombre_file=nombre, proyecto=nombre)


if __name__ == '__main__':
    main()
    
""" import pandas as pd
from src.scraper import ProyectoScraper
from src.exporter import ExcelExporter


def main():
    # 1. URL del proyecto a scrapear
    #url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-3621-pazea-bellavista-callao-callao-cosapi"
    url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2888-duetto-846-fase-ii-cercado-de-lima-lima-lima-cantabria"
    
    # 2. Scraping
    scraper = ProyectoScraper(url)
    df = scraper.scrapear()

    # 3. Agregar fila de ubicación en la última fila, columna A
    if 'DIRECCION' in df.columns and not df['DIRECCION'].isnull().all():
        #direccion = df['DIRECCION'].iloc[0]
        direccion = df['DIRECCION'].iloc[-1]
        # Eliminar columna 'DIRECCION' para no duplicar en el cuerpo de la tabla
        df = df.drop(columns=['DIRECCION'])
        # Crear un DataFrame con la fila de ubicación solo en la primera columna
        fila_ubicacion = {df.columns[0]: direccion}
        df = pd.concat([df, pd.DataFrame([fila_ubicacion])], ignore_index=True)

    # 4. Exportar resultados a Excel
    exporter = ExcelExporter(output_dir="outputs")
    
    #exporter.exportar(df, nombre_file="Callao_Proyecto", proyecto="Pazea")
    exporter.exportar(df, nombre_file="Callao_Proyecto", proyecto="Duetto 846 Fase II")
    
    print("✅ Datos exportados exitosamente a Excel en la carpeta 'outputs'.")

if __name__ == "__main__":
    main() """