import re
from bs4 import BeautifulSoup


def extraer_datos(soup: BeautifulSoup, tag: str, attrs: dict) -> list[str]:
    """Extrae texto limpio de todas las etiquetas que coincidan."""
    return [e.get_text(strip=True) for e in soup.find_all(tag, attrs=attrs) if e]


def extraer_ultima_direccion(soup: BeautifulSoup) -> str | None:
    """Toma la última <p class='direccion'>, elimina hijos no deseados y retorna texto limpio."""
    ps = soup.find_all('p', class_='direccion')
    if not ps:
        return None
    p = ps[-1]
    for t in p.find_all(['i', 'a']):
        t.decompose()
    return p.get_text(strip=True) or None