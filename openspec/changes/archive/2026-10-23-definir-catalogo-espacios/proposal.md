# Proposal

## Why

Una reserva sin un espacio identificable vuelve a la ambigüedad del correo: "el laboratorio" no dice cuál. El plan pide un catálogo con tipo, capacidad y baja lógica.

## What Changes

- Alta, consulta y actualización de espacios por el administrador.
- Tipos cerrados: laboratorio, auditorio, sala de cómputo.
- Código único, capacidad positiva y baja lógica sin borrar historial futuro.

## Capabilities

### New Capabilities

- `catalogo-espacios`: inventario de espacios académicos y quién puede modificarlo.

### Modified Capabilities

- Ninguna.

## Impact

- Depende de `identidad-acceso` para saber quién escribe.
- No decide todavía si un espacio inactivo acepta reservas. Eso queda en la capacidad de solicitud, que debe leer el estado que este catálogo guarda.
