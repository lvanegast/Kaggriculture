# 📓 Historial de Envíos y Registro de Estrategias (Kaggriculture)

Este documento registra cada versión del agente enviada a Kaggle, su hipótesis estratégica, resultados locales en la arena, desempeño en el Leaderboard real y lecciones aprendidas para **no repetir errores ni estrategias subóptimas**.

---

## 📊 Tabla Resumen de Envíos

| Envío # | Versión | Fecha | Estrategia Principal | Score Local (Prom.) | Rating Kaggle | Estado / Resultado |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **#1** | `v1.0` | 2026-09-15 | Clúster 4 casillas de Zanahorias continuas + DROP en `(4,4)` | $5,458 | **343** | **Superado**: Techo de ganancias bajo vs bots de alto margen. |
| **#2** | `v2.0` | 2026-09-15 | Rotación Híbrida: 2 Melones ($1,500/cosecha) + 2 Zanahorias | $10,540 | **182** | **Superado**: Insuficiente escala laboral frente al ladder. |
| **#3** | `v3.0` | 2026-09-15 | Escalamiento Laboral (2 Peones) + Clúster 9 tiles (4 Melones + 5 Zanahorias) | $16,795 | Evaluado en v4 | **Paso intermedio**: Multiplicó capacidad operativa a 72 acc/día. |
| **#4** | `v4.0` | 2026-09-15 | Mega-Clúster 14 Melones + 4 Zanahorias + 2 Peones (19 tiles cuadrante 0) | $33,768 (vs starter) | **400** | **Trampa de Saturación**: Explicada abajo en lección de mercado. |
| **#5** | `v5.0` | 2026-09-15 | FarmBrain Apex: Liquidación Prioritaria + Evacuación Día 29 + 14 Melones | $33,768 (vs starter) | **331** | **Trampa de Saturación**: Colapso de precio del melón ante rivales. |
| **#6** | `v6.0` | 2026-09-17 | **Anti-Crash Balanced Portfolio** (8 Melones + 4 Fresas + 4 Zanahorias + 2 Peones) | $28,599 | *Listo para subir* | **Gana +$3.2k vs v4** en duelos directos; resistente al colapso de mercado. |
| **#7** | `v7.0` | 2026-09-17 | **Dynamic Opponent Profiler** (Pivote en tiempo real según siembra rival) | $33,913 | **431** | **Máximo Score Histórico**: Superó a v4 (400) y v5 (331). |
| **#8** | `v8.0` | 2026-09-17 | **Quad-Labor Industrial Engine** (3 Peones = 96 acc/día; 12M + 4S + 4C) | $35,491 | Evaluado | Congestión por 4 trabajadores en cuadrante 0. |
| **#9** | `v9.0` | 2026-09-17 | **Adaptive Quad-Labor Engine** (3 Peones + Detección de Melones Rivales) | $32,574 | Evaluado | Versión experimental. |
| **#10** | `v10.0`| 2026-09-17 | **Grandmaster Apex** (Quad-Labor + Profiler + Zero-Waste End-Game Cutoffs) | $32,923 | Evaluado | Versión experimental. |
| **#11** | `v11.0`| 2026-09-20 | **FarmBrain v11 Apex Master**: Evolución directa de v7 (2 Peones, Zero-Waste Cutoff, Evacuación Día 29) | $34,021 | *Listo para subir* | **Gana +$3,000 vs v7** en duelos directos; conserva el ratio laboral óptimo de 431 Elo. |

---

## 🔬 Descubrimiento Crítico: "La Trampa del Melón" (The Melon Rush Trap)

Tras inspeccionar el código fuente del simulador (`kaggriculture.py`) se descubrió la causa exacta de por qué **v4 (400)** y **v5 (331)** cayeron en el ladder de Kaggle a pesar de lograr $34k localmente contra el Starter:

1. **La Fórmula Cuadrática de Castigo de Precios:**
   ```python
   MARKET_PARAMS["MELON"] = {
       "base": 250, "I0": 10000, "T": 300, 
       "below_func": "log", "above_func": "sq", "above_target": 3.60
   }
   ```
   - El precio del melón por encima del inventario base ($I_0 = 10,000$) cae con una función **cuadrática (`sq`)**.
   - Con tan solo **158 melones de exceso** vendidos en todo el mercado, el precio del melón se desploma de **$250 a $1.00** (el precio mínimo absoluto).
2. **Ninguna Tienda del Pueblo Consume Melones:**
   - En `kaggriculture.py`, las tiendas (*Smoothie Shop*, *Ice Cream Shop*, *Brunch Spot*, *Bakery*, *Pet Cafe*, *Farmers Market*) consumen hortalizas cada 4 turnos (`townShopSellInterval = 4`).
   - **¡Ninguna tienda del pueblo compra melones!** Solo el *Town Center* consume 1 mísero melón cada 24 turnos (1 melón al día). En una partida de 30 días, el pueblo solo absorbe 30 melones en total.
3. **El Efecto en el Ladder de Kaggle:**
   - En el ladder de Kaggle, otros competidores también siembran melones.
   - Cuando ambos jugadores cosechan y venden 70-80 melones en los Días 12 y 24, el mercado se inunda instantáneamente con más de 150 melones.
   - El precio del melón cae a $1.00. Un bot puramente melonero (como v4 o v5) pasa de ganar $34,000 a ganar solo **$14,000 - $16,000**, empatando o perdiendo frente a cualquier bot diversificado.

### La Solución Ganadora: Fresa (`STRAWBERRY`) + Cuádruple Fuerza Laboral
1. **Fresas Continuas (`ongoing: True`):**
   - Se plantan en los Días 0-2 (semilla $100).
   - Tienen su primera cosecha el Día 10, y a partir de ahí **producen 4 fresas cada 2 días hasta el final de la temporada SIN costo de re-siembra**.
   - 4 plantas de fresa producen hasta 160 fresas a lo largo de la partida.
   - **4 Tiendas del Pueblo consumen fresas cada 4 turnos**: *Smoothie Shop*, *Ice Cream Shop*, *Brunch Spot*, *Farmers Market*. La demanda constante drena el inventario y mantiene el precio alto.
2. **Escalamiento a 3 Peones (4 Trabajadores = 96 acciones/día):**
   - El 3er peón cuesta solo $2/día (sucesión de Fibonacci).
   - Con 4 trabajadores coordinados, atendemos 20 casillas agrícolas alrededor del cobertizo sin ningún cuello de botella.
   - En duelo directo contra un bot de melones puros (v4), nuestra estrategia lo destruye por un margen de **+$10,000 a +$13,800**.

---

## 📁 Archivos Generados y Listos para los 5 Envíos de Hoy

Todos los archivos han sido verificados contra el motor de simulación oficial de Kaggle (`kaggle_environments`) y están listos en la raíz del proyecto:

### 1. Envío #6: [`submission_v6_balanced.py`](file:///C:/Proyectos/Kaggriculture/submission_v6_balanced.py)
* **Estrategia:** Cartera Balanceada Inmune al Crash (8 Melones + 4 Fresas continuas + 4 Zanahorias + 2 Peones).
* **Score vs Starter:** $28,599.00
* **Duelo vs v4:** Gana por **+$3,244.00** ($20,113 vs $16,869).

### 2. Envío #7: [`submission_v7_adaptive.py`](file:///C:/Proyectos/Kaggriculture/submission_v7_adaptive.py)
* **Estrategia:** Perfilado de Oponente en Tiempo Real. Si el rival siembra melones, activa el escudo anti-crash (8M, 4S, 4C). Si el rival es pasivo, monopoliza melones (14M, 4C).
* **Score vs Starter:** $33,913.00
* **Duelo vs v4:** Gana por **+$5,109.00** ($21,634 vs $16,525).

### 3. Envío #8: [`submission_v8_expanded_labor.py`](file:///C:/Proyectos/Kaggriculture/submission_v8_expanded_labor.py)
* **Estrategia:** Motor Industrial Cuádruple (3 Peones = 96 acc/día; 12 Melones + 4 Fresas + 4 Zanahorias en 20 parcelas).
* **Score vs Starter:** $35,491.00
* **Duelo vs v4:** Gana por **+$10,012.00** ($23,568 vs $13,556).

### 4. Envío #9: [`submission_v9_adaptive_quad.py`](file:///C:/Proyectos/Kaggriculture/submission_v9_adaptive_quad.py)
* **Estrategia:** Cuádruple Laboral Adaptativa (3 Peones + Detección de Oponente). Si el rival rushea melones, despliega 12M + 4S + 4C. Si es pasivo, expande a 16M + 4C.
* **Score vs Starter:** $32,574.00
* **Duelo vs v4:** Gana por **+$13,824.00** (hunde a v4 a solo $8,863).

### 5. Envío #10: [`submission_v10_apex.py`](file:///C:/Proyectos/Kaggriculture/submission_v10_apex.py)
* **Estrategia:** Grandmaster Apex. La culminación de todas las mecánicas: 4 Trabajadores + Perfilador Adaptativo + Cortes estrictos de compra en Días 14/26 para eliminar pérdidas + Evacuación de mochilas el Día 29.
* **Score vs Starter:** $32,923.00
* **Duelo vs v4:** Gana por **+$13,561.00** ($23,393 vs $9,832 tanto de P0 como de P1).
