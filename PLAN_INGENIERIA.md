# Plan de ingeniería

Sistema Institucional de Gestión de Reservas de Espacios Académicos (SIGREA)

Fecha: 2026-10-23
Estado: decisión previa a especificaciones e implementación
Restricción de proceso: este documento se cierra antes de inicializar OpenSpec y antes de escribir código de producto.

## 1. Análisis del problema

### Problemática

Las reservas de laboratorios, auditorios y salas de cómputo se piden por correo y se anotan en hojas de cálculo. Ese canal no tiene una fuente única de verdad. Dos personas pueden pedir el mismo espacio en el mismo intervalo, la hoja puede quedar desactualizada respecto al correo, y nadie puede consultar disponibilidad sin escribirle a quien administra el archivo.

El fallo no es de comunicación. Es de consistencia: el estado de ocupación no se valida en el momento de la solicitud, no hay un dueño del conflicto y el historial queda repartido entre buzones.

### Necesidades de la institución

- Un registro único de espacios académicos y de su estado (activo o fuera de servicio).
- Un registro de personas que solicitan y de personas que deciden.
- Una solicitud de reserva con intervalo, espacio y propósito, aceptada o rechazada de forma explícita.
- Una consulta de disponibilidad que use el mismo criterio con el que se acepta o se niega una solicitud.
- Impedir que dos reservas vigentes ocupen el mismo espacio al mismo tiempo.
- Conservar aprobaciones, rechazos y cancelaciones. Borrar una fila no es un historial.

### Actores

| Actor | Qué necesita | Qué no hace |
| --- | --- | --- |
| Solicitante (docente, estudiante, monitor) | Ver espacios, consultar ocupación, crear una solicitud propia, cancelar la suya, ver su historial | Aprobar solicitudes ajenas, alterar el catálogo, cambiar roles |
| Coordinador de espacios | Ver todas las solicitudes, aprobar o rechazar las pendientes, cancelar una reserva vigente cuando el uso institucional lo exige | Crear espacios, asignar roles |
| Administrador institucional | Alta y baja de espacios, alta y administración de usuarios, todo lo que hace el coordinador | Quedar fuera de la auditoría: sus acciones también quedan registradas |
| Quien opera el despliegue | Instalar, configurar la cuenta inicial de administrador, ejecutar pruebas | No es un rol de negocio dentro de la aplicación |

No hay un actor "hoja de cálculo". El sistema lo reemplaza. El correo deja de ser el canal de decisión.

### Alcance

Incluido en la primera versión:

1. Catálogo de espacios: laboratorio, auditorio, sala de cómputo.
2. Registro de usuarios y administración de cuentas.
3. Tres roles con permisos distintos: solicitante, coordinador, administrador.
4. Creación de solicitudes de reserva.
5. Consulta de disponibilidad.
6. Rechazo de una solicitud que se cruce con otra reserva vigente del mismo espacio.
7. Aprobación y rechazo, con nota de revisión.
8. Cancelación, sin borrar el registro.
9. Consulta del historial, filtrable por estado.

Fuera de alcance, a propósito:

- Sincronización con calendario externo, correo automático y el sistema académico de la institución.
- Reservas recurrentes, lista de espera, inventario de equipos dentro del laboratorio y pagos.
- Aplicación móvil nativa. La interfaz de esta entrega es una API HTTP verificable con pruebas.
- Un tope de duración. La primera versión no limita cuántas horas puede pedir un usuario. Si la institución agrega esa regla, entra como cambio de especificación, no como un parche silencioso.
- Varias sedes con reglas distintas. Hay una institución y un catálogo.

### Limitaciones aceptadas

- Despliegue de un solo proceso. No se diseña un clúster.
- La cuenta inicial de administrador se crea por configuración local, no por un flujo de invitación.
- No hay recuperación de contraseña por correo. El administrador reactiva o reemplaza la clave en un procedimiento operativo descrito en el README, no en esta versión del producto.
- La zona horaria de negocio es `America/Bogota`. Los instantes se guardan con zona explícita. No se aceptan fechas "naive".

## 2. Propuesta de solución

### Descripción

SIGREA es un servicio HTTP con una base relacional local. Cada reserva es una fila con estado. La ocupación de un espacio no es una opinión de la hoja de cálculo: es el conjunto de reservas en estado `pendiente` o `aprobada` cuyo intervalo se cruza con el pedido.

La decisión de tratar `pendiente` como ocupación es deliberada. Si solo `aprobada` ocupara el cupo, dos solicitantes verían el mismo hueco, ambos crearían la solicitud y el coordinador descubriría el conflicto al aprobar la segunda. Eso reproduce el problema del correo. Una solicitud pendiente bloquea el intervalo hasta que se rechaza o se cancela. El rechazo y la cancelación liberan el cupo y dejan el registro.

Los intervalos son semiabiertos: `[inicio, fin)`. Una reserva que termina a las 10:00 y otra que empieza a las 10:00 no se cruzan. Así se pueden encadenar bloques contiguos sin un minuto muerto artificial.

Duración mínima: 30 minutos. Por debajo de eso la reserva no representa un uso académico real y multiplica filas inútiles. Duración máxima: ninguna en esta versión.

### Funcionalidades prioritarias

Ordenadas por el daño que evitan, no por lo vistoso de la pantalla:

1. Impedir el cruce de reservas vigentes. Sin esto el sistema miente.
2. Catálogo de espacios, porque no hay reserva sin espacio identificable.
3. Usuarios y roles, porque la aprobación no puede estar abierta a cualquiera.
4. Ciclo de vida: crear, aprobar, rechazar, cancelar, consultar. El historial es parte del ciclo, no un reporte aparte.

### Módulos

| Módulo | Responsabilidad | Depende de |
| --- | --- | --- |
| Identidad | Registro, ingreso, sesión, rol, cuenta activa | Nada de negocio |
| Catálogo | Alta, consulta y actualización de espacios | Identidad, para saber quién escribe |
| Disponibilidad | Predicado de cruce y consulta de intervalos ocupados | Catálogo |
| Reservas | Crear solicitud, aplicar el predicado, cambiar estado, historial | Identidad, catálogo, disponibilidad |

La regla de cruce vive en el dominio, no en el controlador HTTP. La API solo traduce la decisión a una respuesta. Así la misma regla se prueba sin levantar el servidor.

### Estrategia progresiva

No se construye "el sistema" de una vez. Cada módulo se especifica, se revisa y se implementa cuando sus dependencias ya tienen comportamiento comprobable. El orden está en la sección 4. Una funcionalidad sin especificación revisada no se programa.

## 3. Decisiones de arquitectura y tecnología

### Arquitectura

Monolito modular por capas:

- `api`: HTTP, autenticación de la petición, traducción de errores.
- `aplicacion`: casos de uso. Una operación de negocio por función, con transacción.
- `dominio`: estados, intervalos, permisos, predicado de cruce. Sin framework.
- `infraestructura`: SQLAlchemy y SQLite. El dominio no importa esta capa.

Justificación: el problema es un solo proceso de negocio con una invariante (no hay dos ocupaciones vigentes cruzadas). Partir eso en servicios separados metería la invariante en la red. Un monolito modular deja la invariante en un solo lugar y aun así separa la regla del transporte.

Organización de componentes: cada caso de uso recibe un repositorio y un reloj. Las rutas no abren SQL. Los permisos se deciden en aplicación, a partir del rol, no con `if` sueltos en cada ruta.

### Stack

- Python 3.11 o superior. Ya está en la máquina de desarrollo y alcanza para tipar el dominio sin un segundo lenguaje.
- FastAPI, para una API pequeña con validación de entrada y un cliente de pruebas.
- SQLAlchemy 2 y SQLite en archivo. La base se crea al arrancar. No hay un servidor de base que instalar para correr las pruebas.
- pytest y el cliente HTTP de Starlette. Cada escenario de aceptación que sea observable por HTTP tiene una prueba.
- Contraseñas con PBKDF2-HMAC-SHA256 de la biblioteca estándar. El hash y la sal se guardan. No se guarda la clave.
- Sesión opaca: un token aleatorio cuyo resumen SHA-256 se guarda. El cliente envía `Authorization: Bearer`. No se usa JWT en esta versión: no hay varios emisores ni necesidad de leer el token sin consultar la sesión.

### Persistencia

Tabla `usuarios`, tabla `espacios`, tabla `reservas`, tabla `sesiones`.

La reserva guarda solicitante, espacio, inicio, fin, propósito, estado, y los datos de revisión o cancelación (quién, cuándo, nota). No se reescribe la fila hasta desaparecer. El estado cambia. El historial es la propia tabla filtrada.

La consulta de cruce es:

```text
mismo espacio
y estado en (pendiente, aprobada)
y inicio < fin_ajena
y fin > inicio_ajena
```

Eso no cabe en un `UNIQUE`. La comprobación se hace dentro de la transacción que inserta, y el proceso serializa las escrituras de reservas con un cerrojo de aplicación. SQLite en un solo proceso no ofrece una restricción de exclusión como PostgreSQL. El cerrojo cierra la ventana entre el `SELECT` de cruce y el `INSERT`.

Zona: se acepta un instante con offset. Se normaliza a UTC para comparar. La regla de negocio sigue siendo la hora de Bogotá solo como convención de quienes usan el sistema, no como un reloj implícito.

### Tres decisiones, con lo que se descartó

**1. Monolito modular, no microservicios ni "solo una hoja mejorada".**

Se descartó un servicio de espacios, otro de usuarios y otro de reservas. La invariante de cruce cruza los tres. Una llamada remota fallida dejaría una reserva a medias. También se descartó seguir en hojas de cálculo con validación manual: es el sistema actual y es el problema. El monolito es la opción que mantiene la invariante en un proceso y todavía permite pruebas por módulo.

**2. SQLite con SQLAlchemy, no PostgreSQL desde el día uno y no un documento JSON.**

Se descartó PostgreSQL como dependencia de arranque. Para una entrega académica que debe correr con `pytest` y un comando de servidor, exigir otro demonio es fricción sin un segundo escritor. Se deja anotado el camino de producción: en PostgreSQL la misma predicado puede reforzarse con una restricción de exclusión (`tstzrange`) sobre reservas vigentes. Se descartó guardar cada reserva como documento sin esquema. El cruce es una consulta relacional. Un almacén de documentos obligaría a traer intervalos a memoria para compararlos, que es justo donde aparecen los conflictos que la hoja de cálculo ya tiene.

**3. API HTTP con pruebas, no Django completo y no una CLI como único producto.**

Se descartó Django. Trae admin, ORM y plantillas que esta versión no usa, y empuja la regla de negocio hacia el framework. Se descartó una CLI como única interfaz: el coordinador no va a aprobar reservas en una terminal como producto institucional, y una CLI no deja un contrato fácil de probar desde fuera. FastAPI deja el contrato en HTTP, que es lo que las pruebas de aceptación ejercen. Una interfaz web puede sentarse encima después sin mover la regla de cruce.

**4. Sesión opaca en base, no JWT y no HTTP Basic en cada petición.**

Se descartó JWT porque obliga a una biblioteca, a un secreto de firma y a una estrategia de revocación que esta versión no necesita. Cerrar sesión aquí es borrar la fila. Se descartó Basic con la contraseña en cada llamada: alarga la vida del secreto y complica la salida. El token opaco se revoca al salir y no contiene el rol. El rol se lee de la cuenta en cada petición, así un cambio de rol aplica sin esperar a que expire un token.

## 4. Estrategia de desarrollo

### Metodología

Spec-Driven Development con OpenSpec, sobre el orden que fija este plan. El ciclo de cada cambio es: propuesta, especificación con escenarios, diseño técnico del cambio, tareas, revisión, implementación, pruebas, archivo del cambio. Git registra ese orden. Un commit de código de producto no puede preceder al commit de la especificación que lo autoriza.

La metodología de trabajo diario es incremental y por vertical: se cierra un comportamiento comprobable antes de abrir el siguiente. No hay un sprint ceremonial. Hay una cola de cambios con una sola intención cada uno.

### Etapas

| Etapa | Qué queda cerrado | Criterio de terminado |
| --- | --- | --- |
| 0. Este plan | Decisiones y límites | Commit que solo contiene este archivo, anterior a `openspec/` y al código |
| 1. Especificación inicial | Comportamiento de los cuatro módulos, en escenarios | `openspec validate` sin errores y revisión escrita contra este plan |
| 2. Identidad y catálogo | Registro, ingreso, roles, CRUD de espacios | Pruebas de permiso y de validación de espacio en verde |
| 3. Reservas y conflictos | Solicitud, disponibilidad, cruce, estados, historial | Pruebas de los escenarios de aceptación en verde, incluida la contigüidad de intervalos |
| 4. Cambio de negocio | Tope que la institución pida después, si llega | Especificación actualizada antes del código, pruebas nuevas y pruebas anteriores en verde |
| 5. Cierre | README, informe, archivo OpenSpec | Un tercero clona, instala, prueba y arranca con el README |

### Orden de funcionalidades

1. Modelo de usuarios, hash de clave, ingreso y rechazo de cuenta inactiva.
2. Autorización por rol.
3. Espacios: crear, listar, actualizar, impedir reserva sobre espacio inactivo.
4. Predicado de cruce, aislado, con casos de borde (contiguo, contenido, solape parcial, otro espacio).
5. Crear solicitud, que usa el predicado dentro de la transacción.
6. Consulta de disponibilidad, que usa el mismo predicado.
7. Aprobar, rechazar, cancelar.
8. Historial filtrado según el rol.

No se invierte este orden. Aprobar no tiene sentido si crear todavía no valida el cruce.

### Dependencias entre componentes

- La API depende de aplicación. Aplicación depende de dominio y de puertos de repositorio. Infraestructura implementa esos puertos.
- Reservas depende de identidad (quién pide, quién decide) y de catálogo (el espacio existe y está activo).
- Disponibilidad no depende de HTTP.
- Las pruebas de dominio no dependen de la base. Las pruebas de API dependen de una base temporal por test.

### Criterio de etapa terminada

Una etapa termina cuando se cumplen las tres cosas, no una:

- Los escenarios de su especificación tienen una prueba que fallaría si se quitara la regla.
- Un rol que no debe ejecutar la acción recibe rechazo, y eso también está probado.
- El commit correspondiente no mezcla una funcionalidad de una etapa posterior.

## 5. Estrategia de calidad

### Pruebas

- Dominio: predicado de cruce y, cuando exista, la regla de duración. Sin base y sin HTTP.
- Aplicación, vía API: cada escenario de aceptación que el enunciado pide, con el cliente de pruebas y una base temporal.
- Permisos: cada escritura se prueba con el rol que sí puede y con un rol que no puede.
- Regresión: la suite completa se corre después de cada cambio, en particular después del cambio de duración, para ver que el cruce y el ciclo de vida siguen igual.

No hay prueba de carga ni de interfaz gráfica en esta entrega. El riesgo que importa es la invariante, y esa se prueba con casos, no con usuarios simultáneos simulados más allá del cerrojo.

### Riesgos y mitigación

| # | Riesgo | Cómo se nota | Mitigación |
| --- | --- | --- | --- |
| 1 | Dos solicitudes simultáneas pasan el chequeo de cruce | La segunda también queda `pendiente` | Cerrojo de proceso alrededor de leer-y-escribir, más relectura dentro de la transacción. Prueba de dos intervalos cruzados en secuencia y revisión del orden del código |
| 2 | `pendiente` no ocupa cupo y el coordinador aprueba un conflicto | Dos aprobadas cruzadas | La especificación fija que pendiente y aprobada ocupan. La revisión de specs compara esa frase con este plan antes de programar |
| 3 | Fechas sin zona se comparan mal | Un mismo reloj local se guarda distinto según la máquina | Rechazar instantes sin offset. Normalizar a UTC al persistir. Prueba con `-05:00` |
| 4 | El agente de IA programa comportamiento que no está especificado, o se salta un permiso | Aparece un tope de horas, un rol nuevo, o un solicitante aprueba | La implementación se hace contra `tasks.md` de un cambio ya revisado. Cada tarea cita el escenario. Lo que no está en la spec no se codifica |
| 5 | Un cambio de regla se mete en el código y la spec queda vieja | El informe no puede explicar de dónde salió la regla | Prohibido tocar el código de esa regla antes del commit de la delta OpenSpec. El historial de Git es la evidencia |
| 6 | SQLite no sostiene el modo de producción con varios procesos | Dos procesos escriben y el cerrojo de aplicación no los ve | Limitación declarada. Un segundo proceso queda fuera de esta entrega. El camino a PostgreSQL queda escrito, no simulado |
| 7 | Credenciales de demostración se tratan como secreto de producción | Alguien reutiliza la clave del README | El README las marca como datos de arranque local. No hay otro secreto en el repositorio |

### Verificación de requisitos

Cada requisito de OpenSpec tiene al menos un escenario `WHEN` / `THEN`. La revisión marca el escenario y la prueba que lo cubre. Si un requisito no se puede observar desde fuera del código, no está listo y se reescribe antes de implementar.

El cierre compara tres listas: requisitos archivados en `openspec/specs/`, pruebas con nombre del escenario, y secciones de este plan. Una divergencia se documenta en el informe final como decisión cambiada, no se esconde.

## 6. Uso de SDD e inteligencia artificial

### Cómo se usa OpenSpec

OpenSpec es el registro de comportamiento, no el plan de ingeniería. Este archivo dice por qué se eligió la arquitectura. OpenSpec dice qué debe poder observarse cuando el sistema funciona.

Flujo por cambio:

1. `openspec new change <nombre>` crea la carpeta del cambio.
2. `proposal.md` dice la intención en una frase y lista capacidades.
3. `specs/<capacidad>/spec.md` escribe requisitos con `SHALL` y escenarios.
4. `design.md` baja las decisiones de este plan al cambio, sin inventar otra arquitectura.
5. `tasks.md` parte el trabajo en tareas verificables.
6. Se revisa. Si hay contradicción con este plan, se corrige la spec, no el plan en silencio.
7. Solo entonces se implementa, tarea por tarea.
8. `openspec archive` incorpora los requisitos a `openspec/specs/` y guarda el cambio.

La primera versión entra como un cambio de capacidades nuevas. Un cambio posterior de la institución entra como otra carpeta, con `MODIFIED` sobre el requisito que de verdad cambie.

### Del plan a las especificaciones

Este plan no se pega dentro de la spec. Se traduce:

- Actores y permisos pasan a requisitos de autorización, con un escenario por acción prohibida.
- La invariante de cruce pasa a un requisito con escenarios de solape, de contigüidad y de otro espacio.
- Lo que está fuera de alcance no se escribe como requisito. En particular, no habrá un `SHALL` de duración máxima hasta que la institución lo pida y exista un cambio nuevo.
- Las decisiones de stack se quedan en `design.md`. Si mañana la base cambia a PostgreSQL y el comportamiento observable no cambia, la spec no se toca.

### Qué se delega a la IA

- Redactar el borrador de deltas a partir de este plan, para luego corregirlo.
- Escribir el código de las tareas ya aceptadas y las pruebas que nombran el escenario.
- Señalar, al implementar, si una tarea no se puede cumplir sin ampliar la spec. En ese caso se para y se actualiza la spec primero.

### Cómo se verifica el código generado

- La suite se ejecuta. Una tarea no se marca hecha si su prueba no pasa.
- Se lee el diff contra la spec, no contra la intención recordada del chat. Si el código rechaza un caso que la spec permite, o permite un caso que la spec rechaza, manda la spec.
- `openspec validate` se corre sobre el cambio antes de archivar.
- El estudiante (quien entrega) revisa permisos y la invariante de cruce a mano. Esas dos no se dan por buenas porque la prueba exista: se mira que la prueba realmente arme el caso.

### Qué no se delega

- Elegir arquitectura, stack y la decisión de que `pendiente` ocupa cupo. Ya están en este documento.
- Aceptar una spec ambigua. Si un escenario no se puede convertir en prueba, se reescribe antes de programar.
- Meter una regla de negocio nueva directo en el código.
- Declarar la etapa terminada. Eso exige las pruebas en verde y el commit en el orden correcto.

## Decisiones que este plan deja cerradas

Para que la spec no las reabra:

- Estados de reserva: `pendiente`, `aprobada`, `rechazada`, `cancelada`.
- Ocupan cupo: `pendiente` y `aprobada`.
- Intervalo semiabierto `[inicio, fin)`.
- Duración mínima de 30 minutos. Sin duración máxima en la primera versión. Ver la adenda.
- Registro público solo puede crear un `solicitante`. Rol y desactivación los cambia el administrador.
- Un solicitante cancela lo suyo si está pendiente o aprobada. Coordinador y administrador pueden cancelar cualquiera en esos dos estados.
- Aprobar y rechazar exigen nota. Solo desde `pendiente`. Solo coordinador o administrador.
- Un espacio inactivo no admite solicitudes nuevas. Su historial se conserva.
- El propósito es obligatorio, hasta 500 caracteres.
- El correo se guarda en minúsculas y es único.

## Adenda 2026-10-23. Tope de cuatro horas

La institución pidió, ya con las capacidades iniciales especificadas e implementadas, que ningún usuario reserve un espacio durante más de cuatro horas consecutivas.

Afecta este plan en un solo punto: la frase "sin duración máxima" deja de describir el sistema. No afecta la arquitectura, el stack, la ocupación de `pendiente` y `aprobada`, ni el intervalo semiabierto.

Interpretación que se lleva a la spec, para no dejar "consecutivas" ambiguo:

- Cuatro horas exactas se permiten. Un segundo más, no.
- Consecutivo es el bloque del mismo usuario en el mismo espacio, uniendo reservas vigentes que se tocan sin hueco.
- Un hueco, otro espacio u otro usuario no se suman.
- Rechazadas y canceladas no alargan el bloque.

El cambio se especifica en `limitar-duracion-consecutiva` antes de tocar el código. La prueba que aceptaba 08:00 a 18:00 se invierte en la implementación de ese cambio, no en este registro.
