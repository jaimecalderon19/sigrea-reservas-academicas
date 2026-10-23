# Design

## Context

La spec vigente acepta 08:00 a 18:00. Este cambio la modifica. La arquitectura no se mueve: la regla entra en el dominio y la creación de solicitud la consulta dentro del mismo cerrojo que el cruce.

## Goals / Non-Goals

**Goals:**

- Máximo de cuatro horas en la solicitud aislada.
- Máximo de cuatro horas en el bloque continuo del mismo usuario y el mismo espacio.
- Cuatro horas exactas se aceptan. Un segundo de más, no.
- Hueco positivo, otro espacio, otro usuario, rechazada y cancelada quedan fuera del bloque.

**Non-Goals:**

- Tope diario del espacio. Otros usuarios pueden cubrir el día en bloques de cuatro horas.
- Impedir dos reservas separadas por un minuto, aunque sumen más de cuatro. La institución dijo consecutivas, no acumuladas en el día.
- Cambiar el predicado de cruce ni los roles.

## Decisions

- Consecutivo significa hueco cero: el fin de una es el inicio de la otra, o se solapan. Un segundo de separación corta el bloque. Alternativa descartada: sumar toda la duración del día del usuario. Eso prohibiría dos clases separadas y la regla no lo dice.
- El bloque se calcula solo con `pendiente` y `aprobada`. Alternativa descartada: contar también las canceladas. Una cancelación debe liberar, no castigar el siguiente pedido.
- Código de error `duracion_excedida`, distinto de `espacio_no_disponible`. El solicitante tiene que poder distinguir "lo tiene otro" de "usted ya encadenó cuatro horas".
- La comprobación vive en `dominio/tiempo.py` y se llama desde `crear_solicitud`, después del cruce y dentro del cerrojo. Así no se aprueba por la vía de creación un bloque que la spec rechaza.

## Risks / Trade-offs

- [La prueba de diez horas queda obsoleta] → se invierte en la implementación, en el mismo cambio que el código. No se toca el código en el commit de esta spec.
- [Dos reservas con un minuto de hueco eluden el espíritu de la regla] → se acepta. La spec nombra el hueco a propósito para que la prueba no dependa de una interpretación tácita.
