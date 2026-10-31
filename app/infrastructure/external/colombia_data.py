import os
import unicodedata
from urllib.parse import quote

import httpx
from app.infrastructure.resilience.circuit_breaker import CircuitBreaker
from app.infrastructure.resilience.retry import retry


class ColombiaDataClient:
    """Consulta DIVIPOLA y códigos postales mediante API Colombia."""

    def __init__(self, timeout=20.0):
        self.timeout = timeout
        self.divipola_url = os.getenv(
            "DIVIPOLA_API_URL", "https://www.datos.gov.co/resource/gdxc-w37w.json"
        )
        self.api_colombia_url = os.getenv(
            "API_COLOMBIA_URL", "https://api-colombia.com/api/v1"
        ).rstrip("/")
        self.divipola_circuit = CircuitBreaker()
        self.postal_circuit = CircuitBreaker()

    @staticmethod
    def _get_json(url, params=None, timeout=20.0):
        return retry(lambda: httpx.get(url, params=params, timeout=timeout))

    def departamentos(self):
        response = self.divipola_circuit.call(
            lambda: self._get_json(self.divipola_url, {"$limit": 5000}, self.timeout)
        )
        return response.json()

    def municipios(self, departamento=None):
        params = {"$limit": 5000}
        if departamento:
            nombre = departamento.strip().upper().replace("'", "")
            params["$where"] = f"dpto='{nombre}'"
        response = self.divipola_circuit.call(
            lambda: self._get_json(self.divipola_url, params, self.timeout)
        )
        return response.json()

    @staticmethod
    def _normalizar(value):
        value = unicodedata.normalize("NFKD", str(value or ""))
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        return " ".join(value.casefold().strip().split())

    @staticmethod
    def _as_list(data):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Algunas respuestas paginadas encapsulan los registros en "data".
            for key in ("data", "items", "results"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
        return []

    @staticmethod
    def _as_list(data):
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Algunos endpoints entregan un objeto y otros una colección.
            for key in ("data", "items", "cities"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
        return []

    def _buscar_ciudades(self, municipio: str, departamento: str | None):
        """Busca ciudades evitando City/name, que puede responder HTTP 500."""
        wanted_city = self._normalizar(municipio)
        wanted_department = self._normalizar(departamento) if departamento else None
        candidates = []

        # Ruta preferida: departamento -> ciudades de ese departamento.
        if departamento:
            dep_name = quote(departamento.strip(), safe="")
            try:
                dep_response = self.postal_circuit.call(
                    lambda: self._get_json(
                        f"{self.api_colombia_url}/Department/name/{dep_name}",
                        timeout=self.timeout,
                    )
                )
                departments = self._as_list(dep_response.json())
                department_match = next((d for d in departments
                    if isinstance(d, dict) and self._normalizar(d.get("name")) == wanted_department), None)
                if department_match and department_match.get("id") is not None:
                    dep_id = department_match["id"]
                    cities_response = self.postal_circuit.call(
                        lambda: self._get_json(
                            f"{self.api_colombia_url}/Department/{dep_id}/cities",
                            timeout=self.timeout,
                        )
                    )
                    candidates = self._as_list(cities_response.json())
            except Exception:
                # Si falla esta ruta, se intenta la búsqueda general de ciudades.
                candidates = []

        # Alternativa documentada: búsqueda de ciudades por palabra clave.
        if not candidates:
            keyword = quote(municipio.strip(), safe="")
            search_response = self.postal_circuit.call(
                lambda: self._get_json(
                    f"{self.api_colombia_url}/City/search/{keyword}", timeout=self.timeout
                )
            )
            candidates = self._as_list(search_response.json())

        matches = []
        for city in candidates:
            if not isinstance(city, dict):
                continue
            city_name = city.get("name") or city.get("cityName") or ""
            dept = city.get("department") or {}
            dept_name = dept.get("name", "") if isinstance(dept, dict) else str(dept)
            if self._normalizar(city_name) != wanted_city:
                continue
            if wanted_department and dept_name and self._normalizar(dept_name) != wanted_department:
                continue
            matches.append(city)
        return matches

    def codigos_postales(self, municipio: str, departamento: str | None = None):
        """Busca el municipio y devuelve todos sus códigos postales documentados."""
        matching = self._buscar_ciudades(municipio, departamento)
        if not matching:
            raise ValueError(
                "API Colombia no encontró el municipio. Verifique el nombre y el departamento."
            )
        if len(matching) > 1:
            raise ValueError(
                "Hay varios municipios con ese nombre. Indique el departamento para desambiguar."
            )
        city = matching[0]
        city_id = city.get("id")
        if city_id is None:
            raise ValueError("API Colombia encontró la ciudad, pero no devolvió su identificador.")
        postal_response = self.postal_circuit.call(
            lambda: self._get_json(
                f"{self.api_colombia_url}/PostalCode/city/{city_id}", timeout=self.timeout
            )
        )
        postal_data = postal_response.json()
        if isinstance(postal_data, dict) and isinstance(postal_data.get("data"), list):
            postal_data = postal_data["data"]
        if not isinstance(postal_data, list):
            raise ValueError("La API de códigos postales devolvió un formato inesperado.")
        department_data = city.get("department") or {}
        return {
            "municipio": city.get("name", municipio),
            "departamento": department_data.get("name") if isinstance(department_data, dict) else (departamento or department_data),
            "city_id": city_id,
            "cantidad": len(postal_data),
            "codigos_postales": postal_data,
            "nota": "Un municipio puede tener varios códigos postales. Seleccione el que corresponda a la dirección o barrio del cliente.",
        }
