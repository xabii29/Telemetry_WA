# Changelog

## [Sin publicar]

### Documentación

- Consolidada la arquitectura, reglas para agentes, roadmap, backlog y contratos iniciales.
- Normalizada la estructura de pruebas a tests/.
- El protocolo y los drivers se marcan como pendientes de evidencia para evitar implementar supuestos como hechos.
- Declarado `legacy/` como referencia de solo lectura validada para Forza Motorsport (2023), con su trazabilidad documentada fuera de la nueva implementación.
- Añadidos el registro de decisiones y el inventario de referencia histórica.
- Añadido `docs/LEGACY_FINDINGS.md` con los comportamientos conservados, límites de confianza y el desglose de módulos.

### Código

- Añadido el esqueleto de backend: modelo normalizado, límite de driver, receptor UDP y eventos de sesión.
- Añadido un driver experimental de Forza Motorsport (2023) cubierto por paquetes sintéticos.
- Añadido TelemetryBus de navegador y esqueletos aislados de Connection y Vehicle.
- Añadidos roles de IA y contexto en `.ai/`.
