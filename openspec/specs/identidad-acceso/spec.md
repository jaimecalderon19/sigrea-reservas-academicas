# identidad-acceso Specification

## Purpose
Define quién puede entrar a SIGREA, con qué rol queda una cuenta nueva y quién puede cambiar el rol o desactivar a otra persona.

## Requirements

### Requirement: Registro solo como solicitante
El sistema SHALL crear una cuenta de registro público con rol solicitante y SHALL rechazar un registro que pida otro rol.

#### Scenario: Registro válido
- **WHEN** una persona se registra con nombre, correo no usado y clave
- **THEN** el sistema crea la cuenta activa con rol solicitante

#### Scenario: Intento de registrarse como administrador
- **WHEN** una persona se registra pidiendo rol administrador o coordinador
- **THEN** el sistema rechaza el registro y no crea la cuenta

### Requirement: Correo único sin distinguir mayúsculas
El sistema SHALL guardar el correo en minúsculas y SHALL rechazar un correo ya registrado aunque cambien las mayúsculas.

#### Scenario: Mismo correo con otra capitalización
- **WHEN** ya existe admin@uninpahu.edu.co y alguien se registra con Admin@uninpahu.edu.co
- **THEN** el sistema rechaza el registro e informa que el correo ya existe

### Requirement: Ingreso de cuenta activa
El sistema SHALL abrir una sesión solo si el correo y la clave corresponden a una cuenta activa.

#### Scenario: Credenciales correctas
- **WHEN** un usuario activo envía su correo y su clave
- **THEN** el sistema entrega un token de sesión que identifica a esa cuenta

#### Scenario: Clave incorrecta
- **WHEN** el correo existe y la clave no corresponde
- **THEN** el sistema rechaza el ingreso y no entrega token

#### Scenario: Cuenta inactiva
- **WHEN** la clave es correcta y la cuenta está inactiva
- **THEN** el sistema rechaza el ingreso y no entrega token

### Requirement: Cierre de sesión
El sistema SHALL invalidar el token al cerrar la sesión.

#### Scenario: Token usado después de salir
- **WHEN** el usuario cierra la sesión y reutiliza ese token
- **THEN** el sistema rechaza la petición por falta de sesión válida

### Requirement: Administración de rol y estado
El sistema SHALL permitir al administrador cambiar el rol y activar o desactivar una cuenta, y SHALL rechazar esa acción si la hace un solicitante o un coordinador.

#### Scenario: El administrador cambia el rol
- **WHEN** un administrador asigna rol coordinador a un solicitante activo
- **THEN** la cuenta queda con rol coordinador

#### Scenario: El solicitante no administra cuentas
- **WHEN** un solicitante intenta cambiar el rol o el estado de otra cuenta
- **THEN** el sistema rechaza la acción por falta de permiso

#### Scenario: El coordinador no administra cuentas
- **WHEN** un coordinador intenta desactivar una cuenta
- **THEN** el sistema rechaza la acción por falta de permiso

### Requirement: Siempre queda un administrador activo
El sistema SHALL rechazar desactivar o cambiar el rol del único administrador activo.

#### Scenario: El único administrador no se desactiva
- **WHEN** el único administrador activo intenta desactivar su propia cuenta
- **THEN** el sistema rechaza la acción y la cuenta sigue activa y con rol administrador

#### Scenario: Hay otro administrador
- **WHEN** existen dos administradores activos y uno desactiva al otro
- **THEN** la cuenta desactivada queda inactiva y el otro administrador sigue activo

### Requirement: Sesión obligatoria para operar
El sistema SHALL rechazar una operación de negocio cuando la petición no trae una sesión válida.

#### Scenario: Petición sin token
- **WHEN** un cliente pide el listado de usuarios sin token
- **THEN** el sistema rechaza la petición por falta de sesión válida
