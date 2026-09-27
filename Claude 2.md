# Instrucciones para la reestructuración de la Web App

## Objetivo

El objetivo de este proyecto no es únicamente modificar el código existente, sino realizar una reestructuración completa de la aplicación para obtener una arquitectura limpia, modular, mantenible y preparada para futuras expansiones.

Toda decisión de diseño deberá priorizar, en este orden:

1. Modularidad.
2. Bajo acoplamiento entre componentes.
3. Alta cohesión dentro de cada módulo.
4. Facilidad de mantenimiento.
5. Rendimiento.
6. Escalabilidad.
7. Legibilidad del código.

No existe obligación de conservar la implementación actual si encuentras una solución significativamente mejor.

La funcionalidad existente debe mantenerse, pero la implementación interna puede modificarse completamente cuando represente una mejora arquitectónica.

---

## Forma de trabajo

Antes de modificar cualquier archivo:

- Analiza la estructura completa del proyecto.
- Identifica responsabilidades de cada archivo.
- Detecta código duplicado.
- Detecta responsabilidades mezcladas.
- Detecta posibles cuellos de botella.
- Detecta dependencias innecesarias.
- Identifica qué partes pueden reutilizarse.

Una vez entendido el proyecto, comienza la implementación.

No implementes soluciones temporales.

Evita añadir complejidad innecesaria.

Cada cambio debe mejorar la arquitectura general del proyecto.

---

## Principios de diseño

Cada archivo debe tener una única responsabilidad.

Evita que un mismo archivo:

- reciba información
- procese datos
- realice cálculos
- dibuje gráficos
- controle la interfaz
- almacene información

Cada responsabilidad pertenece al módulo correspondiente.

El flujo esperado debe mantenerse conceptualmente como:

UDP
→ Decodificación
→ Normalización de datos
→ WebSocket
→ Procesamiento por módulo
→ Visualización

Los módulos no deben depender directamente entre sí.

Toda comunicación deberá realizarse mediante estructuras de datos estandarizadas.

Si encuentras funciones reutilizables entre módulos, extráelas a un archivo común.

Evita duplicación de código.

---

## Archivos disponibles

Se te comparten una serie de archivos que componen una suite de módulos de telemetría.

El objetivo es lograr una estandarización de los datos de entrada de cada módulo.

Cada módulo debe ser completamente independiente de los demás.

---

## Reestructuración requerida

## Servidor

El archivo correspondiente al servidor únicamente debe:

- recibir el paquete UDP
- descifrar la información
- normalizar los datos
- enviarlos mediante WebSocket

No debe contener lógica de presentación.

No debe contener cálculos propios de los módulos.

---

## Frontend

El layout HTML y CSS debe conservar:

- colores
- distribución
- apariencia
- experiencia visual

La reorganización interna del código JavaScript puede modificarse completamente.

---

## JavaScript

El archivo `app.js` debe dividirse en múltiples archivos.

Cada módulo tendrá su propio archivo independiente.

Ejemplo:

- dyno.js
- pedales.js
- velocidades.js
- mapa.js
- suspensión.js
- etc.

Cada módulo será responsable únicamente de su propia lógica.

---

## Pipeline de procesamiento

Los archivos existentes sirven como referencia para obtener los parámetros necesarios para los cálculos.

Puedes modificar completamente la implementación interna del procesamiento siempre que:

- la funcionalidad se conserve o mejore
- la arquitectura sea más limpia
- el rendimiento sea superior

El flujo deseado continúa siendo:

Recepción UDP
→ Decodificación
→ Normalización
→ Procesamiento
→ Visualización

---

## Motor gráfico

Actualmente el proyecto utiliza Plotly.

Su rendimiento resulta insuficiente.

Migra el proyecto a una alternativa más ligera como:

- uPlot (preferido)
- Chart.js

Siempre que la funcionalidad pueda mantenerse.

---

## Funcionalidades específicas

## Dyno

Agregar en la barra de datos:

- RPM mínimas
- RPM máximas

Si estos valores no existen en el paquete UDP, utilizar los mínimos y máximos observados mediante `CurrentEngineRPM`.

---

## Estandarización de datos

Al finalizar, generar un documento donde se describa la estructura estandarizada utilizada.

Considera que posteriormente existirá un módulo llamado **Source**.

Este módulo será responsable de adaptar distintas fuentes de telemetría.

Ejemplo:

Forza Motorsport

CarOrdinal

↓

CarID

Need For Speed

CarNumber

↓

CarID

Los módulos nunca deberán depender del nombre específico utilizado por una fuente de datos.

Siempre deberán consumir la estructura estandarizada.

---

## Velocidades

Ya existen herramientas de validación para esta sección.

Utilízalas cuando sea posible.

Cuando el sistema alcance una alta certeza sobre los parámetros calculados (por ejemplo diámetro de rueda), estos deberán actualizar automáticamente la información mostrada.

Dividir la pestaña de velocidades en dos columnas.

La columna izquierda debe conservar el comportamiento actual.

Agregar botones de ajuste fino junto a cada slider.

Mantener la combinación de colores del layout existente.

---

## Potencia

Actualizar automáticamente el valor:

max_hp@rpm

utilizando la información derivada del paquete UDP y de los módulos de cálculo disponibles.

Evitar la captura manual cuando sea posible.

---

## Home

Mantener:

- Dyno
- Mapeo de pista

Únicamente cambiar el motor gráfico utilizado.

---

## Pedales

Actualmente la gráfica presenta cortes.

Implementar un buffer circular.

Se recomienda:

- mantener aproximadamente 600 muestras
- insertar una nueva
- eliminar la más antigua

No almacenar información indefinidamente.

---

## Mapeo de pista

Mantener únicamente:

- verde
- rojo

Eliminar el color gris.

El vehículo deberá mostrarse mediante un punto amarillo.

Si el historial de posiciones se almacena:

- guardar por vuelta
- mostrar únicamente:
  - vuelta actual
  - vuelta anterior

Nunca mostrar más de dos vueltas simultáneamente.

---

## Suspensión

Actualmente este módulo no existe.

Si identificas una funcionalidad útil relacionada con los datos disponibles, puedes implementarla.

Documenta la propuesta en un archivo:

Ideas.md

explicando:

- propósito
- funcionamiento
- posibles mejoras futuras

---

## Guardado

Modificar la estrategia actual.

Al seleccionar Guardar deberán existir dos opciones:

**Guardado por default**

Mantener el comportamiento actual.

Mostrar la ruta donde fueron almacenados los archivos.

**Guardado personalizado**

Permitir seleccionar la carpeta base mediante un cuadro de diálogo estándar del sistema operativo.

A partir de dicha carpeta deberán generarse automáticamente las subcarpetas necesarias utilizando la misma estructura actual.

---

## Ambigüedades

Avanza de manera autónoma.

Únicamente solicita aclaraciones cuando exista una ambigüedad que impida continuar correctamente.

No detengas el desarrollo por decisiones menores de implementación.

---

## Restricciones

No inventes información que no exista en los archivos proporcionados.

No agregues funcionalidades que requieran datos inexistentes.

Si una mejora requiere información que actualmente no está disponible:

- documenta la propuesta
- no la implementes

---

## Entregables esperados

Al finalizar deberán existir, como mínimo:

- servidor Python
- index.html
- styles.css
- un archivo JavaScript independiente por cada módulo
- documento de estandarización de datos
- Ideas.md (si se implementa el módulo de suspensión)

Los módulos JavaScript deben ser independientes entre sí y compartir únicamente la estructura de datos estandarizada.

---

## Criterios de calidad

Durante todo el desarrollo prioriza:

- arquitectura limpia
- modularidad
- simplicidad
- reutilización de código
- bajo acoplamiento
- alta cohesión
- facilidad de mantenimiento
- rendimiento
- escalabilidad

No optimices únicamente para que el proyecto funcione hoy.

Diseña una arquitectura que facilite la incorporación futura de nuevas fuentes de telemetría, nuevos módulos y nuevas funcionalidades sin requerir una reestructuración importante.
