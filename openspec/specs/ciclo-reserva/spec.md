# ciclo-reserva Specification

## Purpose
Registra la decisión sobre una solicitud pendiente y conserva aprobaciones, rechazos y cancelaciones para consulta posterior.

## Requirements

### Requirement: Aprobación de solicitud pendiente
El sistema SHALL pasar una solicitud pendiente a aprobada cuando un coordinador o un administrador envía una nota de revisión, y SHALL rechazar la aprobación en cualquier otro caso.

#### Scenario: El coordinador aprueba
- **WHEN** un coordinador aprueba una solicitud pendiente con una nota
- **THEN** la solicitud queda aprobada, con esa nota y con el coordinador como revisor

#### Scenario: El solicitante no aprueba
- **WHEN** el solicitante de la reserva intenta aprobarla
- **THEN** el sistema rechaza la acción por falta de permiso y la solicitud sigue pendiente

#### Scenario: Nota de aprobación vacía
- **WHEN** un coordinador aprueba sin nota
- **THEN** el sistema rechaza la acción y la solicitud sigue pendiente

#### Scenario: Aprobar una solicitud que no está pendiente
- **WHEN** un coordinador intenta aprobar una solicitud rechazada, cancelada o ya aprobada
- **THEN** el sistema rechaza la acción y no cambia el estado

### Requirement: Rechazo de solicitud pendiente
El sistema SHALL pasar una solicitud pendiente a rechazada cuando un coordinador o un administrador envía una nota, y SHALL liberar el intervalo para una solicitud nueva.

#### Scenario: Rechazo con nota
- **WHEN** un administrador rechaza una solicitud pendiente con una nota
- **THEN** la solicitud queda rechazada, con esa nota y con el administrador como revisor

#### Scenario: El intervalo queda libre tras el rechazo
- **WHEN** una solicitud pendiente de E de 08:00 a 10:00 es rechazada y otro solicitante pide E en ese intervalo
- **THEN** el sistema acepta la nueva solicitud en estado pendiente

### Requirement: Cancelación sin borrar
El sistema SHALL cancelar una reserva pendiente o aprobada sin eliminarla, si la cancela su solicitante, un coordinador o un administrador.

#### Scenario: El solicitante cancela la suya
- **WHEN** el solicitante cancela su reserva aprobada
- **THEN** la reserva queda cancelada y sigue consultable en su historial

#### Scenario: El solicitante no cancela la de otro
- **WHEN** un solicitante intenta cancelar una reserva pendiente de otra persona
- **THEN** el sistema rechaza la acción y la reserva sigue pendiente

#### Scenario: Un administrador cancela una reserva ajena
- **WHEN** un administrador cancela una reserva aprobada de un solicitante
- **THEN** la reserva queda cancelada y el intervalo deja de figurar como ocupado

#### Scenario: No se cancela una reserva cerrada
- **WHEN** un coordinador intenta cancelar una reserva rechazada o ya cancelada
- **THEN** el sistema rechaza la acción y el estado no cambia

### Requirement: Historial según el rol
El sistema SHALL mostrar al solicitante solo sus reservas, de cualquier estado, y SHALL mostrar a coordinador y administrador las de todos los solicitantes.

#### Scenario: El solicitante no ve reservas ajenas
- **WHEN** un solicitante consulta el historial y existe una reserva de otra persona
- **THEN** la respuesta no incluye esa reserva

#### Scenario: El coordinador ve todos los estados
- **WHEN** un coordinador consulta el historial y existen reservas pendientes, aprobadas, rechazadas y canceladas
- **THEN** la respuesta incluye las cuatro

#### Scenario: Filtro por estado
- **WHEN** un administrador consulta el historial filtrando por estado cancelada
- **THEN** la respuesta solo incluye reservas canceladas
