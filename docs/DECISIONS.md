# Registro de decisiones arquitectónicas

Registra aquí decisiones que afecten contratos, compatibilidad, tecnologías o límites entre capas. Cada entrada debe indicar evidencia, consecuencias y fecha; no reemplaza los contratos en `docs/`.

## ADR-001 — Separar la referencia histórica de la nueva implementación

- **Estado:** Aceptada
- **Fecha:** 2026-07-31
- **Contexto:** El repositorio conserva implementaciones y resultados previamente validados para Forza Motorsport (2023).
- **Decisión:** `legacy/` se mantiene estrictamente de solo lectura y se usa únicamente como referencia. La nueva arquitectura se implementa desde cero en sus directorios definidos.
- **Consecuencias:** Los resultados pueden contrastarse con el legado, pero toda funcionalidad, prueba y documentación nueva vive fuera de `legacy/`. No se copian estructuras ni dependencias heredadas.

## Plantilla

    ## ADR-NNN — Título
    - **Estado:** Propuesta | Aceptada | Reemplazada | Rechazada
    - **Fecha:** AAAA-MM-DD
    - **Contexto:**
    - **Decisión:**
    - **Evidencia:**
    - **Consecuencias:**
