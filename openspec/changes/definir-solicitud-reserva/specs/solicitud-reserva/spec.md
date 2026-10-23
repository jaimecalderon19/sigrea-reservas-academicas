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

### Requirement: Intervalo válido
El sistema SHALL exigir inicio anterior al fin, duración de al menos 30 minutos e instantes con zona horaria explícita.

#### Scenario: Fin que no es posterior al inicio
- **WHEN** el fin es igual o anterior al inicio
- **THEN** el sistema rechaza la solicitud

#### Scenario: Duración menor a 30 minutos
- **WHEN** el intervalo dura 29 minutos
- **THEN** el sistema rechaza la solicitud

#### Scenario: Instante sin zona
- **WHEN** inicio o fin llegan sin offset de zona horaria
- **THEN** el sistema rechaza la solicitud

#### Scenario: Duración de varias horas
- **WHEN** un solicitante pide un espacio libre de 08:00 a 18:00
- **THEN** el sistema acepta la solicitud en estado pendiente

### Requirement: Cruce con reserva aprobada
El sistema SHALL rechazar una solicitud cuyo intervalo se cruce con una reserva aprobada del mismo espacio.

#### Scenario: Solape parcial con reserva aprobada
- **WHEN** existe una reserva aprobada del espacio E de 08:00 a 10:00 y un solicitante pide E de 09:00 a 11:00
- **THEN** el sistema rechaza la solicitud e informa que el espacio no está disponible

#### Scenario: Mismo intervalo en otro espacio
- **WHEN** existe una reserva aprobada del espacio E1 de 08:00 a 10:00 y un solicitante pide E2 en ese mismo intervalo
- **THEN** el sistema acepta la solicitud sobre E2 en estado pendiente

#### Scenario: Intervalos contiguos
- **WHEN** existe una reserva aprobada del espacio E que termina a las 10:00 y un solicitante pide E desde las 10:00 hasta las 11:00
- **THEN** el sistema acepta la solicitud en estado pendiente

### Requirement: Consulta de disponibilidad
El sistema SHALL informar a un usuario autenticado los intervalos ocupados de un espacio dentro del rango consultado.

#### Scenario: Rango con una reserva aprobada
- **WHEN** un usuario autenticado consulta la disponibilidad de E entre 07:00 y 12:00 y hay una reserva aprobada de 08:00 a 10:00
- **THEN** la respuesta incluye ese intervalo ocupado y no incluye tramos de otros espacios
