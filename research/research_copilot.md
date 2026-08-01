\# Telemetry Protocol Comparison



\## Summary

La mayoría de los simuladores modernos exponen telemetría mediante \*\*UDP\*\* o \*\*Shared Memory\*\*, con frecuencias de actualización entre 20 Hz y 333 Hz. Las variables básicas como \*\*velocidad, RPM, marcha, acelerador, freno y tiempos de vuelta\*\* están presentes en casi todos los títulos. Las variables extendidas (temperatura de neumáticos, desgaste, daños, aerodinámica) varían según el motor del juego. Forza utiliza \*\*UDP Data Out\*\*, Assetto Corsa emplea \*\*bloques de memoria compartida\*\*, iRacing ofrece un \*\*SDK completo\*\*, y F1 Codemasters transmite \*\*paquetes UDP estructurados\*\*. BeamNG.drive es único al incluir datos de \*\*deformación y sensores\*\*.



\---



\## Communication Methods



| Juego | Método | Formato | Frecuencia |

|-------|--------|---------|------------|

| Forza Motorsport (2023) | UDP | Binario (Sled/Dash) | 60 Hz |

| Forza Horizon 5 | UDP | Binario (Sled/Dash) | \~60 Hz |

| Assetto Corsa | Shared Memory | Physics/Graphics/Static | 65–333 Hz |

| Assetto Corsa Competizione | UDP Broadcast API | ksBroadcastingNetwork | 20–60 Hz |

| iRacing | SDK/API | Variables ricas | 60 Hz |

| rFactor 2 | Shared Memory Plugin | rF2SharedMemoryMap | 50 Hz (telemetry), 5 Hz (scoring) |

| Automobilista 2 | UDP | Protocolo Project CARS | 20–60 Hz |

| Project CARS 2 | UDP | SMS UDP packets | 20–60 Hz |

| Dirt Rally 2.0 | UDP | Paquetes XML | \~100 Hz |

| BeamNG.drive | API Python | BeamNGpy (TCP/IPC) | Variable |

| F1 (Codemasters) | UDP | Paquetes estructurados | 60 Hz |



\---



\## Common Telemetry Variables



| Variable | FM23 | FH5 | AC | ACC | iRacing | rF2 | AMS2 | PCARS2 | DR2 | BeamNG | F1 |

|----------|------|-----|----|-----|---------|-----|------|--------|-----|--------|----|

| Speed | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| RPM | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Gear | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Throttle | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Brake | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Lap Time | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Tire Temp | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Suspension Travel | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

| Position (XYZ) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |



\---



\## Game-Specific Variables



\- \*\*Forza Motorsport/Horizon\*\*: Flags de superficie, profundidad de charcos, vibración en bordes.  

\- \*\*Assetto Corsa\*\*: Wheel slip, tyre wear, fuerzas G a 333 Hz.  

\- \*\*ACC\*\*: Delta de sesión, limitaciones del protocolo broadcast.  

\- \*\*iRacing\*\*: Más de 200 variables (aero, daños, pit info).  

\- \*\*rFactor 2\*\*: Telemetría de motor eléctrico, severidad de daños, fuerzas aerodinámicas.  

\- \*\*BeamNG.drive\*\*: Deformación del vehículo, sensores (LiDAR, cámaras, IMU).  

\- \*\*F1 Codemasters\*\*: ERS deployment, brake bias, paquetes de daños.  



\---



\## Recommended Core Telemetry



\- Speed  

\- RPM  

\- Gear  

\- Throttle / Brake / Clutch  

\- Position (XYZ)  

\- Orientation (Yaw/Pitch/Roll)  

\- Tire temperature  

\- Suspension travel  

\- Lap \& sector times  



\---



\## Extended Telemetry Candidates



\- Tire wear \& pressure  

\- G-forces  

\- Fuel level  

\- Weather conditions  

\- Aero data (downforce, drag)  

\- Damage states  



\---



\## Open Questions



\- ¿Los \*\*inputs del piloto\*\* (ángulo de dirección, handbrake, ayudas) deben ser parte del core o extendido?  

\- ¿Cómo normalizar las \*\*frecuencias de actualización\*\* (20 Hz vs 333 Hz)?  

\- ¿Los datos de \*\*multijugador/sesión\*\* (participantes, posiciones) deben ir en `TelemetryPacket` o en un módulo separado?  

\- ¿Cómo manejar la \*\*deformación específica de BeamNG\*\* sin sobrecargar el protocolo base?  



\---



