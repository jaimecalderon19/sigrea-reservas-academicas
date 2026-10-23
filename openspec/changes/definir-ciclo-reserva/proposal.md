# Proposal

## Why

Crear la solicitud no cierra el proceso institucional. Alguien tiene que aprobar o rechazar, el solicitante tiene que poder cancelar, y la fila no puede desaparecer cuando la decisión ya se tomó.

## What Changes

- Aprobación y rechazo de una solicitud pendiente, con nota, por coordinador o administrador.
- Cancelación de una reserva pendiente o aprobada, por su solicitante o por coordinador y administrador.
- Historial consultable. El solicitante solo ve lo suyo. Coordinador y administrador ven todo.

## Capabilities

### New Capabilities

- `ciclo-reserva`: decisiones sobre una solicitud y consulta del historial, sin borrar registros.

### Modified Capabilities

- Ninguna. La liberación del cupo se observa desde esta capacidad, usando la regla de cruce de `solicitud-reserva`.

## Impact

- Cambia estados de reservas ya creadas. No cambia el catálogo ni los roles.
- Si la regla de cruce no trata `pendiente` como ocupación, el escenario de liberación queda mal planteado. La revisión de specs tiene que dejar eso consistente antes de implementar.
