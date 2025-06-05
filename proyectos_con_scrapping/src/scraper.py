import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

def extraer_datos(soup, tag, attrs):
    elementos = soup.find_all(tag, attrs=attrs)
    return [e.text.strip() for e in elementos if e]
from bs4 import BeautifulSoup
import re

def extraer_direccion(soup):
    """
    Devuelve la dirección limpia extraída de <p class="direccion">.
    Ejemplos de salida:
      "Av. Venezuela 2305"
      "Av. Antonio José de Sucre 973"
    """
    p = soup.find('p', class_='direccion')
    if not p:
        return None

    # Quitar iconos y enlaces
    for tag in p.find_all(['i', 'a']):
        tag.decompose()

    # Ahora, p.text solo contiene la dirección
    direccion = p.get_text(strip=True)
    return direccion if direccion else None

import re

def extraer_direccion_desde_snippet(texto: str) -> str | None:
    """
    Busca en `texto` la sección que queda entre "Valor referencial" y "Ver mapa",
    luego limpia para devolver únicamente la calle + número.
    """
    # 1) Capturamos todo lo que haya tras el valor monetario hasta "Ver mapa"
    m = re.search(
        r'Valor referencial.*?\$\s*[\d,\.]+(.+?)Ver mapa',
        texto,
        flags=re.DOTALL
    )
    if not m:
        return None
    segmento = m.group(1)

    # 2) Aislamos calle + número (hasta el último dígito)
    m2 = re.search(r'([A-Za-zÁÉÍÓÚÑ\.\s]+?\d+)', segmento)
    if m2:
        return m2.group(1).strip()

    # 3) Fallback: devolver todo limpio de espacios
    return segmento.strip()


""" class ProyectoScraper:
    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup()

    def _get_soup(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        contenido = driver.page_source
        driver.quit()
        return BeautifulSoup(contenido, 'html.parser')

    def scrapear(self):
        titulo_sucio = extraer_datos(self.soup, "div", {"class": "caption"})
        direccion_sucio = extraer_datos(self.soup, "p", {"class": "Project-header-address"})
        #direccion_sucio = extraer_datos(self.soup, "div", {"class": "col-md-6 col-sm-6 col-xs-12"})
        #direccion_sucio = extraer_datos(self.soup, "div", {"class": "ficha_proyecto1"})
                

        df = pd.DataFrame({
            "TITULO": titulo_sucio,
            "DIRECCION": direccion_sucio * len(titulo_sucio)  # Repetir la dirección si es una sola
        })
        if len(direccion_sucio) == 1:
            direccion_sucio = direccion_sucio * len(titulo_sucio)
        elif len(direccion_sucio) != len(titulo_sucio):
            direccion_sucio = [None] * len(titulo_sucio)  # Default: si no coinciden, dejar vacío
        df = pd.DataFrame({
            "TITULO": titulo_sucio,
            "DIRECCION": direccion_sucio
        })
        
        df = self._limpiar_titulos(df)
        return df

    def _limpiar_titulos(self, df):
        def parsear(titulo):
            unidades = re.search(r'(\d+) unidad?', titulo)
            modelo = re.search(r'(\w+)\sPiso', titulo)
            dormitorios = re.search(r'(\d+) Dormitorios?', titulo)
            area = re.search(r'Área ([\d.]+)', titulo)
            precio = re.search(r'Precio desde S/ ([\d,]+)', titulo)

            return [
                int(unidades.group(1)) if unidades else None,
                modelo.group(1) if modelo else None,
                int(dormitorios.group(1)) if dormitorios else None,
                float(area.group(1)) if area else None,
                float(precio.group(1).replace(',', '')) if precio else None
            ]

        detalles = df["TITULO"].apply(parsear).tolist()
        detalles_df = pd.DataFrame(detalles, columns=["Unidades", "Modelo", "Dormitorios", "Area_m2", "Precio_Soles"])
        df_final = pd.concat([df, detalles_df], axis=1)
        return df_final.dropna(axis=0, how='all')
"""

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

class ProyectoScraper:
    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup()

    def _get_soup(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        html = driver.page_source
        driver.quit()
        return BeautifulSoup(html, 'html.parser')

    def scrapear(self):
        # 1. Extraer lista de títulos (puede ser más de uno)
        titulos = [t.strip() for t in self.soup.select("div.caption")]
        raw = self.soup.select_one("div.caption").get_text(" ", strip=True)
        
        # 2. Extraer UNA sola dirección
        #direccion = extraer_direccion(self.soup)
        direccion = extraer_direccion_desde_snippet(raw)

        # 3. Normalizar listas al mismo largo
        direcciones = ([direccion] * len(titulos)) if direccion else [None] * len(titulos)
        if len(direcciones) != len(titulos):
            direcciones = [None] * len(titulos)

        # 4. Crear DataFrame
        df = pd.DataFrame({
            "TITULO": titulos,
            "DIRECCION": direcciones
        })

        # 5. Aquí irían tus métodos de parseo de título
        df = self._limpiar_titulos(df)
        return df

    def _limpiar_titulos(self, df):
        def parsear(titulo):
            unidades = re.search(r'(\d+) unidad?', titulo)
            modelo = re.search(r'(\w+)\sPiso', titulo)
            dormitorios = re.search(r'(\d+) Dormitorios?', titulo)
            area = re.search(r'Área ([\d.]+)', titulo)
            precio = re.search(r'Precio desde S/ ([\d,]+)', titulo)

            return [
                int(unidades.group(1)) if unidades else None,
                modelo.group(1) if modelo else None,
                int(dormitorios.group(1)) if dormitorios else None,
                float(area.group(1)) if area else None,
                float(precio.group(1).replace(',', '')) if precio else None
            ]

        detalles = df["TITULO"].apply(parsear).tolist()
        detalles_df = pd.DataFrame(detalles, columns=["Unidades", "Modelo", "Dormitorios", "Area_m2", "Precio_Soles"])
        df_final = pd.concat([df, detalles_df], axis=1)
        return df_final.dropna(axis=0, how='all')