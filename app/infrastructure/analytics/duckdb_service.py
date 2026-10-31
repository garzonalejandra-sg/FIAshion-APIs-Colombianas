import duckdb
import unicodedata

class AnalyticsService:
    """Analítica aislada de la base transaccional: usa una conexión DuckDB en memoria."""
    def __init__(self):
        self.connection = duckdb.connect(database=":memory:")
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS poblacion(
                departamento VARCHAR, poblacion BIGINT, anio INTEGER
            )
        """)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS clientes(
                departamento VARCHAR, total BIGINT
            )
        """)

    @staticmethod
    def _normalizar_departamento(value):
        value = unicodedata.normalize("NFKD", str(value or ""))
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        return " ".join(value.upper().strip().split())

    def cargar_poblacion(self, rows):
        self.connection.execute("DELETE FROM poblacion")
        for row in rows:
            departamento = row.get("departamento") or row.get("Departamento") or row.get("nom_depto")
            value = row.get("poblacion") or row.get("Poblacion") or row.get("POBLACION")
            year = row.get("anio") or row.get("Año") or row.get("ANO") or 0
            if departamento and value is not None:
                try:
                    nombre = self._normalizar_departamento(departamento)
                    population = int(float(str(value).replace(" ", "").replace(",", ".")))
                    if nombre and population >= 0:
                        self.connection.execute("INSERT INTO poblacion VALUES (?, ?, ?)",
                            [nombre, population, int(year)])
                except (ValueError, TypeError):
                    continue

    def cargar_clientes(self, rows):
        self.connection.execute("DELETE FROM clientes")
        for departamento, total in rows:
            nombre = self._normalizar_departamento(departamento)
            self.connection.execute("""
                INSERT INTO clientes VALUES (?, ?)
                ON CONFLICT DO NOTHING
            """, [nombre, total])

    def poblacion_por_departamento(self):
        # La fuente demográfica puede contener indicadores de varios años. No se deben sumar registros de años
        # diferentes; el análisis utiliza el último año disponible en la fuente.
        return self.connection.execute("""
            WITH ultimo AS (SELECT MAX(anio) AS anio FROM poblacion)
            SELECT p.departamento, SUM(p.poblacion) AS poblacion, p.anio
            FROM poblacion p CROSS JOIN ultimo u
            WHERE p.anio = u.anio
            GROUP BY p.departamento, p.anio
            ORDER BY poblacion DESC
        """).fetchdf().to_dict(orient="records")

    def clientes_vs_poblacion(self):
        return self.connection.execute("""
            WITH ultimo AS (SELECT MAX(anio) AS anio FROM poblacion),
            poblacion_actual AS (
                SELECT p.departamento, SUM(p.poblacion) AS poblacion, p.anio
                FROM poblacion p CROSS JOIN ultimo u
                WHERE p.anio = u.anio
                GROUP BY p.departamento, p.anio
            )
            SELECT p.departamento, p.poblacion, p.anio,
                   COALESCE(c.total, 0) AS clientes,
                   ROUND(100.0 * COALESCE(c.total, 0) / NULLIF(p.poblacion, 0), 4) AS porcentaje
            FROM poblacion_actual p
            LEFT JOIN clientes c USING(departamento)
            ORDER BY clientes DESC
        """).fetchdf().to_dict(orient="records")
