# Race Telemetry Framework

Framework local, modular y extensible para adquirir, normalizar y visualizar telemetría de videojuegos de carreras en tiempo real.

El primer objetivo es Forza Motorsport (2023); el diseño no debe asumir que será el único juego compatible.

## Estado

Pre-alfa. La arquitectura y las reglas de colaboración están definidas; aún no hay implementación.

## Arquitectura

UDP → Driver → TelemetryPacket → backend → WebSocket → TelemetryBus → módulos de UI

El backend adquiere, normaliza, persiste datos crudos y distribuye. El frontend procesa y visualiza; sus módulos no se comunican entre sí.

## Tecnologías acordadas

- Backend: Python y FastAPI.
- Frontend: HTML, CSS y JavaScript vanilla con ES modules.
- Gráficas: Plotly.js cuando sea necesario.
- Comunicación: WebSocket.

No introducir React, Angular, Vue, Electron, Node, TypeScript, Bootstrap, Tailwind ni otro framework SPA sin una decisión arquitectónica documentada.

## Empezar a trabajar

1. Lee AGENTS.md.
2. Lee ARCHITECTURE.md y el contrato relevante en docs/.
3. Toma una tarea de TODO.md o .ai/issues/.
4. Trabaja solo dentro de los archivos autorizados por esa tarea.
5. Actualiza documentación, changelog y handoff antes de finalizar.

## Documentación

- Arquitectura: ARCHITECTURE.md
- Reglas de agentes: AGENTS.md
- Roadmap: ROADMAP.md
- Tareas: TODO.md
- Contrato de telemetría: docs/PROTOCOL.md
- Drivers: docs/DRIVERS.md
- Módulos: docs/MODULES.md
- Handoff: docs/HANDOFF.md

## Estructura

    backend/       Adquisición UDP, drivers, sesiones, persistencia y API
    frontend/      Dashboard web y módulos de visualización
    docs/          Contratos técnicos y documentación mantenida
    tests/         Pruebas automatizadas
    .ai/           Issues, prompts, revisiones y handoffs para IA
