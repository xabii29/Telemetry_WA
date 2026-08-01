# Convenciones

## Documentación

- Usar UTF-8 y español técnico claro.
- Los documentos de contrato usan UPPER_SNAKE_CASE.md; nombres nuevos no canónicos usan kebab-case.
- Indicar si una decisión es confirmada, borrador o pendiente.
- Enlazar contratos en lugar de duplicarlos.

## Código

- Python: snake_case, tipos cuando aclaren el contrato y módulos pequeños.
- JavaScript: ES modules, camelCase y sin estado global implícito.
- HTML/CSS: estructura, presentación y comportamiento separados.
- Unidades y conversiones se nombran y documentan en el borde del driver.

## Cambios

- Un cambio debe tener propósito verificable.
- No incluir credenciales, archivos de sesión o capturas privadas sin autorización.
- Actualizar contratos, pruebas, changelog y handoff cuando cambie el comportamiento observable.
