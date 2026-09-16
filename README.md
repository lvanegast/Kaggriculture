# Kaggriculture - Autonomous Simulation Framework

Framework autónomo y suite de agentes competitivos para la competencia de simulación de Kaggle **[Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)**.

## 🚀 Inicio Rápido con `uv`

Este proyecto utiliza **[`uv`](https://github.com/astral-sh/uv)** para la gestión rápida de entornos virtuales y dependencias en Python 3.13.

### 1. Sincronizar dependencias
```bash
uv sync
```

### 2. Ejecutar Torneo Local (Arena 1v1)
Compite contra la línea base oficial de Kaggle (`starter`) a lo largo de $N$ partidas de 720 turnos:
```bash
uv run python scripts/arena.py --agent1 greedy --agent2 starter --games 10
```

### 3. Generar y Validar `submission.py`
Compila el agente actual en un archivo autónomo `submission.py` de cero dependencias externas y verifica su ejecución en `kaggle-environments`:
```bash
uv run python scripts/build_submission.py --verify
```

### 4. Ejecutar Suite de Pruebas
```bash
uv run pytest -v
```

---

## 📁 Estructura del Proyecto

```
Kaggriculture/
├── .agents/
│   ├── skills/kaggriculture/SKILL.md  # Skill de Antigravity con flujos de trabajo
│   └── rules/kaggriculture.md         # Reglas y directrices de desarrollo
├── src/
│   └── kaggriculture/
│       ├── sim/
│       │   ├── types.py               # Tipos, catálogo de cultivos y parser
│       │   └── kaggle_wrapper.py      # Runner y utilidades de simulación
│       └── agents/
│           ├── base.py                # Interfaz abstracta BaseAgent
│           ├── baseline_naive.py      # Agente Starter Baseline
│           └── greedy_scheduler.py    # FarmBrainGreedy con clúster adyacente al cobertizo
├── scripts/
│   ├── arena.py                       # Arena de torneos head-to-head con reportes en terminal
│   └── build_submission.py            # Generador y validador de submission.py
├── tests/                             # Suite de pruebas automatizadas
├── pyproject.toml                     # Configuración del proyecto y dependencias con uv
└── submission.py                      # Archivo empaquetado listo para subir a Kaggle
```

---

## 🌾 Agentes y Estrategias

- **`FarmBrainGreedy` (v1.0)**:
  - Cultivo intensivo en clúster compacto de 4 casillas conectado al cobertizo central `(4, 4)`.
  - Cero tiempos muertos de transporte (distancia de Manhattan $\le 2$).
  - Descarga automática al cobertizo (`DROP`) y venta continua en el mercado.
  - Limpieza activa de malezas (`DIG`) y parada de siembra en fin de temporada (día 26).
  - Rendimiento: **100% de victorias** frente a la línea base oficial ($5,458 vs $3,601 promedio).
