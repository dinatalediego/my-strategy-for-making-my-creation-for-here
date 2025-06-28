import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from src.utils import extraer_datos, extraer_ultima_direccion


class ProyectoScraper:
    """Clase OOP para scrapear un solo proyecto inmobiliario."""
    def __init__(self, url: str):
        self.url = url
        self.soup = self._get_soup()

    def _get_soup(self) -> BeautifulSoup:
        driver = webdriver.Chrome()
        driver.get(self.url)
        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, 'html.parser')

    def scrapear(self) -> pd.DataFrame:
        # Extraer lista de títulos
        titulos = extraer_datos(self.soup, 'div', {'class': 'caption'})
        # Extraer única dirección
        direccion = extraer_ultima_direccion(self.soup)
        direcciones = ([direccion] * len(titulos)) if direccion else [None] * len(titulos)

        df = pd.DataFrame({'TITULO': titulos, 'DIRECCION': direcciones})
        return self._limpiar_titulos(df)

    def _limpiar_titulos(self, df: pd.DataFrame) -> pd.DataFrame:
        import re
        detalles = []
        for titulo in df['TITULO']:
            u = re.search(r'(\d+) unidad?', titulo)
            m = re.search(r'(\w+)\sPiso', titulo)
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

            d = re.search(r'(\d+) Dormitorios?', titulo)
            a = re.search(r'Área ([\d.]+)', titulo)
            p = re.search(r'Precio desde S/ ([\d,]+)', titulo)
            detalles.append({
                'Unidades': int(u.group(1)) if u else None,
                'Modelo': m.group(1) if m else None,
                'Dormitorios': int(d.group(1)) if d else None,
                'Area_m2': float(a.group(1)) if a else None,
                'Precio_Soles': float(p.group(1).replace(',', '')) if p else None,
                'Piso mínimo':piso_desde, 
                'Piso máximo':piso_hasta,
                'Rango de Pisos':total_pisos
            })
        return pd.concat([df.reset_index(drop=True), pd.DataFrame(detalles)], axis=1)