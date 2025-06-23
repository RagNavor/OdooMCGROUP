import re
from odoo import http
from odoo.http import request
import requests
import logging
_logger = logging.getLogger(__name__)


class AcademicProxyController(http.Controller):
    POWERBI_BASE_URL = "https://app.powerbi.com"
    POWERBI_VIEW_URL = "https://app.powerbi.com/view?r=eyJrIjoiODE2MWFlM2MtODhkNC00NmNlLTg4ZjktYmUxYTI0NTE1NjZmIiwidCI6IjBiMTgwYjAyLTIzMTUtNDBjMS05ZWIxLTY0MDk4N2FmNDRkYyIsImMiOjl9"
    ODOC_DOMAIN = 'localhost'
    @http.route('/academic_management/dashboard_proxy', type='http', auth='user', website=False)
    def dashboard_proxy(self, **kw):
        """
        Actúa como proxy para cargar el contenido de un dashboard externo (ej. Power BI).
        La URL real se mantiene en el servidor de Odoo.
        """
        # La URL del dashboard de Power BI o cualquier otra URL pública que quieras embeber.
        # ¡IMPORTANTE!: Reemplaza esta URL con tu enlace público real.
        _logger.warning(f"estoy recibiendo: {request}")
        

        headers_to_send = {
            key: value
            for key, value in request.httprequest.headers.items()
            if key.lower() not in ['host', 'origin', 'content-length', 'connection'] # Evitar cabeceras problemáticas
        }
        if 'Content-Type' in request.httprequest.headers:
            headers_to_send['Content-Type'] = request.httprequest.headers['Content-Type']

        try:
            method = request.httprequest.method
            response = None

            if method == 'GET':
                # Realiza la solicitud GET para obtener el HTML inicial
                response = requests.get(self.POWERBI_VIEW_URL, verify=True, headers=headers_to_send)

            elif method == 'POST':
                # Realiza la solicitud POST reenviando los datos del cuerpo
                response = requests.post(self.POWERBI_BASE_URL, verify=True, headers=headers_to_send, data=request.httprequest.get_data())

            

            else:
                _logger.warning(f"Controlador: Método HTTP no soportado en dashboard_proxy: {method}")
                return request.not_found() # O un 405 Method Not Allowed

            # Si llegamos aquí, hemos hecho una solicitud GET/POST
            

            # Reenviar las cabeceras de la respuesta externa al cliente (CRÍTICO para MIME y CORS)
            headers_to_forward_to_client = []
            for header_name, header_value in response.headers.items():
                # Evita cabeceras que pueden causar errores o son manejadas por Odoo/requests
                if header_name.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                    if header_name.lower() == 'set-cookie':
                        modified_cookie_value = header_value

                        modified_cookie_value = re.sub(r';\s*Domain=[^;]+', '', modified_cookie_value, flags=re.IGNORECASE)
                    
                        # 2. Añadir el nuevo Domain, que es el dominio de tu Odoo.
                        # El navegador ahora "creerá" que la cookie es para tu sitio.
                        modified_cookie_value = f"{modified_cookie_value}; Domain={self.ODOC_DOMAIN}"
                        
                        # 1. Eliminar cualquier atributo SameSite existente (ya sea Lax, Strict o None)
                        modified_cookie_value = re.sub(r';\s*SameSite=[^;]+', '', modified_cookie_value, flags=re.IGNORECASE)
                        
                        # 2. Asegurar que 'Secure' esté presente. Si ya está, no hace nada. Si no, lo añade.
                        # Esto es un requisito para SameSite=None.
                        if '; Secure' not in modified_cookie_value and ';secure' not in modified_cookie_value:
                            modified_cookie_value = f"{modified_cookie_value}; Secure"
                            
                        # 3. Añadir SameSite=None.
                        # Esto es lo que permite que la cookie sea enviada en un contexto de terceros (iframe).
                        modified_cookie_value = f"{modified_cookie_value}; SameSite=None"
                        
                        _logger.info(f"Cookie original: '{header_value}' de Power BI. Cookie modificada (SameSite=None; Secure forzado): '{modified_cookie_value}'")
                        headers_to_forward_to_client.append((header_name, modified_cookie_value))
                    else:
                        headers_to_forward_to_client.append((header_name, header_value))

            # Añadir cabeceras CORS de vuelta al cliente si son necesarias para el iframe
            if 'Access-Control-Allow-Origin' not in response.headers:
                headers_to_forward_to_client.append(('Access-Control-Allow-Origin', request.httprequest.headers.get('Origin', '*')))
            if 'Access-Control-Allow-Credentials' not in response.headers:
                headers_to_forward_to_client.append(('Access-Control-Allow-Credentials', 'true')) # Si PowerBI usa credenciales/cookies

            _logger.info(f"Controlador: Solicitud '{method}' a {self.POWERBI_VIEW_URL} proxied exitosamente con Content-Type: {response.headers.get('Content-Type')}")
            return request.make_response(response.content, headers=headers_to_forward_to_client)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error al proxy del dashboard externo para '{method}' request: %s", e)
            return request.render('academic_management.dashboard_proxy_error_template', {
                'error_message': f"No se pudo cargar el dashboard externo para la solicitud '{method}'.",
                'details': str(e)
            })



        
    @http.route('/<path:resource_path>', type='http', auth='user', website=False)
    def dashboard_resource_proxy(self, resource_path, **kw):
        """
        Proxy para cualquier recurso solicitado por el HTML de Power BI que
        se intente cargar desde el dominio de Odoo (ej. /scripts/hash-manifest.js).
        """
        # Filtra solo las rutas que potencialmente son de Power BI.
        # Esto es CRÍTICO para no proxear todo el tráfico de Odoo.
        # La ruta problemática que viste es "/13.0.26140.37/scripts/hash-manifest.js"
        # Así que podrías buscar un prefijo como "13.0.26140.37"
        # O, si Power BI es más consistente, podrías buscar "/scripts/" o "/styles/"
        # O el patrón '/<version>/<type>/<filename>'
        # Hay que ser MUY específico aquí para no atrapar rutas legítimas de Odoo.

        # Ejemplo muy específico basado en tu error:
        _logger.info(f"Solicitud a {resource_path} recibida en dashboard_resource_proxy")
        if not resource_path.startswith('13.0.26140.37/') and \
           not resource_path.startswith('scripts/') and \
           not resource_path.startswith('styles/') and \
           not resource_path.startswith('images/'): # Puedes añadir más prefijos de recursos de Power BI
           # Si la ruta no coincide con los patrones de recursos de Power BI,
           # Odoo debería intentar procesarla con sus propios controladores web estándar.
           # Sin embargo, en un controlador catch-all como este, si no lo proxy,
           # podría dar un 404. Es mejor ser explícito.
           # Para este ejemplo, si no es PowerBI, dejamos que Odoo maneje el 404 estándar.
           _logger.debug(f"Controlador: No es un recurso de Power BI, ignorando: /{resource_path}")
           return request.not_found() # Devuelve un 404 si no es un recurso de PowerBI.

        full_external_url = f"{self.POWERBI_BASE_URL}/{resource_path}"
        _logger.info(f"Controlador: Proxear recurso: {full_external_url}")

        try:
            # Reenviar headers del navegador si es necesario, pero Content-Type es el más importante
            # También podrías pasar request.httprequest.headers si quieres reenviar todas las cabeceras
            response = requests.get(full_external_url, verify=True, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            # Extraer y reenviar las cabeceras HTTP originales, especialmente Content-Type
            headers_to_forward = []
            for header_name, header_value in response.headers.items():
                # Es CRÍTICO reenviar Content-Type.
                # Evita cabeceras que pueden causar errores o son manejadas por Odoo.
                if header_name.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'set-cookie', 'connection']:
                    headers_to_forward.append((header_name, header_value))

            _logger.info(f"Controlador: Recurso {resource_path} proxied exitosamente con Content-Type: {response.headers.get('Content-Type')}")
            return request.make_response(response.content, headers=headers_to_forward)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error al proxear el recurso {full_external_url}: {e}")
            return request.not_found() # O devolver una imagen/JS de error si quieres algo más amigable