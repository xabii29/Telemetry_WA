# Protocolo interno

## Estado

**Pendiente de especificación.** No implementar ni asumir la forma binaria de Forza Motorsport (2023) hasta contar con documentación oficial o capturas de paquetes reales trazables.

## Objetivo

    datagrama nativo → Driver → TelemetryPacket → WebSocket → TelemetryBus

## Reglas

- Cada campo debe documentar tipo, unidad SI o convención explícita, rango, nulabilidad y fuente.
- Un campo ausente se representa explícitamente; no se reemplaza por cero salvo que cero sea una medición válida documentada.
- Las adiciones compatibles son opcionales. Renombrar, cambiar unidades o semántica exige una versión nueva.
- Los eventos de transporte se separan de mediciones.

## TelemetryPacket v1 — borrador

Es un inventario de candidatos, no autorización para inventar datos.

| Grupo | Campos candidatos |
| --- | --- |
| Identidad | timestamp, frame, game_id, car_id |
| Movimiento | speed, position, orientation, velocity, acceleration, angular_velocity |
| Motor y transmisión | rpm, gear, power, torque, boost |
| Controles | throttle, brake, clutch, handbrake, steering |
| Chasis | suspension, tires, temperatures |

## Eventos — borrador

packet, session_started, session_saved, car_changed, connection_lost y connection_restored.

La forma exacta de cada carga útil sigue pendiente del Issue 001.
