# Arquitectura

RTF recibe telemetría de juegos de carreras, la normaliza a un contrato común y la visualiza en un dashboard web. El primer driver será Forza Motorsport (2023), sin acoplar el sistema a ese juego.

## Flujo y límites

    Juego --UDP--> receptor --bytes--> driver --TelemetryPacket--> backend
                                                                  |
                                                             WebSocket
                                                                  |
                                                            TelemetryBus
                                                                  |
                                                       módulos de UI aislados

| Capa | Responsabilidad | No debe hacer |
| --- | --- | --- |
| backend/ | UDP, drivers, sesiones, datos crudos y distribución. | Dyno, trazados, estadísticas o renderizado. |
| backend/drivers/ | Traducir protocolo nativo a TelemetryPacket. | Conocer UI o módulos. |
| frontend/ | WebSocket, TelemetryBus, procesamiento y renderizado. | Decodificar paquetes nativos. |
| frontend/modules/ | Consumir eventos y presentar una capacidad. | Importar o modificar otro módulo. |
| tests/ | Validar contratos y comportamiento observable. | Lógica de producción. |

## Contratos obligatorios

- Cada driver emite exclusivamente TelemetryPacket; ver docs/PROTOCOL.md.
- La compatibilidad usa campos opcionales y versiones; nunca cambia silenciosamente el significado de un campo.
- El backend añade metadatos de transporte pero no modifica las medidas normalizadas del driver.
- El frontend publica eventos WebSocket al TelemetryBus. No existe comunicación directa entre módulos.
- La persistencia contiene datos crudos y metadatos reproducibles; nunca gráficos ni resultados derivados.

Eventos iniciales: packet, session_started, session_saved, car_changed, connection_lost y connection_restored. Su carga útil se define antes de escribir código.

## Rendimiento

- Medir antes de optimizar.
- Evitar copias, serializaciones y asignaciones innecesarias en la ruta de paquetes.
- Usar buffers acotados y procesamiento incremental.
- Usar requestAnimationFrame, Web Workers o actualizaciones incrementales de Plotly solo cuando una medición lo justifique.

## Estructura

    backend/api/       API HTTP y WebSocket
    backend/drivers/   Adaptadores por juego
    backend/telemetry/ UDP, normalización, bus y sesiones
    backend/storage/   Persistencia de datos crudos
    frontend/          Dashboard y módulos
    docs/              Especificaciones y registros
    tests/             Pruebas automatizadas
    .ai/               Artefactos de coordinación
