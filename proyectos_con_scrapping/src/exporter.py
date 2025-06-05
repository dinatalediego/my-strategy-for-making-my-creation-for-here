import os

class ExcelExporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # ✅ crea la carpeta si no existe

    def exportar(self, df, nombre_file, proyecto):
        from datetime import datetime

        fecha = datetime.now().strftime("%d_%m_%Y")
        full_path = os.path.join(self.output_dir, f"{nombre_file}_{proyecto}_{fecha}.xlsx")

        df.to_excel(full_path, index=False)
        print(f"✅ Exportado a: {full_path}")


""" import pandas as pd
from datetime import datetime
import os

class ExcelExporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def exportar(self, df, nombre_file, proyecto):
        fecha = datetime.now().strftime("%d_%m_%Y")
        full_path = os.path.join(self.output_dir, f"{nombre_file}_{fecha}.xlsx")
        df.to_excel(full_path, index=False)
        print(f"Exportado a: {full_path}")
 """