# 📓 Historial de Envíos y Registro de Estrategias (Kaggriculture)

Este documento registra cada versión del agente enviada a Kaggle, su hipótesis estratégica, resultados locales en la arena, desempeño en el Leaderboard real y lecciones aprendidas para **no repetir errores ni estrategias subóptimas**.

---

## 📊 Tabla Resumen de Envíos

| Envío # | Versión | Fecha | Estrategia Principal | Score Local (Prom.) | Rating Kaggle | Estado / Resultado |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **#1** | `v1.0` | 2026-09-15 | Clúster 4 casillas de Zanahorias continuas + DROP en `(4,4)` | $5,458 | 347 (bajó de 600) | **Superado**: Rival acumuló más dinero ($8k-$12k). |
| **#2** | `v2.0` | 2026-09-15 | Rotación Híbrida: 2 Melones ($1,500/cosecha) + 2 Zanahorias | $10,540 | 447 (+100 vs v1) | **Mejora clara**: +100 puntos en el ladder, pero insuficiente vs bots >$15k. |
| **#3** | `v3.0` | 2026-09-15 | Escalamiento Laboral (2 Peones) + Clúster 9 tiles (4 Melones + 5 Zanahorias) | $16,795 | *En evaluación* | **Enviado**: Multiplica capacidad operativa 3x. Esperando Elo. |
| **#4** | `v4.0` | 2026-09-15 | Mega-Clúster 14 Melones + 4 Zanahorias + 2 Peones (19 tiles cuadrante 0) | $33,768 | 456 (provisional) | **En evaluación**: Entró en 600, calibrando en el ladder. |
| **#5** | `v5.0` | 2026-09-15 | FarmBrain Apex: Liquidación Prioritaria + Evacuación Día 29 + 14 Melones | $33,768 | *Pendiente Envío* | **Listo para Envío**: Pico de $36,084. Último intento del día. |

---

## 🔍 Detalle de Estrategias

### 📦 Envío #1: FarmBrain v1.0 — "Pure Carrot Cluster"
* **Fecha:** 2026-09-15
* **Código base:** Commit `4b02a70`
* **Hipótesis:** 
  - Cultivar un bloque cerrado de 4 casillas adyacentes al cobertizo `[(4,4), (3,4), (4,3), (3,3)]` exclusivamente con zanahorias (ciclo corto de 3 días) para eliminar costos de viaje.
  - Descargar automáticamente al cobertizo (`DROP`) y vender de inmediato.
* **Mecánicas aplicadas:**
  - Siembra: 100% Zanahorias.
  - Gestión de inventario: Descarga al cobertizo en `(4, 4)` cuando lleva hortalizas en la mochila.
  - Parada de fin de temporada: Detener siembras el día 26 y vender todo.
* **Resultados en Pruebas Locales (Arena):**
  - Tasa de victoria vs. `starter`: 100% (10/10).
  - Puntuación promedio: **$5,458.70** (Rival: $3,601.90).
* **Desempeño en Kaggle:**
  - Rating inicial: 600.
  - Rating resultante: **347** tras las primeras 2-3 partidas.
* **Lección Aprendida / Qué NO Repetir:**
  > [!WARNING]
  > **Techo de ingresos bajo:** La zanahoria genera un flujo de caja rápido y seguro ($120 netos cada 3 días), pero tiene un techo máximo de ~$5,500 en la temporada completa. Los competidores reales en Kaggle están usando cultivos de alto margen (como melones o árboles) que alcanzan $8,000 - $12,000+. Un bot que solo siembre zanahorias siempre perderá contra oponentes de mitad o tabla alta.

---

### 📦 Envío #2: FarmBrain v2.0 — "Hybrid Melon + Carrot Engine"
* **Fecha:** 2026-09-15
* **Código base:** Commit `095c388`
* **Hipótesis:**
  - El **Melón (`MELON`)** tiene el multiplicador de beneficio más alto del juego: una semilla de $80 rinde 6 melones a $250 base = **$1,500 en efectivo por cosecha**.
  - Reservar 2 casillas fijas `(3, 4)` y `(4, 3)` para dos tandas de melones (Días 0-12 y Días 12-24) aporta **+$6,000 directos** de beneficio limpio.
  - En las otras 2 casillas `(4, 4)` y `(3, 3)`, mantener la rotación rápida de zanahorias para financiar los costos operativos y abastecer tiendas del pueblo.
* **Mecánicas aplicadas:**
  - Lote 1 de Melones: Días 0 al 2 (cosecha el día 12).
  - Lote 2 de Melones: Días 12 al 14 (cosecha el día 24-25).
  - Zanahorias continuas: Días 0 al 26 en slots secundarios.
  - Parada de siembra: Día 26.
  - Descarga automática al cobertizo y liquidación total.
* **Resultados en Pruebas Locales (Arena):**
  - Tasa de victoria vs. `starter`: 100% (10/10).
  - Puntuación promedio: **$10,540.00** (Rival: $3,655.70).
  - Puntuación máxima: **$12,771.00**.
* **Desempeño en Kaggle:**
  - Rating inicial: 600.
  - Rating resultante: **447** (subió **+100 puntos** frente al 347 del bot v1.0).
* **Lección Aprendida:**
  > [!NOTE]
  > El salto de $5.4k a $10.5k le otorgó de inmediato +100 puntos de rating. Sin embargo, en el ladder competitivo los rivales del rango 600-800+ están haciendo entre **$14,000 y $18,000**, por lo que un bot con 1 solo trabajador y solo 2 melones se queda corto en turnos/acciones para superar a la mitad alta. La solución obligatoria es el escalamiento laboral multi-peón (v3.0).

---

### 📦 Envío #3: FarmBrain v3.0 — "Industrial Multi-Worker Scaling"
* **Fecha:** 2026-09-15
* **Código base:** `submission.py` (FarmBrainV3)
* **Hipótesis:**
  - En lugar de limitarse a 1 trabajador (24 acciones/día), contratar **2 peones diarios (`HIRE`)** cuesta una miseria ($1 + $1 = $2/día) debido a la progresión Fibonacci del coste de contratación diario.
  - Esto triplica la capacidad operativa a **72 acciones de unidades por día**.
  - Con 3 trabajadores coordinados mediante reserva de objetivos (`claimed_targets`), podemos expandir el cultivo a un **clúster denso de 9 casillas** adyacente al cobertizo:
    - **4 casillas dedicadas a Melones**: `[(3, 4), (4, 3), (3, 3), (2, 4)]` en dos tandas masivas (Días 0-12 y Días 12-24), generando hasta 48 melones = **$12,000+ en ingresos de melón**.
    - **5 casillas dedicadas a Zanahorias**: `[(4, 4), (4, 2), (2, 3), (3, 2), (2, 2)]` produciendo un flujo ininterrumpido de liquidez rápida para semillas y salarios.
  - Gestión integral de mochilas: los trabajadores descargan en `(4, 4)` tan pronto como tienen cosechas y no hay tareas urgentes.
* **Mecánicas aplicadas:**
  - Contratación: Hasta 2 peones por día hasta el día 25.
  - Coordinación: Despacho greedy con prevención de colisiones (`claimed_targets` por turno).
  - Parada de siembra: Día 26.
  - Cosecha y liquidación total asegurada antes del turno 720.
* **Resultados en Pruebas Locales (Arena):**
  - Tasa de victoria vs. `starter`: 100% (10/10).
  - Puntuación promedio: **$16,794.90** (Rival: $3,442.50).
  - Puntuación máxima: **$17,733.00**.
  - Margen de ventaja: **+$13,352.40**.
* **Objetivo de este envío:**
  - Romper los $16,000 en Kaggle y catapultar el ranking competitivo a los puestos más altos de la tabla.

---

### 📦 Envío #4: FarmBrain v4.0 — "Mega-Cluster 14 Melones + 4 Zanahorias"
* **Fecha:** 2026-09-15
* **Código base:** [`submission_v4_megacluster.py`](file:///C:/Proyectos/Kaggriculture/submission_v4_megacluster.py) / [`submission.py`](file:///C:/Proyectos/Kaggriculture/submission.py)
* **Hipótesis:**
  - El análisis minucioso del motor de simulación reveló que en Kaggriculture, el precio base del melón es **$250** (con multiplicador cuadrático hacia abajo solo si se supera $I_0 = 10,000$). Vender hasta 84 melones por lote apenas deprime el precio a ~$200.
  - Al contar con 3 trabajadores (Granjero + 2 Peones = 72 acciones/día), se pueden atender sin esfuerzo hasta **18-19 casillas cultivadas** en el Cuadrante 0 sin pagar los $1,000 de expansión de tierra.
  - **14 Casillas dedicadas a Melones**: Dos tandas masivas (Días 0-12 y Días 12-24). Cada tanda genera 14 x 6 = **84 melones**, produciendo ~$17,000 por lote (~$34,000 en total solo de melones).
  - **4 Casillas de Zanahorias fijas**: Proporcionan liquidez continua ($140 cada 3 días) para financiar los $2/día de peones y asegurar que nunca falte saldo para re-siembras.
  - Prevención de colisiones distribuida (`claimed_targets`) para que los 3 trabajadores se repartan el trabajo de riego y cosecha sin solaparse.
* **Resultados en Pruebas Locales (Arena - 10 partidas):**
  - Tasa de victoria vs. `starter`: 100% (10/10).
  - Puntuación promedio: **$33,768.50** (Rival: $3,444.80).
  - Puntuación máxima (Pico): **$35,823.00**.
  - Margen de ventaja: **+$30,323.70**.
* **Objetivo de este envío:**
  - Duplicar de golpe el rendimiento de la v3.0 ($16.8k -> $33.8k) y competir de lleno en el Top Tier del Leaderboard global.

---

### 📦 Envío #5: FarmBrain v5.0 — "Apex: Value-Priority Liquidation & Day 29 Evacuation"
* **Fecha:** 2026-09-15
* **Código base:** [`submission_v5_apex.py`](file:///C:/Proyectos/Kaggriculture/submission_v5_apex.py) / [`submission.py`](file:///C:/Proyectos/Kaggriculture/submission.py)
* **Hipótesis:**
  - **Liquidación por Prioridad de Rentabilidad**: En lugar de iterar el cobertizo en orden arbitrario, forzar la venta en orden de mayor valor por unidad: `MELON` ($250) primero, luego `STRAWBERRY` ($120), `TOMATO` ($60), `CARROT` ($35) y `WHEAT` ($25). Esto garantiza que los fondos de alto volumen ingresen en el primer turno de procesamiento de mercado.
  - **Protocolo de Cierre Absoluto (Día 29)**: En las últimas 24 horas (turnos 696 a 719), cualquier peón o granjero que lleve productos en la mochila abandona cualquier tarea secundaria y camina directamente a `(4, 4)` a soltar la cosecha (`["DROP"]`). En ese mismo turno, el mercado liquida todo el cobertizo, asegurando que **cero unidades de hortalizas queden atrapadas en mochilas al terminar el turno 720**.
  - **Clúster de Máximo Rendimiento**: 14 Melones en dos tandas masivas + 4 Zanahorias de liquidez continua en Cuadrante 0.
* **Resultados en Pruebas Locales (Arena - 10 partidas):**
  - Tasa de victoria vs. `starter`: 100% (10/10).
  - Puntuación promedio: **$33,768.30** (Rival: $3,444.80).
  - Puntuación máxima verificada: **$36,084.00**.
  - Margen de ventaja: **+$30,323.50**.
* **Objetivo de este envío:**
  - Maximizar hasta el último dólar con liquidación perfecta al cierre de temporada, coronando el 5º y último envío del día.

---

## 🔮 Banco de Ideas para Futuros Envíos (Día 2 en adelante)

Para los próximos intentos diarios, considerar:

1. **Aprovechamiento de Fertilizante (`FERTILIZER`)**:
   - Comprar fertilizante cuando el dinero supere $4,000 para duplicar unidades en casillas clave.
2. **Sincronización con Tiendas del Pueblo (`Town Shops Arbitrage`)**:
   - Monitorear `obs["town"]["unlocked_shops"]` (ej. *Farmers Market*, *Pet Cafe*, *Smoothie Shop*). Si una tienda consume zanahorias o melones, vender con sobreprecio.
3. **Expansión de Cuadrante (`BUY_LAND`)**:
   - Cuando el capital supere $6,000, comprar el cuadrante Noreste (cuadrante 1) y contratar un operario (`HIRE`) que cuesta solo $1 para operar 4 casillas adicionales.
