# 001 — Especificar el protocolo interno v1

## Objetivo

Definir el contrato v1 entre el driver de Forza Motorsport (2023), el backend y el frontend a partir de evidencia verificable del protocolo UDP.

## Contexto

El driver traduce datagramas nativos a TelemetryPacket. Los módulos del frontend solo consumen el contrato interno. Consultar ARCHITECTURE.md y docs/PROTOCOL.md.

## Archivos autorizados

- docs/PROTOCOL.md
- docs/DRIVERS.md
- tests/fixtures/ (solo muestras autorizadas y sin datos sensibles)
- tests/
- docs/CHANGELOG.md
- docs/HANDOFF.md
- TODO.md

## Fuera de alcance

- Implementar receptor UDP, driver, backend o frontend.
- Diseñar módulos de visualización.

## Criterios de aceptación

- Cada campo de TelemetryPacket indica tipo, unidad, opcionalidad, fuente y semántica.
- El contrato define envolvente y carga útil de eventos WebSocket.
- Se documentan versión, compatibilidad y representación de datos ausentes.
- Los supuestos no confirmados quedan fuera del contrato o marcados con plan de validación.
- Las conclusiones se apoyan en documentación o muestras identificables.

## Verificación requerida

Revisión de consistencia entre protocolo, contrato de driver y ejemplo de datos; no se acepta una verificación basada solo en intuición.

## Dependencias / bloqueos

Documentación fiable o capturas de paquetes de Forza Motorsport (2023).
