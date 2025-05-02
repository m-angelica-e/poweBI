import requests
import pandas as pd

def obtener_datos_desde_api():
    url = "https://www.datos.gov.co/resource/w9zh-vetq.json"
    response = requests.get(url)

    if response.status_code == 200:
        datos = response.json()
        df = pd.DataFrame(datos)
        return df
    else:
        raise Exception(f"Error al obtener datos: {response.status_code}")