# Informe final

SIGREA, gestión de reservas de espacios académicos.
Fecha de cierre: 2026-10-23.

## Resultado

El sistema corre como API HTTP sobre un monolito modular y SQLite. Cubre catálogo, usuarios y roles, solicitud, disponibilidad, cruce, aprobación, rechazo, cancelación, historial y el tope de cuatro horas consecutivas.

`pytest` cierra en 79 pruebas, todas en verde al archivar el último cambio. No hay una prueba suelta de "el sistema funciona": cada escenario de `openspec/specs/` tiene un caso que fallaría si se quitara la regla.

El historial de Git conserva el orden que pedía la actividad:

1. `bfa9f7f` plan de ingeniería, sin OpenSpec y sin código.
2. `b8fe41d` inicialización de OpenSpec.
3. `b33af7d` especificaciones.
4. `c47ccaf` revisión y corrección, y recién ahí las tareas.
5. `0969fca`, `a4a7ed5`, `7be967e`, `34af7fe` implementación por capacidad.
6. `52c00fe` spec del tope de cuatro horas, sin tocar código.
7. `3781be9` implementación de ese tope.
8. Archivos OpenSpec en `33f1677` y `8b49813`.

## Dificultades

La primera no fue de código. El borrador de `solicitud-reserva` solo rechazaba el cruce con una reserva aprobada. El plan ya había decidido que `pendiente` también ocupa, para que dos solicitudes no pasen sobre el mismo hueco. Si se hubiera programado el borrador, las pruebas del ciclo (liberar el cupo al rechazar) habrían quedado mal planteadas: la segunda solicitud habría entrado igual antes del rechazo. Se corrigió en `c47ccaf`, antes de la primera línea de reservas.

La segunda fue de formato, no de negocio. OpenSpec no deja que un requisito `MODIFIED` borre un escenario existente. El escenario "Duración de varias horas" no se podía sustituir por otro título. Se conservó el nombre y se cambió el resultado: 08:00 a 18:00 ahora se rechaza. Eso obligó a leer la spec vigente en vez de reescribirla de memoria.

La tercera es de alcance del enunciado. "Más de cuatro horas consecutivas" no dice si un minuto de separación corta la racha, ni si cuenta otro espacio, ni si una rechazada suma. Dejarlo implícito habría hecho que la prueba dependiera del humor de quien implementa. Se cerró en la spec: hueco cero, mismo usuario, mismo espacio, solo vigentes. Cuatro horas exactas pasan. Un segundo más, no.

SQLite no expresa un solape con `UNIQUE`. El cruce se relee dentro de un cerrojo de proceso. Sirve para un solo proceso, que es el despliegue de esta entrega. No sirve si mañana hay dos procesos escribiendo. Eso ya estaba aceptado en el plan. No se simuló PostgreSQL para fingir que el riesgo desapareció.

## Decisiones que cambiaron

| Decisión inicial | Qué pasó | Dónde quedó |
| --- | --- | --- |
| Sin duración máxima | La institución la pidió después. Se agregó tope de cuatro horas consecutivas | Adenda de `PLAN_INGENIERIA.md` y `solicitud-reserva` |
| El cruce, en el primer borrador, solo contra aprobadas | Contradecía el plan. Se corrigió antes de programar | `openspec/REVISION_ESPECIFICACIONES.md` |
| Solo el solicitante crea reservas | No estaba cerrado en el primer borrador. La revisión lo fijó según el cuadro de actores | Spec de solicitud |
| El último administrador no se desactiva | Estaba en el diseño y no en la spec. Se subió a requisito | Spec de identidad |

No cambió la arquitectura, el stack, el intervalo semiabierto ni el conjunto de roles. Esas decisiones aguantaron el contacto con el código. La que no aguantó fue la de "sin tope", y no por un fallo técnico: llegó un requisito nuevo.

## Correspondencia

| Capacidad | Pruebas |
| --- | --- |
| `identidad-acceso` | `tests/test_identidad.py`, `tests/test_claves.py` |
| `catalogo-espacios` | `tests/test_espacios.py` |
| `solicitud-reserva` | `tests/test_solicitud.py`, `tests/test_ocupacion.py`, `tests/test_duracion.py` |
| `ciclo-reserva` | `tests/test_ciclo.py` |

La prueba de diez horas se invirtió en el mismo commit que el código del tope, no antes. Hasta `52c00fe` el sistema todavía aceptaba esa jornada, como decía la spec anterior. Eso es lo que el historial tiene que poder mostrar.

## Conclusión sobre SDD y OpenSpec

Frente a pedirle a un agente "hazme el sistema de reservas", la diferencia útil no fue la cantidad de markdown. Fue el momento en que se puede decir que no.

Sin spec, el agente llena los huecos con algo plausible: a veces solo la aprobada ocupa, a veces mete un tope de horas que nadie pidió, a veces deja que el coordinador cree solicitudes. Con spec, esos huecos se ven antes del diff. En este trabajo se vieron dos: la ocupación de la pendiente, y el significado de "consecutivas". Los dos se habrían colado en el código si la instrucción hubiera sido directa.

El costo también es real. Hay más archivos que lógica. Un cambio de una frase obliga a tocar el requisito, el escenario, la prueba y el archivo. OpenSpec además tiene reglas de forma (el escenario no se borra, el `SHALL` es normativo) que no perdonan un título renombrado. Para un arreglo de una línea es ceremonia. Para una invariante de cruce, la ceremonia es más barata que el defecto.

La IA sirvió para redactar el borrador y para escribir el código de tareas ya aceptadas. No sirvió como autora de la arquitectura ni como juez de la spec. La decisión de que `pendiente` ocupa, el rechazo de microservicios y la lectura de "consecutivas" como hueco cero son del plan y de la revisión. Si se delegan, el repositorio queda consistente consigo mismo y desalineado del problema.

## Respuestas para la sustentación

1. Antes de programar se cerró el monolito por capas, SQLite con la invariante en el proceso, FastAPI como contrato comprobable, sesión opaca, intervalo semiabierto, y pendiente más aprobada como ocupación. También se dejó escrito lo que no se iba a construir, incluido el tope de horas.
2. Al pasar el plan a specs apareció una spec que solo nombraba la reserva aprobada, un borde de intervalo que vivía en el diseño y no en el requisito, y un permiso de creación que el cuadro de actores no daba al coordinador. La revisión está en `openspec/REVISION_ESPECIFICACIONES.md`.
3. La IA no implementó a partir del chat. Implementó a partir de `tasks.md` de un cambio ya validado. Lo que no estaba en la spec no se codificó: el tope de cuatro horas no existe en los commits de la primera versión, aunque era tentador "dejarlo listo".
4. La planificación y el código coinciden en arquitectura y en la invariante de cruce. Difieren en la duración máxima, que entró como cambio posterior, y en tres precisiones de la revisión (ocupación, quién crea, último administrador) que el primer borrador no había copiado bien del plan.
5. La ventaja es el desacuerdo temprano y el historial que muestra spec antes que código. La limitación es el peso del proceso y el riesgo de cumplir la forma (carpetas, `SHALL`, archivo) sin mirar si el escenario de verdad fallaría. Por eso la prueba nombra el caso, y no basta con que `openspec validate` pase.
