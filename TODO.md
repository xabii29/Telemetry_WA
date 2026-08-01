# Tareas activas

Este archivo contiene solo trabajo pendiente o bloqueado. Las tareas grandes se detallan en .ai/issues/.

| ID | Prioridad | Estado | Dependencias | Archivos previstos | Resultado |
| --- | --- | --- | --- | --- | --- |
| 001 | P0 | Pendiente | Muestras y especificación UDP de Forza Motorsport (2023) | docs/PROTOCOL.md, docs/DRIVERS.md, .ai/issues/001-protocolo-interno.md | Contrato interno v1, sin campos inventados. |
| 002 | P0 | Bloqueada por 001 | Issue 001 | backend/drivers/, backend/telemetry/, tests/ | Pipeline UDP a TelemetryPacket con muestras reales. |
| 003 | P0 | Bloqueada por 001 y 002 | Issues 001–002 | backend/api/, frontend/js/, tests/ | Evento packet por WebSocket y publicado al bus. |
| 004 | P1 | Bloqueada por 003 | Issue 003 | frontend/modules/, frontend/plot/, tests/ | Módulos iniciales de pedales y pista. |

Estados válidos: Pendiente, En curso, Bloqueada, En revisión y Terminada. Al terminar una tarea, muévela al changelog y actualiza el roadmap.
