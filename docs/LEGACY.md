# Referencia histórica

## Estado y alcance

`legacy/Forza Motorsport 2023/` conserva el sistema anterior y resultados de validación para Forza Motorsport (2023). Es evidencia histórica y material de consulta; no pertenece a la arquitectura actual ni a la distribución del producto.

El directorio es **estrictamente de solo lectura**. No se crean, editan, mueven, renombran ni eliminan archivos dentro de `legacy/` durante el trabajo normal.

## Uso permitido

- Comparar resultados y comportamiento observable.
- Consultar algoritmos, fórmulas, nombres de señales y supuestos que deban volver a validarse.
- Identificar datos que justifiquen nuevas muestras o pruebas reproducibles.

## Uso no permitido

- Copiar implementaciones completas o trasladar su estructura y dependencias.
- Convertir su comportamiento en contrato sin evidencia o pruebas nuevas trazables.
- Hacer que componentes de `backend/`, `frontend/` o `tests/` dependan de rutas o archivos de `legacy/`.

## Trazabilidad requerida

Una implementación nueva que se haya contrastado con esta referencia debe documentar: el archivo o resultado consultado, el comportamiento comparado, la evidencia nueva obtenida y la prueba que lo verifica. La evidencia nueva vive en `tests/` o `docs/`, nunca en `legacy/`.

Para las reglas completas de colaboración, ver `AGENTS.md`.
