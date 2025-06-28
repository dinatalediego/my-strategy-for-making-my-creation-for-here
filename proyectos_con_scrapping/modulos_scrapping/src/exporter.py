import os
from datetime import datetime

class ExcelExporter:
    """Clase para exportar DataFrames a Excel creando directorio si hace falta."""
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def exportar(self, df, nombre_file: str, proyecto: str):
        fecha = datetime.now().strftime("%d_%m_%Y")
        full_path = os.path.join(self.output_dir, f"{nombre_file}_{proyecto}_{fecha}.xlsx")
        df.to_excel(full_path, index=False)
        print(f"✅ Exportado a: {full_path}")