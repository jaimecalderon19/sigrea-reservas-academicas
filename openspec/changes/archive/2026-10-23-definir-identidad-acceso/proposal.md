# Proposal

## Why

Sin usuarios y roles no hay quien solicite ni quien decida, y cualquiera podría aprobar una reserva. El plan de ingeniería cierra tres roles y un registro público limitado a solicitante. Esta capacidad vuelve observable esa decisión.

## What Changes

- Registro público que solo crea cuentas con rol solicitante.
- Ingreso con sesión revocable y rechazo de cuenta inactiva o clave incorrecta.
- Administración de rol y de estado activo, reservada al administrador.
- Correo único, comparado sin distinguir mayúsculas.

## Capabilities

### New Capabilities

- `identidad-acceso`: registro, sesión, roles y administración de cuentas.

### Modified Capabilities

- Ninguna. No hay specs previas.

## Impact

- Módulo de identidad. Las demás capacidades dependen de una sesión válida y de un rol.
- No agrega reservas ni espacios. No cambia la arquitectura del plan.
