from src.scraper import ProyectoScraper
from src.exporter import ExcelExporter

# URL del proyecto
url = "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-3621-pazea-bellavista-callao-callao-cosapi"

# Scraping
scraper = ProyectoScraper(url)
df_resultado = scraper.scrapear()

# Exportación
exportador = ExcelExporter(output_dir="outputs")
exportador.exportar(df_resultado, nombre_file="Callao_Proyecto", proyecto="Pazea")
#exportar_excel(df_comas_cleaned_actualizado, nombre_file="Callao Proyecto", proyecto = "Pazea")