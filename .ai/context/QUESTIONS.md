# Preguntas abiertas

## Q-001 — Evidencia del paquete Forza

- **Estado:** abierta
- **Pregunta:** ¿Qué captura reproducible confirma cada offset, tamaño y unidad del paquete `Car Dash` de Forza Motorsport (2023)?
- **Impacto:** bloquea declarar estable el driver y contrato v1.
- **Siguiente evidencia:** fixture binario autorizado más tabla de valores observados.

## Q-002 — Cadencia y ausencia de datos

- **Estado:** abierta
- **Pregunta:** ¿Qué umbral de silencio distingue una conexión perdida de una pausa normal del juego?

## Q-003 — Historial y límites

- **Estado:** resuelta
- **Decisión:** el core entrega frames; cada módulo limita su historial visual. Persistencia futura guarda paquetes crudos y metadatos.

## Q-004 — Datos de rueda

- **Estado:** abierta
- **Pregunta:** ¿La unidad de `WheelRotSpeed` es rad/s en las situaciones relevantes y cómo se comporta AWD?

## Q-005 — API WebSocket

- **Estado:** abierta
- **Pregunta:** ¿Qué envolvente y versión se publicarán a clientes y cómo se negocian cambios compatibles?
