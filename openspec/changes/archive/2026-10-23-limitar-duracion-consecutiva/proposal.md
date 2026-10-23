# Proposal

## Why

La institución agrega una regla después de cerrada la primera versión: ningún usuario puede reservar un espacio durante más de cuatro horas consecutivas. El plan la había dejado fuera a propósito. Meterla en el código sin actualizar la spec rompería el escenario que hoy acepta una jornada de 08:00 a 18:00.

## What Changes

- Una solicitud de más de cuatro horas se rechaza. Cuatro horas exactas siguen siendo válidas.
- El mismo usuario no puede encadenar reservas vigentes del mismo espacio, sin hueco entre ellas, hasta pasar de cuatro horas.
- Un hueco, otro espacio u otro usuario no se suman a ese bloque.
- Rechazadas y canceladas no alargan el bloque.
- **BREAKING** respecto del escenario "Duración de varias horas": 08:00 a 18:00 deja de aceptarse.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `solicitud-reserva`: el intervalo válido gana un máximo de cuatro horas, y se agrega el bloque consecutivo del mismo usuario en el mismo espacio.

## Impact

- Afecta el plan: la frase "sin duración máxima" queda sustituida. La adenda de `PLAN_INGENIERIA.md` lo registra. No cambia arquitectura, stack ni la regla de cruce.
- La prueba que acepta diez horas tiene que invertirse en la implementación, no antes. El resto de la suite debe seguir en verde.
- No cambia aprobación, catálogo ni roles, salvo que una solicitud que antes nacía pendiente ahora ni siquiera se crea.
