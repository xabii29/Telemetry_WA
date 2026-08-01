# Módulos de frontend

Un módulo es una unidad de visualización o análisis del navegador. Consume eventos del TelemetryBus y mantiene su propio estado. No llama ni importa otros módulos directamente.

## Contrato mínimo

Cada módulo declara eventos consumidos, campos requeridos y unidades, salida visible, límites de memoria, comportamiento ante datos ausentes y datos de validación.

## Rendimiento

- Actualizar UI en una cadencia visual razonable, no necesariamente por paquete.
- Limitar series y buffers.
- Usar procesamiento incremental; un Web Worker necesita justificación medida.
- Plotly se actualiza incrementalmente cuando corresponda.

## Módulos planeados

| Módulo | Estado | Contrato requerido |
| --- | --- | --- |
| Diagnóstico de conexión | Planeado | Eventos de transporte. |
| Pedales | Planeado | Controles. |
| Pista | Planeado | Posición y sesión. |
| Dyno | Futuro | Motor, transmisión y evidencia física. |
| Transmisión | Futuro | Motor y transmisión. |
| Suspensión | Futuro | Chasis. |
| Neumáticos / temperaturas | Futuro | Chasis. |
