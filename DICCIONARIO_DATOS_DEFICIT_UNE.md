# Diccionario de Datos: Serie Histórica Diaria de Déficit Eléctrico UNE (2021–2026) ⚡🇨🇺

Este conjunto de datos recopila la serie histórica continua, diaria y oficial de los partes emitidos por la **Unión Eléctrica (UNE)** y el **Ministerio de Energía y Minas (MINEM)** de Cuba.

- **Período temporal:** 24 de agosto de 2021 hasta 2 de octubre de 2026.
- **Frecuencia:** Diaria (~1,529 días analizados).
- **Archivos generados:**
  - `cuba_energia_deficit_diario_une_2021_2026.csv` (formato tabular diario estándar: 1,529 días analizados).
  - `cuba_energia_deficit_diario_une_2021_2026.json` (formato JSON estructurado diario para dashboards web).
  - `cuba_energia_deficit_mensual_une_2021_2026.csv` (serie consolidada mensual de 60 meses: promedio, máximo y días con apagón 24h).
  - `cuba_energia_deficit_mensual_une_2021_2026.json` (serie consolidada mensual en formato JSON).

---

## 📋 Estructura de Columnas y Variables

| Nombre de Columna | Tipo de Dato | Unidad | Descripción y Contexto Operativo |
| :--- | :--- | :--- | :--- |
| `id` | Entero | ID | Identificador único de la publicación oficial en el repositorio de prensa oficial. |
| `fecha` | String (ISO) | `AAAA-MM-DD` | Fecha correspondiente al día del reporte matutino de la UNE. |
| `hora_publicacion` | String | `HH:MM:SS` | Hora exacta en que se divulgó oficialmente el parte. |
| `titulo` | String | Texto | Titular oficial del parte emitido por la UNE. |
| `afectacion_pico_mw` | Numérico (Float) | MW | **Afectación pronosticada para el horario pico nocturno** (máxima demanda). Representa los megavatios de carga desconectada / apagón previsto. |
| `deficit_pico_mw` | Numérico (Float) | MW | **Déficit de capacidad de generación proyectado en horario pico** (Demanda pico - Disponibilidad pico). |
| `disponibilidad_pico_mw` | Numérico (Float) | MW | Capacidad de generación total disponible estimada en el SEN para el horario pico. |
| `demanda_pico_mw` | Numérico (Float) | MW | Demanda máxima esperada en el país para el horario pico nocturno. |
| `max_afectacion_ayer_mw` | Numérico (Float) | MW | **Afectación real máxima por déficit ocurrida en el día anterior** (valor auditado ex-post). |
| `hora_max_ayer` | String | `HH:MM` | Hora exacta a la que ocurrió el pico máximo de apagón del día anterior. |
| `afectacion_ayer_24h` | Booleano | Bool | `True` si el día anterior el apagón fue ininterrumpido durante las 24 horas del día. |
| `afectacion_mediodia_mw` | Numérico (Float) | MW | Afectación estimada o real durante el horario de la media / diurno (11:00 - 14:00). |
| `disponibilidad_manana_mw`| Numérico (Float) | MW | Generación disponible a las 06:00 o 07:00 horas al momento de emitir el parte. |
| `demanda_manana_mw` | Numérico (Float) | MW | Demanda del SEN a las 06:00 o 07:00 horas. |
| `afectacion_manana_mw` | Numérico (Float) | MW | Afectación que ya existía en la mañana al momento de redactar el parte. |
| `limitacion_termica_mw` | Numérico (Float) | MW | Capacidad de generación térmica fuera por fallas técnicas en calderas, condensadores o turbinas. |
| `fuera_combustible_mw` | Numérico (Float) | MW | Capacidad no disponible por desabastecimiento de combustible (fueloil / diésel en motores y plantas). |
| `solar_fotovoltaica_mwh`| Numérico (Float) | MWh | Energía total generada por los parques solares fotovoltaicos en el día anterior. |
| `solar_potencia_max_mw` | Numérico (Float) | MW | Potencia pico instantánea entregada por la energía solar al SEN. |
| `url` | String | URL | Enlace permanente a la nota informativa oficial. |

---

## 📈 Resumen Estadístico y Evolución Anual (Horario Pico)

| Año | Días Registrados | Déficit Pico Promedio (MW) | Déficit Máximo Anual (MW) | Días con Déficit ≥ 1,000 MW | Días con Déficit ≥ 1,500 MW |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2021** | 62 | 53 MW | 465 MW | 0 | 0 |
| **2022** | 212 | 616 MW | 1,848 MW | 48 | 1 |
| **2023** | 357 | 203 MW | 1,225 MW | 1 | 0 |
| **2024** | 333 | 778 MW | 1,735 MW | 118 | 16 |
| **2025** | 325 | 1,556 MW | 2,120 MW | 301 | 225 |
| **2026 (YTD)** | 240 | 1,912 MW | 2,410 MW | 239 | 224 |

---

## 🚀 Ejemplos de Uso Rápido

### En Python (Pandas y Matplotlib)

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("cuba_energia_deficit_diario_une_2021_2026.csv", parse_dates=["fecha"])

# Graficar la evolución histórica del déficit en el pico
plt.figure(figsize=(14, 6))
plt.plot(df["fecha"], df["afectacion_pico_mw"], label="Afectación Pronosticada Pico (MW)", color="red", lw=1)
plt.plot(df["fecha"], df["max_afectacion_ayer_mw"], label="Máxima Afectación Real Ayer (MW)", color="black", alpha=0.5, lw=1)
plt.title("Evolución Diaria del Déficit Eléctrico en Cuba (Partes Oficiales UNE 2021–2026)")
plt.xlabel("Fecha")
plt.ylabel("Megavatios (MW)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("grafico_deficit_diario_cuba.png", dpi=300)
plt.show()
```
