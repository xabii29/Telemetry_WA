# Handoff actual

## Estado

El proyecto está en pre-alfa. Existe un primer corte vertical experimental: modelo de paquete, adaptador Forza, seguimiento de sesión, recepción UDP y bus web. No se considera todavía un dashboard funcional.

## Decisiones vigentes

- Python/FastAPI en backend; HTML, CSS y JavaScript vanilla en frontend.
- Drivers independientes normalizan telemetría nativa a TelemetryPacket.
- Backend: adquisición, sesiones, persistencia de datos crudos y distribución.
- Frontend: TelemetryBus, análisis y visualización mediante módulos aislados.
- La especificación binaria y las unidades aún requieren muestras trazables; el driver inicial está cubierto solo por pruebas sintéticas.
- `legacy/` es referencia estrictamente de solo lectura: contiene implementaciones y resultados validados para Forza Motorsport (2023), pero no es una dependencia ni una base para copiar código.

## Próximo paso recomendado

Obtener una captura UDP autorizada de Forza Motorsport (2023), crear un fixture, comparar sus valores contra el juego y convertir `docs/PROTOCOL.md` en contrato v1. En paralelo, implementar Inputs y Motion sobre `packet` sin acoplar módulos.

## Verificación realizada

Revisión del legado y pruebas de decodificación sintética, cambio de coche y sintaxis JavaScript. Falta verificación con UDP real.
