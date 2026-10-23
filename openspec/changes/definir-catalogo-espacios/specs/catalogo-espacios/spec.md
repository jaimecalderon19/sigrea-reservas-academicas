# Spec Delta

## Purpose

Mantiene el inventario de laboratorios, auditorios y salas de cómputo, con un responsable único de las altas y las bajas lógicas.

## ADDED Requirements

### Requirement: Alta de espacio por el administrador
El sistema SHALL permitir al administrador crear un espacio con código único, nombre, tipo, capacidad positiva y ubicación, y SHALL rechazar el alta a los demás roles.

#### Scenario: Alta de laboratorio
- **WHEN** un administrador crea un espacio de tipo laboratorio con capacidad 20 y código LAB-01
- **THEN** el espacio queda consultable, activo, con esos datos

#### Scenario: Tipos admitidos
- **WHEN** un administrador crea un auditorio y una sala de cómputo con códigos distintos
- **THEN** ambos quedan registrados con su tipo

#### Scenario: Capacidad no positiva
- **WHEN** un administrador crea un espacio con capacidad 0 o negativa
- **THEN** el sistema rechaza el alta y no crea el espacio

#### Scenario: Tipo no admitido
- **WHEN** un administrador crea un espacio con un tipo distinto de laboratorio, auditorio o sala de cómputo
- **THEN** el sistema rechaza el alta

#### Scenario: Código duplicado
- **WHEN** ya existe el código LAB-01 y un administrador intenta crear otro espacio con ese código
- **THEN** el sistema rechaza el alta e informa que el código ya existe

#### Scenario: El coordinador no crea espacios
- **WHEN** un coordinador intenta crear un espacio
- **THEN** el sistema rechaza la acción por falta de permiso

#### Scenario: El solicitante no crea espacios
- **WHEN** un solicitante intenta crear un espacio
- **THEN** el sistema rechaza la acción por falta de permiso

### Requirement: Consulta del catálogo
El sistema SHALL permitir a cualquier usuario autenticado listar los espacios y consultar uno por identificador, incluidos los inactivos.

#### Scenario: Listado autenticado
- **WHEN** un solicitante pide el listado y existe al menos un espacio
- **THEN** el sistema devuelve ese espacio con su estado activo o inactivo

#### Scenario: Identificador inexistente
- **WHEN** un usuario autenticado consulta un identificador que no existe
- **THEN** el sistema informa que el espacio no existe

#### Scenario: Consulta sin sesión
- **WHEN** un cliente lista espacios sin sesión válida
- **THEN** el sistema rechaza la petición por falta de sesión

### Requirement: Actualización y baja lógica
El sistema SHALL permitir al administrador modificar los datos de un espacio y desactivarlo sin eliminarlo.

#### Scenario: Desactivar un espacio
- **WHEN** un administrador marca un espacio activo como inactivo
- **THEN** el espacio sigue en el catálogo con estado inactivo

#### Scenario: El coordinador no modifica el catálogo
- **WHEN** un coordinador intenta desactivar un espacio
- **THEN** el sistema rechaza la acción por falta de permiso
