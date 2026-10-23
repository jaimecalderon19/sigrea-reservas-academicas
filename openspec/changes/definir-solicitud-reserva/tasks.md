# Tasks

## 1. Regla de ocupación

- [x] 1.1 Implementar la comparación semiabierta en el dominio, sin HTTP. Verificar con pruebas de dominio el solape, la contigüidad, el solape de un segundo y el otro espacio.

## 2. Solicitud y disponibilidad

- [x] 2.1 Implementar la creación solo para solicitante, con propósito, espacio activo, zona horaria y duración mínima de 30 minutos, sin duración máxima. Verificar el escenario de 08:00 a 18:00 y el de 501 caracteres.
- [x] 2.2 Rechazar el cruce con pendiente y con aprobada dentro de la transacción protegida por el cerrojo de proceso. Verificar los escenarios de solape parcial, intervalo idéntico y otro espacio.
- [x] 2.3 Implementar la consulta de disponibilidad con el mismo conjunto ocupado. Verificar que incluye pendiente y aprobada y omite una rechazada.
