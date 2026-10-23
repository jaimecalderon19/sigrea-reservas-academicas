# Revisión de especificaciones

Fecha: 2026-10-23
Contra: `PLAN_INGENIERIA.md` y los cuatro cambios activos.
Resultado: no se implementa nada hasta cerrar los puntos de esta revisión. Las correcciones quedan en el mismo commit que este archivo.

## Correspondencia con el plan

| Decisión del plan | Dónde quedó | Veredicto |
| --- | --- | --- |
| Tres roles y registro público solo solicitante | `identidad-acceso` | Coincide |
| Administrador cambia rol y estado | `identidad-acceso` | Coincide |
| Catálogo con tres tipos, código único, baja lógica | `catalogo-espacios` | Coincide |
| Duración mínima de 30 minutos, sin máximo | `solicitud-reserva`, escenario de 08:00 a 18:00 | Coincide. El tope de horas no se cuela |
| Intervalo semiabierto | Solo en `design.md` de solicitud, no en el requisito | Ambiguo. Se corrige |
| Pendiente y aprobada ocupan cupo | El requisito de cruce nombra solo `aprobada` | Contradice el plan. Se corrige |
| Aprobar, rechazar, cancelar, historial | `ciclo-reserva` | Coincide, pero su escenario de liberación asume la corrección anterior |
| Stack y capas | `design.md` de cada cambio | No están en la spec. Correcto: no son comportamiento |

## Hallazgos

### 1. Contradicción: quién ocupa el cupo

`PLAN_INGENIERIA.md` dice que `pendiente` y `aprobada` ocupan, para que dos solicitudes no pasen sobre el mismo intervalo. El requisito "Cruce con reserva aprobada" solo rechaza el cruce con una aprobada. Con esa frase, dos pendientes del mismo intervalo serían válidas y el coordinador heredaría el conflicto del correo.

El escenario "El intervalo queda libre tras el rechazo" de `ciclo-reserva` no se puede probar en serio si la pendiente nunca ocupó el cupo: la segunda solicitud habría sido aceptada igual antes del rechazo.

Corrección: el requisito pasa a llamarse "Ocupación del intervalo". Ocupan `pendiente` y `aprobada`. Se agregan escenarios de cruce con pendiente, de intervalo contenido y de intervalo idéntico.

### 2. Ambigüedad: borde del intervalo

El plan fija `[inicio, fin)`. El borrador solo lo cuenta en un escenario de contigüidad, y solo contra una aprobada. Un solape de un segundo no tenía requisito.

Corrección: el requisito de ocupación dice que la comparación es semiabierta. El escenario contiguo se conserva. Se agrega un solape de un segundo, que debe rechazarse.

### 3. Ambigüedad: qué devuelve la disponibilidad

"Intervalos ocupados" no decía si una pendiente cuenta. Si la consulta ignorara las pendientes, el solicitante vería libre un cupo que la creación ya no puede tomar, o al revés, después de la corrección del punto 1.

Corrección: la consulta devuelve pendientes y aprobadas que se cruzan con el rango, y no devuelve rechazadas ni canceladas.

### 4. Hueco: límite de 500 caracteres

El requisito nombra el tope y no tiene escenario. Se agrega el rechazo de un propósito de 501 caracteres. 500 caracteres sigue siendo válido: el tope es cerrado.

### 5. Hueco: borde de los 30 minutos

"Al menos 30 minutos" rechaza 29 y no dice qué pasa con 30 exactos. Se agrega el escenario. 30 minutos se acepta.

### 6. Ambigüedad: quién crea una solicitud

El cuadro de actores del plan asigna la creación al solicitante. No se la da al coordinador ni al administrador. El borrador no lo cerraba.

Decisión de esta revisión: solo el solicitante crea solicitudes, siempre a su nombre. Un coordinador que necesite una sala usa una cuenta de solicitante. Queda anotado como límite, no como olvido de implementación. No se amplía el permiso en el código.

### 7. Hueco: último administrador

El diseño de identidad impide desactivar al único administrador activo. Esa frase no estaba en la spec. O se baja del diseño o se sube a requisito. Se sube. Si no, el código podría inventarla o saltársela sin que una prueba la exigiera.

### 8. Lo que no se cambia

- No se agrega duración máxima. El escenario de 08:00 a 18:00 sigue aceptado. Una regla de cuatro horas, si llega, será otro cambio.
- No se mueven decisiones de framework a la spec.
- Los cuatro cambios siguen separados. Implementar el ciclo antes de corregir la ocupación habría fijado el defecto en pruebas.

## Tareas

Quedan definidas en el `tasks.md` de cada cambio, después de estas correcciones. Ninguna tarea autoriza comportamiento que esta revisión haya dejado fuera.
