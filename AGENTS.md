# Guía de colaboración para agentes

## Antes de cambiar archivos

Lee, en este orden:

1. AGENTS.md
2. ARCHITECTURE.md
3. La tarea asignada en TODO.md o .ai/issues/
4. Los contratos relevantes en docs/
5. docs/HANDOFF.md y el changelog reciente

Si la tarea no define objetivo, archivos autorizados y criterios de aceptación, no programes: completa o solicita esa definición.

## Reglas de trabajo

- Una tarea por cambio. No mezclar refactorizaciones ajenas a la tarea.
- Respeta los límites de archivos de la tarea. Ampliarlos exige justificación en la tarea y el handoff.
- No inventes formatos, unidades, paquetes de juego, valores físicos ni comportamientos sin fuente, prueba o decisión documentada.
- No adaptes la arquitectura al código histórico.
- No agregues dependencias o frameworks no aprobados.
- No cambies contratos públicos sin actualizar protocolo, pruebas y plan de compatibilidad.
- No borres datos del usuario, sesiones o artefactos sin autorización explícita.

## Límites por rol

| Rol | Alcance | No hace |
| --- | --- | --- |
| Arquitectura / QA | Diseño, contratos, riesgos, rendimiento, revisión y pruebas. | Módulos completos sin tarea explícita. |
| Backend | backend/, pruebas relacionadas y documentos afectados. | Lógica de visualización. |
| Frontend | frontend/, pruebas relacionadas y documentos afectados. | Decodificación de protocolos nativos. |
| Documentación | docs/, documentos raíz y .ai/. | Cambios de comportamiento de producción. |

Un agente toca varios ámbitos solo cuando la tarea lo autorice.

## Definición de terminado

1. Cumple criterios de aceptación.
2. Ejecutó verificaciones aplicables y registró resultados.
3. Actualizó contratos y documentación afectados.
4. Añadió una entrada al changelog.
5. Actualizó el handoff con el estado real y siguiente paso.

## Plantilla de tarea

    # NNN — Título
    ## Objetivo
    ## Contexto y decisiones existentes
    ## Archivos autorizados
    ## Fuera de alcance
    ## Criterios de aceptación
    ## Verificación requerida
    ## Dependencias / bloqueos

## Entrega

Reporta cambios, decisiones, verificaciones, resultados, riesgos y pendientes. No afirmes que algo está probado si no ejecutaste una verificación.

## Uso del directorio legacy/

El directorio `legacy/` es material de referencia **estrictamente de solo lectura**. Contiene implementaciones y resultados previamente validados para Forza Motorsport (2023); no forma parte del producto nuevo ni de su superficie de mantenimiento.

Estos archivos constituyen evidencia técnica que puede consultarse para validar:

- Decodificación del protocolo UDP.
- Algoritmos ya comprobados.
- Lógica de módulos existentes.
- Comportamiento esperado del sistema.

### Restricciones

El código, datos y resultados contenidos en `legacy/` NO forman parte de la nueva arquitectura. Ninguna tarea autoriza cambios dentro de ese directorio, salvo una tarea documental explícita aprobada para preservar o corregir su inventario.

Está prohibido:

- Crear, editar, mover, renombrar o eliminar archivos en `legacy/`.
- Copiar archivos completos.
- Adaptar la arquitectura al código legacy.
- Reproducir dependencias del proyecto anterior.
- Mantener estructuras heredadas por compatibilidad.

Está permitido:

- Consultar algoritmos.
- Verificar fórmulas.
- Comparar resultados.
- Validar el comportamiento esperado.
- Extraer únicamente la lógica necesaria para una nueva implementación.

Toda funcionalidad incorporada al nuevo sistema deberá implementarse nuevamente, fuera de `legacy/`, respetando la arquitectura definida en ARCHITECTURE.md. Cuando se use la referencia para una decisión, registrar qué comportamiento o resultado se comparó y conservar la nueva evidencia en `tests/` o `docs/`.

El objetivo es preservar el conocimiento adquirido, no reutilizar la estructura del proyecto anterior.
