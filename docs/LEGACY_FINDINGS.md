# Hallazgos validados del legado de Forza Motorsport (2023)

## Propósito

Este documento registra comportamiento observable consultado en `legacy/` que debe conservarse como requisito del producto nuevo. No convierte al código histórico en dependencia ni copia su arquitectura. Cada punto requiere una prueba nueva antes de declararse estable.

## Comportamientos a preservar

| Área | Comportamiento validado | Fuente consultada | Destino nuevo |
| --- | --- | --- | --- |
| Adquisición | Ignorar datagramas de tamaño inesperado y frames fuera de carrera. | `main.py` | Driver Forza |
| Vehículo | Un cambio de `CarOrdinal` inicia contexto nuevo para no mezclar mediciones de coches distintos. | `main.py` | `SessionTracker` + `car_changed` |
| Dyno | La curva se construye por intervalos de RPM; los extremos se recortan 10 %. | `main.py` | Módulo Dyno |
| Dyno | Muestra válida: acelerador alto, potencia positiva y embrague en extremo. | `main.py` | Módulo Dyno |
| Dyno | Potencia y torque máximos de un intervalo se conservan independientemente. | `main.py` | Módulo Dyno + pruebas |
| Pedales | La UI puede actualizarse a menor frecuencia que UDP. | `main.py`, `static/app.js` | Módulo Inputs |
| Pista | El mapa usa X/Z y clasifica por predominio de acelerador o freno. | `main.py`, `static/app.js` | Módulo Track |
| Conexión | Una UI no debe aparentar datos actuales tras perder WebSocket. | `static/app.js` | Módulo Connection |
| Transmisión | La razón motor/rueda solo vale con embrague en extremo y valores útiles. | `validaciones.py` | Módulo Transmission |
| Física | El diámetro se infiere con rueda no motriz en FWD/RWD; AWD es ambiguo. | `validaciones.py` | Módulo Transmission |
| Arrastre | `power / speed` solo es fuerza en régimen casi estacionario y acelerador alto. | `validate_drag.py` | Módulo Physics |

## Límites de confianza

- El legado declara un paquete Forza de 331 bytes, pero el repositorio aún no contiene una captura independiente y trazable. La decodificación inicial es **experimental** hasta añadir ese fixture.
- Las unidades de `WheelRotSpeed` y el eje de aceleración longitudinal tienen scripts de validación, no un resultado archivado. No se exponen aún en el contrato público.
- La base comunitaria de nombres de coche es opcional; la identidad fiable para el core es `CarOrdinal`.

## Desglose de módulos actualizado

| Módulo | Pregunta que responde | Datos mínimos | Estado |
| --- | --- | --- | --- |
| Connection | ¿Hay telemetría actual y conexión al dashboard? | eventos de transporte | Esqueleto |
| Vehicle | ¿Qué coche generó esta sesión? | ordinal, clase, PI, tracción, cilindros | Esqueleto |
| Inputs | ¿Qué controla el conductor? | acelerador, freno, embrague, dirección | Siguiente |
| Motion | ¿Cómo se mueve el coche? | velocidad, posición, velocidad vectorial | Siguiente |
| Track | ¿Por dónde circuló y dónde acelera/frena? | X/Z, acelerador, freno, track id | Siguiente |
| Engine | ¿Cómo trabaja el motor? | RPM, límites, potencia, torque, boost, combustible | Siguiente |
| Dyno | ¿Cuál es la envolvente de potencia y torque? | Engine + Inputs + Vehicle | Siguiente |
| Session | ¿En qué vuelta/posición está? | vuelta, tiempos, posición, distancia | Siguiente |
| Transmission | ¿Cómo se relacionan motor, ruedas y marcha? | marcha, embrague, tracción, wheel speed | Investigación |
| Chassis | ¿Qué sucede en suspensión/neumáticos? | recorrido, temperatura, slip, desgaste | Futuro |

Los módulos consumen eventos del bus; ninguno llama a otro módulo ni solicita al backend que conserve sus series visuales.
