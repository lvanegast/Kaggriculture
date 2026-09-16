# 📓 Historial de Envíos y Registro de Estrategias (Kaggriculture)

Este documento registra cada versión del agente enviada a Kaggle, su hipótesis estratégica, resultados locales en la arena, desempeño en el Leaderboard real y lecciones aprendidas para **no repetir errores ni estrategias subóptimas**.

---

## 📊 Tabla Resumen de Envíos

| Envío # | Versión | Fecha | Estrategia Principal | Score Local (Prom.) | Rating Kaggle | Estado / Resultado |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **#1** | `v1.0` | 2026-09-15 | Clúster 4 casillas de Zanahorias continuas + DROP en `(4,4)` | $5,458 | 347 (bajó de 600) | **Superado**: Rival acumuló más dinero ($8k-$12k). |
| **#2** | `v2.0` | 2026-09-15 | Rotación Híbrida: 2 Melones ($1,500/cosecha) + 2 Zanahorias | $10,540 | 447 (+100 vs v1) | **Mejora clara**: +100 puntos en el ladder, pero insuficiente vs bots >$15k. |
| **#3** | `v3.0` | 2026-09-15 | Escalamiento Laboral (2 Peones) + Clúster 9 tiles (4 Melones + 5 Zanahorias) | $16,795 | *Pendiente Envío* | **Listo para Envío**: Multiplica capacidad operativa 3x. |

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

## 🔮 Banco de Ideas para Futuros Envíos (v4.0, v5.0)

Para los próximos intentos diarios, considerar:

1. **Aprovechamiento de Fertilizante (`FERTILIZER`)**:
   - Comprar fertilizante cuando el dinero supere $4,000 para duplicar unidades en casillas clave.
2. **Sincronización con Tiendas del Pueblo (`Town Shops Arbitrage`)**:
   - Monitorear `obs["town"]["unlocked_shops"]` (ej. *Farmers Market*, *Pet Cafe*, *Smoothie Shop*). Si una tienda consume zanahorias o melones, vender con sobreprecio.
3. **Expansión de Cuadrante (`BUY_LAND`)**:
   - Cuando el capital supere $6,000, comprar el cuadrante Noreste (cuadrante 1) y contratar un operario (`HIRE`) que cuesta solo $1 para operar 4 casillas adicionales.
