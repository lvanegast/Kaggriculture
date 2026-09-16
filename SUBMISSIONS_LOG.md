# 📓 Historial de Envíos y Registro de Estrategias (Kaggriculture)

Este documento registra cada versión del agente enviada a Kaggle, su hipótesis estratégica, resultados locales en la arena, desempeño en el Leaderboard real y lecciones aprendidas para **no repetir errores ni estrategias subóptimas**.

---

## 📊 Tabla Resumen de Envíos

| Envío # | Versión | Fecha | Estrategia Principal | Score Local (Prom.) | Rating Kaggle | Estado / Resultado |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **#1** | `v1.0` | 2026-09-15 | Clúster 4 casillas de Zanahorias continuas + DROP en `(4,4)` | $5,458 | 347 (bajó de 600) | **Superado**: Rival acumuló más dinero ($8k-$12k). |
| **#2** | `v2.0` | 2026-09-15 | Rotación Híbrida: 2 Melones ($1,500/cosecha) + 2 Zanahorias | $10,540 | *En calibración* | **En evaluación**: +188% sobre línea base (pico $12.7k). |

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
  - *En evaluación por los servidores de emparejamiento.*
* **Objetivo de este envío:**
  - Romper la barrera de los $10,000 de capital y revertir la racha inicial, escalando hacia el top del ranking.

---

## 🔮 Banco de Ideas para Futuros Envíos (v3.0, v4.0)

Para los próximos intentos diarios, considerar:

1. **Aprovechamiento de Fertilizante (`FERTILIZER`)**:
   - Comprar fertilizante cuando el dinero supere $4,000 para duplicar unidades en casillas clave.
2. **Sincronización con Tiendas del Pueblo (`Town Shops Arbitrage`)**:
   - Monitorear `obs["town"]["unlocked_shops"]` (ej. *Farmers Market*, *Pet Cafe*, *Smoothie Shop*). Si una tienda consume zanahorias o melones, vender con sobreprecio.
3. **Expansión de Cuadrante (`BUY_LAND`)**:
   - Cuando el capital supere $6,000, comprar el cuadrante Noreste (cuadrante 1) y contratar un operario (`HIRE`) que cuesta solo $1 para operar 4 casillas adicionales.
