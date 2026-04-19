import os
import requests

BASE_URL = "https://apim.bccr.fi.cr/SDDE/api/Bccr.GE.SDDE.Publico.Indicadores.API"

class BCCRAPIError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

def get_headers():
    token = os.getenv("BCCR_TOKEN") 
    if not token or token.strip() == "":
        raise ValueError("Falta el Token: El token BCCR_TOKEN no está configurado o está vacío en el archivo .env.")
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/json, */*"
    }

def _make_request(url, params=None, stream=False):
    """
    Realiza la solicitud HTTP GET a la API, retornando JSON o contenido binario (archivo).
    """
    try:
        headers = get_headers()
        response = requests.get(url, headers=headers, params=params, stream=stream)
        
        if response.status_code == 200:
            # Verifica si la respuesta es un archivo Excel o genérico binario
            content_type = response.headers.get("Content-Type", "")
            if stream or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type or "application/octet-stream" in content_type:
                 return {"is_file": True, "content": response.content}
            
            return {"is_file": False, "data": response.json()}
        
        # Manejo de errores de la API (400, 401, 404, 500)
        error_msg = f"API Error {response.status_code}: "
        try:
            error_data = response.json()
            if "mensaje" in error_data:
                error_msg += str(error_data["mensaje"])
            elif "message" in error_data: # Por si viene en inglés
                error_msg += str(error_data["message"])
            else:
                error_msg += str(error_data)
        except ValueError:
            error_msg += response.text if response.text else "Sin detalles provistos por la API."
            
        raise BCCRAPIError(error_msg, status_code=response.status_code)
        
    except requests.exceptions.RequestException as e:
        raise BCCRAPIError(f"Error de conexión a la API: {str(e)}")

# ==========================================
# Endpoints de Cuadros
# ==========================================

def descargar_cuadros(idioma="ES"):
    url = f"{BASE_URL}/cuadro/descargar"
    return _make_request(url, params={"idioma": idioma}, stream=True)

def metadata_cuadro(codigo, idioma="ES"):
    url = f"{BASE_URL}/cuadro/{codigo}/metadata"
    return _make_request(url, params={"idioma": idioma})

def series_cuadro(codigo, fecha_inicio, fecha_fin, idioma="ES"):
    url = f"{BASE_URL}/cuadro/{codigo}/series"
    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "idioma": idioma
    }
    return _make_request(url, params=params)

# ==========================================
# Endpoints de Indicadores Económicos
# ==========================================

def descargar_indicadores(idioma="ES"):
    url = f"{BASE_URL}/indicadoresEconomicos/descargar"
    return _make_request(url, params={"idioma": idioma}, stream=True)

def metadata_indicador(codigo, idioma="ES"):
    url = f"{BASE_URL}/indicadoresEconomicos/{codigo}/metadata"
    return _make_request(url, params={"idioma": idioma})

def series_indicador(codigo, fecha_inicio, fecha_fin, idioma="ES"):
    url = f"{BASE_URL}/indicadoresEconomicos/{codigo}/series"
    params = {
        "fechaInicio": fecha_inicio,
        "fechaFin": fecha_fin,
        "idioma": idioma
    }
    return _make_request(url, params=params)
