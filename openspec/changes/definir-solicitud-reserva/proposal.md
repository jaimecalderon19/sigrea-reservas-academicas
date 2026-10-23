# Proposal

## Why

El daño concreto del proceso actual es aceptar dos usos del mismo espacio en el mismo intervalo. Esta capacidad crea la solicitud y la consulta de disponibilidad con un solo criterio de cruce.

## What Changes

- Un solicitante autenticado crea una solicitud a su nombre, en estado pendiente.
- Se rechazan intervalos inválidos, propósito vacío, espacio inexistente o inactivo, y duración menor a 30 minutos.
- Se rechaza el cruce con una reserva pendiente o aprobada del mismo espacio. El intervalo es semiabierto.
- La consulta de disponibilidad muestra pendientes y aprobadas del rango pedido, no rechazadas ni canceladas.
- Solo un solicitante crea solicitudes, a su propio nombre.

## Capabilities

### New Capabilities

- `solicitud-reserva`: creación de la solicitud, validación del intervalo y consulta de disponibilidad.

### Modified Capabilities

- Ninguna.

## Impact

- Depende de identidad y de catálogo.
- No incluye aprobar, rechazar ni cancelar. Eso es `definir-ciclo-reserva`.
- No limita la duración máxima. El plan lo deja fuera de la primera versión.
