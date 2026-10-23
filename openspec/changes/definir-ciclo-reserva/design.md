# Design

## Context

Ver `PLAN_INGENIERIA.md`, ciclo de vida. Esta capacidad no crea la regla de cruce. La usa. La nota de revisión es obligatoria para que el historial explique la decisión, no solo el estado.

## Goals / Non-Goals

**Goals:**

- Transiciones: `pendiente` a `aprobada`, `pendiente` a `rechazada`, `pendiente` o `aprobada` a `cancelada`.
- Toda transición guarda actor y momento. Aprobación y rechazo exigen nota. La cancelación admite nota vacía.
- El listado es el historial. No hay una tabla paralela de auditoría en esta versión.

**Non-Goals:**

- Borrar reservas.
- Reabrir una rechazada o una cancelada.
- Notificar por correo.

## Decisions

- Aprobar vuelve a evaluar el cruce dentro de la misma transacción. Si otra reserva vigente se cruzara, la aprobación se rechaza con `espacio_no_disponible` y el estado no cambia. Con la regla corregida (pendiente ocupa) ese caso no debería ocurrir por la vía normal. Se mantiene como defensa.
- Cancelar una aprobada la saca del conjunto que ocupa cupo. La consulta de disponibilidad deja de devolver ese intervalo.
- Códigos: `prohibido`, `estado_invalido`, `no_encontrado`, `datos_invalidos`, `espacio_no_disponible`.
- El solicitante que pide una reserva por id ajeno recibe `prohibido`, no `no_encontrado`, para no usar el historial como oráculo de existencia más allá de lo que ya puede listar. Coordinador y administrador sí reciben `no_encontrado` si el id no existe.

## Risks / Trade-offs

- [El escenario de liberación exigía que la pendiente ocupara el cupo] → la revisión del 2026-10-23 ya corrigió `solicitud-reserva`. Este cambio se implementa después de esa corrección, no contra el borrador.
