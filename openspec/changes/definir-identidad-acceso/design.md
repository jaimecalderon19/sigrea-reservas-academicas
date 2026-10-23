# Design

## Context

Ver `PLAN_INGENIERIA.md`, secciones 3 y 6. No hay código de producto todavía. Esta capacidad es la primera dependencia del resto.

## Goals / Non-Goals

**Goals:**

- Tres roles: `solicitante`, `coordinador`, `administrador`.
- Registro público forzado a `solicitante`.
- Sesión opaca revocable. El rol se lee de la cuenta en cada petición.
- Correo normalizado a minúsculas, único.

**Non-Goals:**

- Recuperación de clave por correo.
- JWT.
- Reservar espacios o aprobar solicitudes.

## Decisions

- Hash PBKDF2-HMAC-SHA256 con sal aleatoria. La clave en claro no se guarda. Alternativa descartada: guardar la clave o usar solo SHA-256 sin sal.
- Token `secrets.token_urlsafe`. Se persiste solo su SHA-256. Cerrar sesión borra la fila. Alternativa descartada: JWT, ya rechazada en el plan.
- La cuenta inicial de administrador no sale de esta spec. La crea el arranque desde configuración, documentada en el README. No es un registro público.
- Errores observables como cuerpo `{"codigo", "mensaje"}`. Códigos de esta capacidad: `correo_duplicado`, `credenciales_invalidas`, `cuenta_inactiva`, `no_autenticado`, `prohibido`, `datos_invalidos`.
- Un usuario no puede desactivar su propia sesión de administrador si es la única cuenta administradora activa. Se rechaza con `datos_invalidos`. Evita dejar el sistema sin quien administre.

## Risks / Trade-offs

- [PBKDF2 en la biblioteca estándar es más lento de afinar que argon2] → 200000 iteraciones. Suficiente para esta entrega, sin dependencia nativa.
- [El rol se consulta en cada petición] → un cambio de rol aplica de inmediato. Cuesta una lectura, no una revocación de tokens.
