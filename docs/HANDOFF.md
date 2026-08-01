# Handoff actual

## Estado

El proyecto está en pre-alfa. Se definieron límites de capas, reglas de colaboración y una secuencia de trabajo; aún no hay implementación de producto.

## Decisiones vigentes

- Python/FastAPI en backend; HTML, CSS y JavaScript vanilla en frontend.
- Drivers independientes normalizan telemetría nativa a TelemetryPacket.
- Backend: adquisición, sesiones, persistencia de datos crudos y distribución.
- Frontend: TelemetryBus, análisis y visualización mediante módulos aislados.
- Los contratos aún no contienen especificación binaria ni unidades confirmadas.

## Próximo paso recomendado

Completar Issue 001: reunir fuente verificable o muestras reales de UDP de Forza Motorsport (2023) y convertir el borrador de docs/PROTOCOL.md en un contrato v1 con campos, unidades y eventos precisos.

## Verificación realizada

Revisión documental y de estructura. No hay código ejecutable ni pruebas aún.
