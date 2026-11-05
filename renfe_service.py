import requests
from bs4 import BeautifulSoup
import json
import re

def obtener_incidencias_renfe(linea_buscada=None):
    """
    Conecta en tiempo real con las fuentes de datos de Renfe y Adif.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    incidencias = []

    # 1. Intentar obtener avisos activos del endpoint JSON oficial de Renfe Cercanías
    try:
        url_renfe = "https://www.renfe.com/content/dam/renfe/es/General/json/avisos_cercanias_madrid.json"
        resp = requests.get(url_renfe, headers=headers, timeout=8)
        if resp.status_code == 200:
            datos = resp.json()
            for aviso in datos.get("avisos", []):
                titulo = aviso.get("titulo", "")
                cuerpo = aviso.get("texto", "")
                incidencias.append(f"📌 *{titulo}*\n{cuerpo}")
    except Exception as e:
        print(f"Error consultando JSON Renfe: {e}")

    # 2. Si no hay avisos en el JSON, consultar la web de incidencias de Adif mediante scraping
    if not incidencias:
        try:
            url_adif = "https://www.adif.es/es/estado-de-la-red/incidencias"
            resp = requests.get(url_adif, headers=headers, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                bloques = soup.find_all(['div', 'article', 'p'], class_=re.compile(r'incidencia|aviso|alerta', re.I))
                for b in bloques:
                    texto = b.get_text(strip=True)
                    if "Cercanías" in texto or "Madrid" in texto or "C-" in texto:
                        incidencias.append(texto)
        except Exception as e:
            print(f"Error consultando Adif: {e}")

    # 3. Filtrar por línea si se solicita una específica (ej: C5)
    if linea_buscada and incidencias:
        linea_upper = linea_buscada.upper()
        filtradas = [inc for inc in incidencias if linea_upper in inc.upper()]
        if filtradas:
            return True, f"🚨 *INCIDENCIAS EN LÍNEA {linea_upper}*\n\n" + "\n\n---\n\n".join(filtradas)
        else:
            return False, f"✅ *Línea {linea_upper}:* Sin incidencias ni demoras registradas en este momento."

    # 4. Si hay incidencias generales en la red
    if incidencias:
        resumen = "\n\n---\n\n".join(incidencias[:5])
        return True, f"🚨 *ESTADO GLOBAL CERCANÍAS MADRID*\n\n{resumen}"

    return False, "✅ *Cercanías Madrid:* Circulación con normalidad en toda la red."