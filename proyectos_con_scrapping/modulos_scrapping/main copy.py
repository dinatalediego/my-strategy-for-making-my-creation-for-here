import pandas as pd
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
    main()