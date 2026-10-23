# SIGREA

Sistema de gestión de reservas de laboratorios, auditorios y salas de cómputo. Centraliza la solicitud, la disponibilidad y la decisión, para no depender de correos y hojas de cálculo.

La regla de negocio que evita el doble uso: una reserva `pendiente` o `aprobada` ocupa el intervalo `[inicio, fin)`. Dos intervalos contiguos no se cruzan. El mismo usuario no puede sumar más de cuatro horas consecutivas en el mismo espacio.

## Requisitos

- Python 3.11 o superior
- pip

No hace falta un servidor de base de datos. La persistencia es un archivo SQLite.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Pruebas

```bash
pytest
```

Cada escenario de `openspec/specs/` tiene una prueba en `tests/`. La suite usa una base temporal por test. No toca `sigrea.db`.

## Ejecución

```bash
python -m sigrea
```

Queda en `http://127.0.0.1:8000`. La documentación interactiva de la API está en `http://127.0.0.1:8000/docs`.

Si la base no tiene usuarios, el arranque crea un administrador local:

| Variable | Valor por defecto |
| --- | --- |
| `SIGREA_ADMIN_CORREO` | `admin@uninpahu.edu.co` |
| `SIGREA_ADMIN_CLAVE` | `cambiar-esta-clave` |
| `SIGREA_ADMIN_NOMBRE` | `Administrador` |
| `SIGREA_DATABASE_URL` | `sqlite:///./sigrea.db` |
| `SIGREA_PORT` | `8000` |

Esas credenciales son de arranque en la máquina local. No son un secreto de producción. Cámbialas antes de exponer el proceso.

## Uso mínimo

1. `POST /api/auth/ingreso` con el administrador.
2. `POST /api/espacios` con `tipo` en `laboratorio`, `auditorio` o `sala_computo`.
3. `POST /api/auth/registro` crea solo un `solicitante`.
4. El solicitante hace `POST /api/reservas`.
5. El coordinador o el administrador llama `POST /api/reservas/{id}/aprobar` o `/rechazar`, con nota.
6. `GET /api/espacios/{id}/disponibilidad?desde=&hasta=` usa el mismo criterio de ocupación que la creación.

Las fechas llevan offset, por ejemplo `2026-10-26T08:00:00-05:00`. Sin zona, la solicitud se rechaza.

## Roles

| Acción | Solicitante | Coordinador | Administrador |
| --- | --- | --- | --- |
| Crear solicitud propia | sí | no | no |
| Aprobar o rechazar | no | sí | sí |
| Cancelar la propia, si está pendiente o aprobada | sí | sí | sí |
| Cancelar la de otro | no | sí | sí |
| Espacios y cuentas | no | no | sí |

## OpenSpec

El comportamiento vigente está en `openspec/specs/`. El historial de cada cambio, con propuesta, diseño y tareas, está en `openspec/changes/archive/`.

```bash
openspec validate --specs
openspec list --specs
```

El orden de construcción se lee en `git log`: plan, especificaciones, corrección de la ocupación, implementación, y solo después el cambio de las cuatro horas.
