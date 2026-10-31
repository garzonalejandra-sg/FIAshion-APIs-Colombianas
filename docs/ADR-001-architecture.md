# ADR-001: Arquitectura y consulta de datos territoriales

- **Estado:** Aceptada
- **Fecha:** 2026-10-31

## Contexto
FIAshion es una API FastAPI para una tienda de ropa, respaldada por SQLite y SQLAlchemy. Se requiere conservar el catálogo y el registro de clientes, consultar divisiones territoriales colombianas y complementar la ubicación del cliente con códigos postales.

## Decisión
Se conserva FastAPI como adaptador HTTP y SQLite/SQLAlchemy como persistencia transaccional. DIVIPOLA, mediante el recurso Socrata de datos.gov.co, sigue siendo la fuente de departamentos y municipios. API Colombia se utiliza como segunda fuente REST para resolver la ciudad y consultar sus códigos postales: primero se consulta `/City/name/{name}` y después `/PostalCode/city/{cityId}`.

El código postal se almacena como dato opcional del cliente. Como una ciudad puede tener más de un código postal, la API devuelve la lista disponible y el usuario selecciona el que corresponde a su dirección o barrio. Circuit Breaker y Retry protegen las llamadas externas.

## Consecuencias
El catálogo de productos y el registro de clientes siguen funcionando aunque una fuente externa no esté disponible. La consulta de códigos postales es independiente del CRUD. Las bases SQLite existentes reciben una columna opcional `codigo_postal` mediante una migración no destructiva.

## Alternativas consideradas
- Reemplazar SQLite: rechazado para no arriesgar los registros existentes.
- Consultar servicios externos desde las rutas de productos: rechazado porque una falla externa no debe bloquear el catálogo.
- Asignar automáticamente un único código postal a todo un municipio: rechazado porque puede haber varias zonas postales por municipio.
