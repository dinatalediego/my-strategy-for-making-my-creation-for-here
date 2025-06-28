import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup

from src.utils import extraer_datos, extraer_ultima_direccion


class ProyectoScraper:
    """Clase para scrapear proyectos inmobiliarios."""
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
        # 1) Extraer títulos (pueden haber varios)
        titulos = extraer_datos(self.soup, "div", {"class": "caption"})

        # 2) Extraer solo la última dirección válida
        direccion = extraer_ultima_direccion(self.soup)
        direcciones = ([direccion] * len(titulos)) if direccion else [None] * len(titulos)

        # 3) Construir DataFrame inicial
        df = pd.DataFrame({
            "TITULO": titulos,
            "DIRECCION": direcciones
        })

        # 4) Parsear TITULO en columnas adicionales
        df = self._limpiar_titulos(df)
        return df

    def _limpiar_titulos(self, df: pd.DataFrame) -> pd.DataFrame:
        import re
        detalles = []
        for titulo in df["TITULO"]:
            unidades    = re.search(r'(\d+) unidad?', titulo)
            modelo      = re.search(r'(\w+)\sPiso', titulo)
            dormitorios = re.search(r'(\d+) Dormitorios?', titulo)
            area        = re.search(r'Área ([\d.]+)', titulo)
            precio      = re.search(r'Precio desde S/ ([\d,]+)', titulo)

            detalles.append({
                "Unidades":     int(unidades.group(1))    if unidades    else None,
                "Modelo":       modelo.group(1)            if modelo      else None,
                "Dormitorios":  int(dormitorios.group(1)) if dormitorios else None,
                "Area_m2":      float(area.group(1))       if area        else None,
                "Precio_Soles": float(precio.group(1).replace(',', '')) if precio else None,
            })

        detalles_df = pd.DataFrame(detalles)
        return pd.concat([df.reset_index(drop=True), detalles_df], axis=1)