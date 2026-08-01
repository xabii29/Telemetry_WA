# Registro de decisiones arquitectónicas

Registra aquí decisiones que afecten contratos, compatibilidad, tecnologías o límites entre capas. Cada entrada debe indicar evidencia, consecuencias y fecha; no reemplaza los contratos en `docs/`.

## ADR-001 — Separar la referencia histórica de la nueva implementación

- **Estado:** Aceptada
- **Fecha:** 2026-07-31
- **Contexto:** El repositorio conserva implementaciones y resultados previamente validados para Forza Motorsport (2023).
- **Decisión:** `legacy/` se mantiene estrictamente de solo lectura y se usa únicamente como referencia. La nueva arquitectura se implementa desde cero en sus directorios definidos.
- **Consecuencias:** Los resultados pueden contrastarse con el legado, pero toda funcionalidad, prueba y documentación nueva vive fuera de `legacy/`. No se copian estructuras ni dependencias heredadas.

## ADR-002 — Primer corte vertical: Forza UDP y módulos independientes

- **Estado:** Aceptada
- **Fecha:** 2026-07-31
- **Contexto:** El producto debe empezar a producir código sin diseñar un framework genérico antes de comprobar módulos reales.
- **Decisión:** El primer corte implementa Forza Motorsport (2023) sobre UDP, un frame normalizado mínimo, eventos de sesión y módulos web que solo hablan con `TelemetryBus`. Quedan fuera APIs externas y memoria.
- **Evidencia:** `legacy/Forza Motorsport 2023/` preserva comportamientos para cambio de coche, dyno, pedales, trazado y transmisión; inventariados en `docs/LEGACY_FINDINGS.md`.
- **Consecuencias:** La decodificación y offsets siguen siendo experimentales hasta añadir una captura trazable. Los módulos se construyen por necesidad observable, no por una taxonomía especulativa.

## Plantilla

    ## ADR-NNN — Título
    - **Estado:** Propuesta | Aceptada | Reemplazada | Rechazada
    - **Fecha:** AAAA-MM-DD
    - **Contexto:**
    - **Decisión:**
    - **Evidencia:**
    - **Consecuencias:**
