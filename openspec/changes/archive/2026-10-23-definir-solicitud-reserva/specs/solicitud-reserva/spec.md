# Spec Delta

## Purpose

Permite a un solicitante pedir un espacio en un intervalo concreto y consultar qué tramos figuran como ocupados antes de decidir.

## ADDED Requirements

### Requirement: Creación de solicitud propia
El sistema SHALL crear la solicitud a nombre del usuario autenticado, en estado pendiente, sobre un espacio activo, con propósito no vacío de hasta 500 caracteres.

#### Scenario: Solicitud aceptada
- **WHEN** un solicitante pide un espacio activo de 08:00 a 10:00 con un propósito
- **THEN** el sistema registra la solicitud en estado pendiente, a nombre de ese solicitante

#### Scenario: Propósito vacío
- **WHEN** un solicitante envía un propósito vacío o de solo espacios
- **THEN** el sistema rechaza la solicitud y no la registra

#### Scenario: Espacio inactivo
- **WHEN** un solicitante pide un espacio marcado inactivo
- **THEN** el sistema rechaza la solicitud e informa que el espacio no admite reservas

#### Scenario: Espacio inexistente
- **WHEN** un solicitante pide un identificador de espacio que no existe
- **THEN** el sistema informa que el espacio no existe y no registra la solicitud

#### Scenario: Propósito de 501 caracteres
- **WHEN** un solicitante envía un propósito de 501 caracteres
- **THEN** el sistema rechaza la solicitud y no la registra

#### Scenario: El coordinador no crea solicitudes
- **WHEN** un coordinador pide un espacio activo y libre
- **THEN** el sistema rechaza la acción por falta de permiso y no registra la solicitud

### Requirement: Intervalo válido
El sistema SHALL exigir inicio anterior al fin, duración de al menos 30 minutos e instantes con zona horaria explícita.

#### Scenario: Fin que no es posterior al inicio
- **WHEN** el fin es igual o anterior al inicio
- **THEN** el sistema rechaza la solicitud

#### Scenario: Duración menor a 30 minutos
- **WHEN** el intervalo dura 29 minutos
- **THEN** el sistema rechaza la solicitud

#### Scenario: Duración de 30 minutos
- **WHEN** un solicitante pide un espacio libre durante 30 minutos exactos
- **THEN** el sistema acepta la solicitud en estado pendiente

#### Scenario: Instante sin zona
- **WHEN** inicio o fin llegan sin offset de zona horaria
- **THEN** el sistema rechaza la solicitud

#### Scenario: Duración de varias horas
- **WHEN** un solicitante pide un espacio libre de 08:00 a 18:00
- **THEN** el sistema acepta la solicitud en estado pendiente

### Requirement: Ocupación del intervalo
El sistema SHALL tratar como ocupado el intervalo de toda reserva pendiente o aprobada del mismo espacio, SHALL comparar intervalos semiabiertos y SHALL rechazar la solicitud que se cruce con esa ocupación.

#### Scenario: Solape parcial con reserva pendiente
- **WHEN** existe una reserva pendiente del espacio E de 08:00 a 10:00 y otro solicitante pide E de 09:00 a 11:00
- **THEN** el sistema rechaza la solicitud e informa que el espacio no está disponible

#### Scenario: Solape parcial con reserva aprobada
- **WHEN** existe una reserva aprobada del espacio E de 08:00 a 10:00 y un solicitante pide E de 09:00 a 11:00
- **THEN** el sistema rechaza la solicitud e informa que el espacio no está disponible

#### Scenario: Intervalo idéntico a una pendiente
- **WHEN** existe una reserva pendiente del espacio E de 08:00 a 10:00 y otro solicitante pide E de 08:00 a 10:00
- **THEN** el sistema rechaza la solicitud e informa que el espacio no está disponible

#### Scenario: Mismo intervalo en otro espacio
- **WHEN** existe una reserva pendiente del espacio E1 de 08:00 a 10:00 y un solicitante pide E2 en ese mismo intervalo
- **THEN** el sistema acepta la solicitud sobre E2 en estado pendiente

#### Scenario: Intervalos contiguos
- **WHEN** existe una reserva pendiente del espacio E que termina a las 10:00 y un solicitante pide E desde las 10:00 hasta las 11:00
- **THEN** el sistema acepta la solicitud en estado pendiente

#### Scenario: Solape de un segundo
- **WHEN** existe una reserva pendiente del espacio E que termina a las 10:00:01 y un solicitante pide E desde las 10:00:00 durante 30 minutos
- **THEN** el sistema rechaza la solicitud e informa que el espacio no está disponible

### Requirement: Consulta de disponibilidad
El sistema SHALL informar a un usuario autenticado los intervalos de reservas pendientes y aprobadas del espacio que se cruzan con el rango consultado, y SHALL omitir rechazadas y canceladas.

#### Scenario: Pendiente y aprobada dentro del rango
- **WHEN** un usuario autenticado consulta E entre 07:00 y 12:00 y E tiene una pendiente de 08:00 a 09:00 y una aprobada de 09:00 a 10:00
- **THEN** la respuesta incluye esos dos intervalos y no incluye reservas de otros espacios

#### Scenario: Rechazada fuera de la ocupación
- **WHEN** un usuario autenticado consulta E en un rango donde la única reserva de E está rechazada
- **THEN** la respuesta no incluye esa reserva
