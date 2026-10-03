import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

output_dir = "/home/randy/Game_Dev/3d/analisis_historico_2015_2025/assets"
os.makedirs(output_dir, exist_ok=True)

years = np.array([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026])

# 1. Imports by Country (BPD)
vzla = np.array([90000, 75000, 58000, 51000, 55000, 62000, 56000, 53500, 55000, 33500, 11000, 1500])
mexico = np.array([0, 0, 0, 0, 0, 0, 0, 1000, 18500, 20000, 13000, 2500])
russia = np.array([0, 0, 4000, 3000, 2000, 1500, 2000, 4500, 5500, 5500, 3500, 2000])
others = np.array([5000, 5000, 4000, 3500, 3000, 3500, 3000, 2500, 2000, 1500, 1500, 1500])

# Importaciones vendidas / entregadas estrictamente al Estado / Gobierno
state_imports = vzla + mexico + russia + others

# Importaciones del sector privado / MIPYMES de EE.UU. (NO se venden al gobierno ni van a termoeléctricas)
eeuu_private = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32000])

domestic_crude = np.array([50000, 48000, 45000, 43000, 41000, 42000, 38000, 36000, 34000, 32000, 30000, 28000])

# Combustible REAL disponible para el Gobierno / SEN (Crudo Nacional + Importaciones Estatales)
state_fuel_available = state_imports + domestic_crude

# 2. Electric Generation (GWh)
total_gen_gwh = np.array([20123.0, 20245.0, 20558.1, 20837.0, 20622.0, 19070.9, 17965.5, 15732.1, 15331.1, 14344.9, 12200.0, 11400.0])

# Renewables Breakdown (GWh)
biomass_gwh = np.array([510, 530, 500, 490, 420, 330, 290, 245, 215, 200, 180, 150])
solar_gwh = np.array([290, 305, 325, 350, 375, 410, 430, 420, 440, 510, 620, 800])
hydro_gwh = np.array([140, 135, 125, 120, 125, 130, 110, 105, 95, 90, 85, 90])
wind_gwh = np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
total_renewables_gwh = biomass_gwh + solar_gwh + hydro_gwh + wind_gwh

# 3. Peak Generation Deficit (MW)
deficit_mw = np.array([0, 0, 20, 30, 80, 150, 520, 980, 880, 1350, 1950, 2100])

# -------------------------------------------------------------
# CHART 1: 12-Year Fuel Imports & Country Share (2015-2026)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors = ['#dc2626', '#16a34a', '#1e40af', '#94a3b8', '#0284c7']

# Volume Bar Chart
total_country_imports = state_imports + eeuu_private
ax1.bar(years, vzla, label='Venezuela (PDVSA)', color=colors[0], width=0.6)
ax1.bar(years, mexico, bottom=vzla, label='México (PEMEX)', color=colors[1], width=0.6)
ax1.bar(years, russia, bottom=vzla+mexico, label='Rusia', color=colors[2], width=0.6)
ax1.bar(years, others, bottom=vzla+mexico+russia, label='Otros (Argelia / Spot)', color=colors[3], width=0.6)
ax1.bar(years, eeuu_private, bottom=vzla+mexico+russia+others, label='EE.UU. (Sector Privado / MIPYMES)', color=colors[4], hatch='//', width=0.6)

ax1.set_title('Importaciones de Combustible a Cuba (2015–2026 YTD)\n[Diferenciando Sector Estatal vs Sector Privado]', fontsize=12, fontweight='bold', pad=12)
ax1.set_ylabel('Barriles por Día (BPD)', fontsize=11)
ax1.set_xlabel('Año', fontsize=11)
ax1.set_ylim(0, 120000)
for y, s_tot, p_tot in zip(years, state_imports, eeuu_private):
    tot = s_tot + p_tot
    if p_tot > 0:
        ax1.annotate(f'Estatal: {int(s_tot/1000)}k\nPriv: {int(p_tot/1000)}k', xy=(y, tot), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=7.5, fontweight='bold')
    else:
        ax1.annotate(f'{int(tot/1000)}k', xy=(y, tot), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Percentage Share
vzla_pct = (vzla / total_country_imports) * 100
mex_pct = (mexico / total_country_imports) * 100
rus_pct = (russia / total_country_imports) * 100
oth_pct = (others / total_country_imports) * 100
eeuu_pct = (eeuu_private / total_country_imports) * 100

ax2.bar(years, vzla_pct, label='Venezuela %', color=colors[0], width=0.6)
ax2.bar(years, mex_pct, bottom=vzla_pct, label='México %', color=colors[1], width=0.6)
ax2.bar(years, rus_pct, bottom=vzla_pct+mex_pct, label='Rusia %', color=colors[2], width=0.6)
ax2.bar(years, oth_pct, bottom=vzla_pct+mex_pct+rus_pct, label='Otros %', color=colors[3], width=0.6)
ax2.bar(years, eeuu_pct, bottom=vzla_pct+mex_pct+rus_pct+oth_pct, label='EE.UU. (Privado) %', color=colors[4], hatch='//', width=0.6)

ax2.set_title('Evolución del Share de Proveedores de Crudo (2015–2026 YTD)\n[% del Total Importado]', fontsize=12, fontweight='bold', pad=12)
ax2.set_ylabel('Participación (%)', fontsize=11)
ax2.set_xlabel('Año', fontsize=11)
ax2.set_ylim(0, 100)
ax2.legend(loc='lower left', frameon=True, fontsize=8.5)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
c1_path = os.path.join(output_dir, "cuba_fuel_imports_2015_2025.png")
plt.savefig(c1_path, dpi=300)
plt.close()

# -------------------------------------------------------------
# CHART 2: Fuel Supply vs Deficit (2015-2026) - STRICTLY STATE FUEL
# -------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()

# Línea 1: Combustible Estatal Total Disponible para el Gobierno
l1 = ax1.plot(years, state_fuel_available, marker='o', color='#2563eb', linewidth=2.8, 
              label='Combustible Total Estatal Disponible para el Gobierno (BPD)')

# Línea 2: Total Importaciones Vendidas/Entregadas al Gobierno desde el Exterior
l2 = ax1.plot(years, state_imports, marker='s', color='#0d9488', linewidth=2.2, linestyle='--', 
              label='Total Importaciones Vendidas/Entregadas al Gobierno (BPD)')

l3 = ax1.axhline(110000, color='gray', linestyle=':', label='Umbral Demanda Base (~110k BPD)')

bars = ax2.bar(years, deficit_mw, width=0.4, color='#dc2626', alpha=0.6, label='Déficit de Generación Pico (MW - UNE)')

ax1.set_xlabel('Año', fontsize=11, fontweight='bold')
ax1.set_ylabel('Suministro de Petróleo Estatal (BPD)', fontsize=11, color='#2563eb', fontweight='bold')
ax2.set_ylabel('Déficit Promedio Pico (MW)', fontsize=11, color='#dc2626', fontweight='bold')

ax1.set_ylim(0, 160000)
ax2.set_ylim(0, 2500)

ax1.scatter([2026], [state_fuel_available[-1]], color='#2563eb', s=100, zorder=5)
ax1.scatter([2026], [state_imports[-1]], color='#0d9488', s=100, zorder=5)

ax1.annotate('Era de Superávit / Reventa\n(2015-2016: >130k-145k BPD)\nDéficit = 0 MW', 
             xy=(2015.5, 140000), xytext=(2015, 145000),
             bbox=dict(boxstyle="round,pad=0.3", fc="#eff6ff", ec="#2563eb", lw=1),
             fontweight='bold', fontsize=8.5)

ax1.annotate('Total Estatal 2026: 35,500 BPD\n(28k nacional + 7.5k importado)\nExplica el récord de 2,100 MW', 
             xy=(2026, state_fuel_available[-1]), xytext=(2022.8, 52000),
             arrowprops=dict(facecolor='#2563eb', arrowstyle='->', lw=1.5),
             bbox=dict(boxstyle="round,pad=0.3", fc="#eff6ff", ec="#2563eb", lw=1.2),
             fontweight='bold', fontsize=8.5, color='#1e40af')

ax1.annotate('Total Vendido al Gobierno: 7,500 BPD\n(Colapso total de aliados)', 
             xy=(2026, state_imports[-1]), xytext=(2023.2, 16000),
             arrowprops=dict(facecolor='#0d9488', arrowstyle='->', lw=1.5),
             bbox=dict(boxstyle="round,pad=0.3", fc="#f0fdfa", ec="#0d9488", lw=1.2),
             fontweight='bold', fontsize=8.5, color='#0f766e')

# Cuadro explicativo de exclusión de combustible privado
ax1.text(0.02, 0.95, 
         "⚠️ EXCLUSIÓN TRANSPARENTE: NO se cuenta el combustible refinado de EE.UU. (32,000 BPD en 2026)\n"
         "porque es venta privada a MIPYMES; NO se le vende al gobierno ni se quema en termoeléctricas.",
         transform=ax1.transAxes, fontsize=8.2, verticalalignment='top',
         bbox=dict(boxstyle="round,pad=0.4", fc="#fffbeb", ec="#f59e0b", lw=1.2),
         color='#92400e', fontweight='bold')

all_lines = l1 + l2 + [l3] + [bars]
all_labels = [l.get_label() for l in all_lines]
ax1.legend(all_lines, all_labels, loc='center left', bbox_to_anchor=(0.02, 0.72), frameon=True, fontsize=8.5)

plt.title('Cuba: Dinámica Histórica - Suministro de Combustible ESTATAL vs Déficit (2015–2026)', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
c2_path = os.path.join(output_dir, "cuba_fuel_vs_deficit_2015_2025.png")
plt.savefig(c2_path, dpi=300)
plt.close()

# -------------------------------------------------------------
# CHART 3: Long-term Correlation & Renewable Shift (2015-2026)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

x_fuel = state_fuel_available
y_def = deficit_mw

corr_12y = np.corrcoef(x_fuel, y_def)[0, 1]
p_fit = np.polyfit(x_fuel, y_def, 2)
x_line = np.linspace(30000, 150000, 100)
y_pred_poly = np.polyval(p_fit, x_line)

ax1.scatter(x_fuel, y_def, color='#1f77b4', s=100, zorder=5)
ax1.plot(x_line, y_pred_poly, color='#e11d48', linestyle='--', linewidth=2, 
         label=f'Ajuste Polinómico (Efecto Umbral)\nCorr lineal r = {corr_12y:.2f}')

for i, y in enumerate(years):
    ax1.annotate(str(y), (x_fuel[i], y_def[i]), xytext=(6, -2), textcoords='offset points', fontweight='bold', fontsize=9)

ax1.set_title('Efecto Umbral: Combustible vs Apagones (2015–2026)\n(Sobre 110,000 BPD déficit = 0; por debajo se dispara)', fontsize=11, fontweight='bold')
ax1.set_xlabel('Combustible Total Disponible (BPD)', fontsize=10)
ax1.set_ylabel('Déficit Pico de Generación (MW)', fontsize=10)
ax1.axvline(110000, color='gray', linestyle=':', alpha=0.7)
ax1.legend(loc='upper right', frameon=True)
ax1.grid(True, linestyle='--', alpha=0.5)

# Renewable Generation Shift
ax2.plot(years, biomass_gwh, marker='s', color='#8b5cf6', linewidth=2, label='Biomasa Cañera (Bagazo)')
ax2.plot(years, solar_gwh, marker='o', color='#f59e0b', linewidth=2, label='Solar Fotovoltaica')
ax2.plot(years, hydro_gwh, marker='^', color='#06b6d4', linewidth=1.5, label='Hidroeléctrica')
ax2.plot(years, total_renewables_gwh, marker='D', color='#10b981', linewidth=2.5, linestyle='--', label='Total Renovable (GWh)')

ax2.set_title('Evolución de Fuentes Renovables (2015–2026)\n[Expansión solar 2026 vs declive de bioeléctricas]', fontsize=11, fontweight='bold')
ax2.set_xlabel('Año', fontsize=10)
ax2.set_ylabel('Generación (GWh)', fontsize=10)
ax2.set_ylim(0, 1300)
ax2.legend(loc='center right', frameon=True)
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
c3_path = os.path.join(output_dir, "cuba_longterm_correlation_2015_2025.png")
plt.savefig(c3_path, dpi=300)
plt.close()

print("All 2015-2026 historical charts updated successfully!")
