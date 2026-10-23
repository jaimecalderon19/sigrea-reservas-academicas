# Tasks

## 1. Decisiones

- [x] 1.1 Implementar aprobar y rechazar desde pendiente, con nota, solo coordinador o administrador, revalidando el cruce al aprobar. Verificar los escenarios de permiso, nota vacía y estado que no está pendiente.
- [x] 1.2 Implementar cancelar sin borrar, por el solicitante dueño o por coordinador y administrador, y liberar el cupo. Verificar que el solicitante no cancela la ajena y que una cancelada deja de figurar como ocupada.

## 2. Historial

- [x] 2.1 Implementar el listado filtrable. Verificar que el solicitante no ve ajenas, que el coordinador ve los cuatro estados y que el filtro por cancelada no mezcla otros estados.
- [x] 2.2 Verificar el escenario de liberación tras el rechazo con la suite de `ciclo-reserva` en verde, junto con la suite ya existente de solicitud.
