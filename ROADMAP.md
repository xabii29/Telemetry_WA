# Roadmap

## Fase 0 — Fundación

- [x] Estructura documental y reglas de trabajo.
- [ ] Confirmar fuente de telemetría, versión y muestras del primer juego.
- [ ] Crear registro de decisiones para cambios arquitectónicos irreversibles.

## Fase 1 — Contrato de datos

- [ ] Especificar TelemetryPacket v1: campos, unidades, opcionalidad, precisión y compatibilidad.
- [ ] Especificar eventos WebSocket y semántica de sesión.
- [ ] Definir contrato de Driver y detección de protocolo.

## Fase 2 — Flujo mínimo vertical

- [ ] Receptor UDP con límites de buffer, errores y ciclo de vida.
- [ ] Driver de Forza Motorsport (2023) respaldado por muestras reales.
- [ ] Distribución de TelemetryPacket a cliente WebSocket.
- [ ] Dashboard que conecte, publique al bus y muestre diagnóstico.
- [ ] Pruebas con paquetes grabados y conexión/desconexión.

## Fase 3 — Sesiones y módulos iniciales

- [ ] Persistencia de datos crudos y metadatos de sesión.
- [ ] Módulo de pedales y módulo de trazado de pista.
- [ ] Límites de rendimiento y memoria para sesiones prolongadas.

## Fase 4 — Análisis y expansión

- [ ] Dyno, transmisión, suspensión, neumáticos y temperaturas como módulos independientes.
- [ ] Segundo driver de juego.

## Futuro: plataforma

- [ ] Evaluar Android con servidor local embebido y WebView, reutilizando frontend y contrato.
