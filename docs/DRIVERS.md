# Drivers

Un driver es el único adaptador que conoce el protocolo de telemetría de un juego. Su salida es siempre un TelemetryPacket versionado.

## Contrato conceptual

    class Driver:
        game_id: str
        protocol_version: str
        def probe(self, datagram: bytes) -> bool: ...
        def decode(self, datagram: bytes) -> TelemetryPacket: ...

Las firmas definitivas se fijarán con el esquema de TelemetryPacket.

## Reglas

- Un driver no importa frontend ni módulos de UI.
- probe no tiene efectos secundarios y debe ser económico.
- decode valida tamaño, versión y límites antes de producir datos.
- Los valores conservan fuente y unidades hasta normalizarlos explícitamente.
- Datos desconocidos, inválidos o ausentes se señalan; no se fabrican.
- Cada implementación se prueba con datagramas capturados y autorizados.

## Registro

| Juego | Estado | Evidencia |
| --- | --- | --- |
| Forza Motorsport (2023) | Planeado | Pendiente de confirmar. |
| Forza Horizon 5 | Futuro | No investigado. |
| Forza Motorsport 7 | Futuro | No investigado. |
| Assetto Corsa | Futuro | No investigado. |
| Assetto Corsa Competizione | Futuro | No investigado. |
| BeamNG.drive | Futuro | No investigado. |
