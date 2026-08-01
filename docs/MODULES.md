# Módulos de frontend

Un módulo es una unidad de visualización o análisis del navegador. Consume eventos del TelemetryBus y mantiene su propio estado. No llama ni importa otros módulos directamente.

## Contrato mínimo

Cada módulo declara eventos consumidos, campos requeridos y unidades, salida visible, límites de memoria, comportamiento ante datos ausentes y datos de validación.

## Rendimiento

- Actualizar UI en una cadencia visual razonable, no necesariamente por paquete.
- Limitar series y buffers.
- Usar procesamiento incremental; un Web Worker necesita justificación medida.
- Plotly se actualiza incrementalmente cuando corresponda.

## Módulos derivados de la referencia validada

| Módulo | Estado | Contrato requerido |
| --- | --- | --- |
| Diagnóstico de conexión | Esqueleto | Eventos de transporte. |
| Vehículo | Esqueleto | Identidad, clase, PI y tracción. |
| Pedales | Siguiente | Controles normalizados. |
| Movimiento | Siguiente | Velocidad, posición y velocidad vectorial. |
| Pista | Siguiente | Posición X/Z, controles y sesión. |
| Motor | Siguiente | RPM, potencia, torque, boost y combustible. |
| Dyno | Siguiente | Motor, controles y vehículo; no es responsabilidad del backend. |
| Sesión | Siguiente | Vuelta, posición, distancia y tiempos confirmados. |
| Transmisión | Investigación | Motor, ruedas, embrague y tracción. |
| Suspensión / neumáticos | Futuro | Chasis. |

El detalle y trazabilidad están en `docs/LEGACY_FINDINGS.md`.
