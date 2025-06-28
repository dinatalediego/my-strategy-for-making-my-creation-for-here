import re
from bs4 import BeautifulSoup


def extraer_datos(soup: BeautifulSoup, tag: str, attrs: dict) -> list[str]:
    """Extrae texto de todas las etiquetas que coincidan con tag y attrs."""
    elementos = soup.find_all(tag, attrs=attrs)
    return [e.get_text(strip=True) for e in elementos if e]


def extraer_direccion(soup: BeautifulSoup) -> str | None:
    """Extrae la dirección limpia de <p class="direccion">. """
    p = soup.find('p', class_='direccion')
    if not p:
        return None

    # Eliminar iconos y enlaces hijos
    for tag in p.find_all(['i', 'a']):
        tag.decompose()

    direccion = p.get_text(strip=True)
    return direccion or None

def extraer_ultima_direccion(soup: BeautifulSoup) -> str | None:
    """
    Encuentra todas las <p class="direccion"> y retorna solo la última,
    sin iconos ni enlaces.
    """
    ps = soup.find_all('p', class_='direccion')
    if not ps:
        return None
    p = ps[-1]  # tomamos la última
    # eliminar iconos y enlaces
    for tag in p.find_all(['i', 'a']):
        tag.decompose()
    return p.get_text(strip=True) or None


def extraer_direccion_desde_snippet(texto: str) -> str | None:
    """
    Aísla el fragmento entre "Valor referencial" y "Ver mapa" y devuelve
    solo la calle + número (p.ej. 'AV. OSCAR R. BENAVIDES 3866').
    """
    m = re.search(r'Valor referencial.*?\$\s*[\d,\.]+(.+?)Ver mapa',
                  texto, flags=re.DOTALL)
    if not m:
        return None
    segmento = m.group(1)

    m2 = re.search(r'([A-Za-zÁÉÍÓÚÑ\.\s]+?\d+)', segmento)
    if m2:
        return m2.group(1).strip()

    return segmento.strip()