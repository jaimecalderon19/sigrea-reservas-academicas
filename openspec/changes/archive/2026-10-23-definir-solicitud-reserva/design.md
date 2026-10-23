# Design

## Context

Ver `PLAN_INGENIERIA.md`, secciones 2 y 3. La invariante de cruce es el motivo del sistema. Esta capacidad la especifica antes de programarla.

## Goals / Non-Goals

**Goals:**

- Estado inicial `pendiente`.
- Intervalo semiabierto en la comparación: `inicio < fin_ajena` y `fin > inicio_ajena`.
- Duración mínima de 30 minutos. Sin máximo.
- La misma regla alimenta la creación y la consulta de disponibilidad.

**Non-Goals:**

- Aprobar, rechazar, cancelar.
- Tope de cuatro horas. Fuera de alcance del plan. No se implementa en este cambio.
- Reservas recurrentes.

## Decisions

- El solicitante de la fila es siempre el de la sesión. El cuerpo no acepta un `solicitante_id` ajeno. Alternativa descartada: permitir que un coordinador cree a nombre de otro. No está en el plan y abre un permiso que no se ha especificado.
- Comparación en UTC después de exigir offset. `-05:00` y `Z` del mismo instante son el mismo punto.
- Códigos: `espacio_no_disponible`, `espacio_inactivo`, `no_encontrado`, `datos_invalidos`, `no_autenticado`.
- La escritura de la solicitud toma un cerrojo de proceso, relee las reservas vigentes del espacio y solo entonces inserta. Alternativa descartada: confiar en un `UNIQUE`, que no expresa solape.

## Risks / Trade-offs

- [SQLite no excluye rangos entre procesos] → limitación ya aceptada en el plan. Un solo proceso.
- [El borrador solo nombraba reservas aprobadas] → la revisión del 2026-10-23 lo corrigió: pendiente y aprobada ocupan, comparación semiabierta. Se implementa la spec corregida, no el borrador.
