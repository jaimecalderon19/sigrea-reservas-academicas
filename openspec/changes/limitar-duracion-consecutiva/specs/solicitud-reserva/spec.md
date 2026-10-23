# Spec Delta

## MODIFIED Requirements

### Requirement: Intervalo válido
El sistema SHALL exigir inicio anterior al fin, duración de al menos 30 minutos y como máximo cuatro horas, e instantes con zona horaria explícita.

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
- **THEN** el sistema rechaza la solicitud e informa que supera las cuatro horas consecutivas

#### Scenario: Duración de cuatro horas
- **WHEN** un solicitante pide un espacio libre de 08:00 a 12:00
- **THEN** el sistema acepta la solicitud en estado pendiente

#### Scenario: Duración mayor a cuatro horas
- **WHEN** un solicitante pide un espacio libre de 08:00 a 12:01
- **THEN** el sistema rechaza la solicitud e informa que supera las cuatro horas consecutivas

## ADDED Requirements

### Requirement: Bloque consecutivo del mismo usuario
El sistema SHALL rechazar la solicitud si, al unirla sin hueco con las reservas pendientes o aprobadas del mismo usuario y del mismo espacio, el bloque continuo supera cuatro horas.

#### Scenario: Encadenar hasta cuatro horas
- **WHEN** el mismo solicitante ya tiene una reserva pendiente del espacio E de 08:00 a 10:00 y pide E de 10:00 a 12:00
- **THEN** el sistema acepta la solicitud en estado pendiente

#### Scenario: Encadenar por encima de cuatro horas
- **WHEN** el mismo solicitante ya tiene una reserva pendiente del espacio E de 08:00 a 10:00 y pide E de 10:00 a 12:01
- **THEN** el sistema rechaza la solicitud e informa que supera las cuatro horas consecutivas

#### Scenario: Un hueco rompe la consecutividad
- **WHEN** el mismo solicitante ya tiene una reserva pendiente del espacio E de 08:00 a 10:00 y pide E de 10:01 a 14:00
- **THEN** el sistema acepta la solicitud en estado pendiente

#### Scenario: Otro espacio no se suma
- **WHEN** el mismo solicitante ya tiene una reserva pendiente del espacio E1 de 08:00 a 12:00 y pide el espacio E2 de 08:00 a 12:00
- **THEN** el sistema acepta la solicitud sobre E2 en estado pendiente

#### Scenario: Otro usuario no se suma
- **WHEN** un solicitante tiene una reserva pendiente del espacio E de 08:00 a 12:00 y otro solicitante pide E de 12:00 a 16:00
- **THEN** el sistema acepta la solicitud del segundo solicitante en estado pendiente

#### Scenario: Una reserva rechazada no alarga el bloque
- **WHEN** la única reserva previa del solicitante en E, de 08:00 a 10:00, está rechazada y pide E de 10:00 a 14:00
- **THEN** el sistema acepta la solicitud en estado pendiente
