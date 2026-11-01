# FIAshion — APIs Colombianas

API REST para la tienda virtual de FIAshion. Conserva el CRUD de productos y clientes, consulta departamentos/municipios mediante DIVIPOLA y complementa la ubicación de los clientes con códigos postales mediante API Colombia. No incluye integración de IA, DANE ni TerriData.

## Tecnologías
- Python, FastAPI y Pydantic
- SQLite y SQLAlchemy
- HTTPX para consumir APIs REST
- Circuit Breaker y Retry
- DuckDB permanece disponible para analítica local existente
- Pytest

## Fuentes externas
1. **DIVIPOLA — Datos Abiertos Colombia:** `https://www.datos.gov.co/resource/gdxc-w37w.json` para departamentos y municipios.
2. **API Colombia:** `https://api-colombia.com/api/v1` para consultar ciudades y sus códigos postales. No requiere clave API según su documentación pública.

Documentación de API Colombia: https://docs.api-colombia.com/

## Instalación en Windows
1. Descomprima el ZIP. La carpeta principal se llama `FIAshion APIs Colombianas` y contiene directamente `iniciar.bat`.
2. Abra esa carpeta en Visual Studio Code.
3. Ejecute ` .\iniciar.bat ` desde la terminal PowerShell. El script crea el entorno virtual, instala dependencias y arranca Uvicorn.
4. Abra Swagger en http://127.0.0.1:8000/docs.

## Endpoints principales
| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Estado de la API |
| POST/GET | `/api/v1/productos` | Registrar y listar productos |
| GET/PUT/DELETE | `/api/v1/productos/{producto_id}` | Consultar, actualizar y eliminar productos |
| POST/GET | `/api/v1/clientes` | Registrar y listar clientes |
| GET | `/api/v1/colombia/departamentos` | Consultar departamentos en DIVIPOLA |
| GET | `/api/v1/colombia/municipios?departamento=Cundinamarca` | Consultar municipios |
| GET | `/api/v1/colombia/codigos-postales?municipio=Chía&departamento=Cundinamarca` | Consultar códigos postales en API Colombia |

## Flujo de códigos postales
1. DIVIPOLA sigue siendo la fuente de departamentos y municipios.
2. Al conocer el municipio y departamento, el backend consulta `GET /City/name/{name}` en API Colombia para obtener el identificador de ciudad.
3. Con ese identificador consulta `GET /PostalCode/city/{cityId}`.
4. La respuesta entrega todos los códigos postales asociados a la ciudad, en una lista simplificada con código, zona, tipo, barrios y límites cuando la API los proporciona. Un municipio puede tener varios códigos; el sistema no asigna uno arbitrariamente. El usuario debe seleccionar el correspondiente a su barrio/dirección.
5. Al registrar al cliente, se puede enviar el código elegido en el campo opcional `codigo_postal`.

Ejemplo de consulta:
`GET /api/v1/colombia/codigos-postales?municipio=Chía&departamento=Cundinamarca` (devuelve `cantidad` y todos los elementos de `codigos_postales`).

Ejemplo de registro de cliente:
```json
{
  "nombre": "Ana",
  "departamento": "Cundinamarca",
  "municipio": "Chía",
  "codigo_postal": "250001"
}
```

## Compatibilidad de base de datos
Al iniciar, la aplicación agrega la columna opcional `codigo_postal` a la tabla `clientes` si la base SQLite existente todavía no la tiene. No elimina los registros existentes. Para conservar datos de una instalación anterior, copie su archivo `fiashion.db` a esta carpeta antes de iniciar el proyecto.

## Pruebas.
Desde la terminal, ejecute `pytest -q`. Las pruebas simulan las respuestas de API Colombia; no requieren conexión externa. La disponibilidad real de los servicios externos depende de la conexión a Internet y de los proveedores.
