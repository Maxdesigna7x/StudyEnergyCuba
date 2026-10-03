# StudyEnergyCuba ⚡🛢️

Auditoría numérica y estudio interactivo sobre la correlación entre las importaciones de combustible (estatal vs privado), la generación termoeléctrica, el avance de energías renovables (solar) y el déficit del Sistema Electroenergético Nacional (SEN) en Cuba.

🔗 **Sitio Web Interactivo (GitHub Pages):**  
👉 **[https://Maxdesigna7x.github.io/StudyEnergyCuba/](https://Maxdesigna7x.github.io/StudyEnergyCuba/)**

---

## 📌 Preguntas Clave Respondidas con Datos

1. **¿Concuerda el combustible que entra con la generación eléctrica?**  
   - **No.** El balance termodinámico oficial (550 kWh/barril) revela que en 2023 entraron 115,000 BPD y la red solo consumió 65,800 BPD. Quedó un remanente no explicado de **49,200 BPD** mientras el país sufría 880 MW de apagones promedio.
2. **¿El refinado de EE.UU. en 2026 entra a las termoeléctricas o se le vende al gobierno?**  
   - **No.** Las ventas de combustible refinado desde EE.UU. (~32,000 BPD) corresponden al sector privado (MIPYMES) bajo licencias comerciales humanitarias y no son para el gobierno ni aptas para plantas térmicas. Se excluyen de la gráfica vs déficit. El gobierno solo dispuso de **35,500 BPD** estatales, explicando el récord de 2,100 MW de apagones.
3. **¿La caída de combustible se debe a la transición solar?**  
   - **No.** Entre 2024 y 2025, el petróleo cayó en -33,500 BPD y la energía solar apenas generó el equivalente a +548 BPD (1.6% del déficit). El 98.4% restante fue colapso de suministro.

---

## 📂 Estructura del Repositorio

- `index.html`: Dashboard principal interactivo (2020–2026 YTD) con Chart.js, responsive para celular y escritorio.
- `analisis_historico_2015_2025/`: Serie histórica completa de 12 años (2015–2026 YTD), analizando la era de superávit y reventa formal en Cuvenpetrol y el efecto umbral de los 110,000 BPD.
- `assets/`: Gráficos de alta resolución generados en Python.
- `scratch/`: Scripts de cálculo termodinámico y balances de masa.

---

## 📊 Fuentes de Datos

- **Oficina Nacional de Estadística e Información (ONEI):** Anuarios *Electricidad en Cuba* y balances energéticos oficiales.
- **Unión Eléctrica de Cuba (UNE):** Partes diarios de disponibilidad y afectación en horario pico.
- **Energy Institute, University of Texas at Austin (Jorge Piñón):** Rastreo de tanqueros y envíos marítimos.
- **Kpler y Reuters:** Monitoreo satelital y comercial de hidrocarburos.
