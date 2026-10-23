# Design

## Context

Ver `PLAN_INGENIERIA.md`, módulo de catálogo. Depende de la sesión definida en `definir-identidad-acceso`.

## Goals / Non-Goals

**Goals:**

- Tipos cerrados: `laboratorio`, `auditorio`, `sala_computo`.
- Código único, capacidad entera mayor que cero, nombre y ubicación obligatorios.
- Baja lógica. No hay borrado físico.

**Non-Goals:**

- Fotos, inventario de equipos, sedes múltiples.
- Decidir aquí si un inactivo acepta reservas. La spec de solicitud lo prohíbe. Este diseño solo persiste `activo`.

## Decisions

- El código se guarda tal como lo envía el administrador, sin convertirlo en clave primaria. La clave es un identificador numérico. Así un código puede corregirse sin romper reservas futuras.
- Códigos de error: `codigo_duplicado`, `datos_invalidos`, `no_encontrado`, `prohibido`, `no_autenticado`.
- Listar devuelve activos e inactivos. Ocultar los inactivos escondería la baja lógica que el administrador acaba de hacer.

## Risks / Trade-offs

- [El solicitante ve espacios inactivos] → puede intentar reservarlos. La spec de solicitud debe rechazar ese caso. Si esa spec no se implementa, el catálogo solo no basta. La tarea de solicitud cubre el rechazo.
