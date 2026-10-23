# Tasks

## 1. Dominio e infraestructura

- [ ] 1.1 Crear el paquete `sigrea` con error de negocio, hash de clave y normalización de correo. Verificar con una prueba de dominio que el mismo correo en mayúsculas normaliza igual y que la clave no se guarda en claro.
- [ ] 1.2 Persistir usuarios y sesiones en SQLite. Verificar que el arranque crea las tablas sobre una base temporal.

## 2. Casos de uso y API

- [ ] 2.1 Implementar registro, ingreso, salida y administración de rol y estado, incluida la protección del último administrador. Verificar con las pruebas de API de `identidad-acceso` que cada escenario de la spec corregida pasa.
- [ ] 2.2 Rechazar peticiones sin sesión en el listado de usuarios. Verificar el escenario "Petición sin token".
