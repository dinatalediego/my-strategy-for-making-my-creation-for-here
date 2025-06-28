import os
import pandas as pd

# Carpeta donde están los archivos .xlsx
folder = 'outputs'

# Lista para acumular las últimas filas
last_rows = []

# Recorremos todos los archivos de la carpeta
for fname in os.listdir(folder):
    if fname.lower().endswith('.xlsx'):
        path = os.path.join(folder, fname)
        # Leemos el archivo (hoja por defecto)
        df = pd.read_excel(path)
        if not df.empty:
            # Tomamos la última fila y le añadimos una columna con el nombre original del archivo
            row = df.tail(1).copy()
            row['origen'] = fname
            last_rows.append(row)

# Si encontramos alguna fila, las concatenamos
if last_rows:
    result = pd.concat(last_rows, ignore_index=True)
    # Exportamos al Excel de salida
    result.to_excel('Direcciones Proyectos.xlsx', index=False)
    print(f"Generado 'resumen_últimas_filas.xlsx' con {len(result)} registros.")
else:
    print("No se encontraron filas para procesar.")
