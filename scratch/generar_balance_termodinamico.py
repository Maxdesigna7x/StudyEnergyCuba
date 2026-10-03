import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

output_dirs = [
    "/home/randy/Game_Dev/3d/assets",
    "/home/randy/.gemini/antigravity/brain/d2701034-be2e-4caa-b2c3-bb906091a59a"
]

years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])

# 1. Total fuel available (BPD)
total_fuel_available = np.array([109000, 99000, 97500, 115000, 92500, 59000, 67500])

# 2. Electric generation total (GWh)
gen_total_gwh = np.array([19070.9, 17965.5, 15732.1, 15331.1, 14344.9, 12200.0, 11400.0])

# Non-oil generation (Gas natural Energas + Renovables)
gas_gwh = np.array([1500, 1450, 1400, 1350, 1300, 1250, 1200])
ren_gwh = np.array([880, 840, 780, 760, 810, 895, 1050])
solar_gwh = np.array([410, 430, 420, 440, 510, 620, 800])

# Thermal generation from oil/fuel (GWh)
gen_oil_gwh = gen_total_gwh - gas_gwh - ren_gwh

# Thermodynamic conversion factor:
# In Cuba, specific consumption is ~275 g/kWh, which corresponds to ~550 kWh generated per barrel of fuel (1.818 bbl / MWh)
bbl_per_mwh = 1.81818
fuel_needed_electric_bpd = (gen_oil_gwh * 1000 * bbl_per_mwh) / 365.0

# Remaining fuel for non-electric economy (transport, aviation, industry, bunker, re-export/losses)
fuel_remaining_bpd = total_fuel_available - fuel_needed_electric_bpd

# Deficit (MW)
deficit_mw = np.array([150, 520, 980, 880, 1350, 1950, 2100])

# -------------------------------------------------------------
# GRÁFICA 1: Balance Termodinámico (Combustible Eléctrico vs Resto)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5))

ax.bar(years, fuel_needed_electric_bpd, label='Combustible Consumido en Electricidad (BPD)', color='#2563eb', width=0.55)
ax.bar(years, fuel_remaining_bpd, bottom=fuel_needed_electric_bpd, 
       label='Combustible Restante (Transporte, Industria, GAESA / Reventa)', color='#d97706', width=0.55)
ax.plot(years, total_fuel_available, color='#0f172a', marker='o', linewidth=2.5, label='Combustible Total Disponible (BPD)')

# Anotación en 2023
ax.annotate('En 2023: 115k BPD disponibles\nSolo 65.8k BPD fueron a electricidad\n~49.2k BPD restantes\n¡Y aun así hubo 880 MW de apagones!',
            xy=(2023, 115000), xytext=(2020.8, 122000),
            arrowprops=dict(facecolor='#dc2626', arrowstyle='->', lw=1.5),
            bbox=dict(boxstyle="round,pad=0.4", fc="#fef2f2", ec="#dc2626", lw=1.2),
            fontsize=8.5, fontweight='bold', color='#991b1b')

# Anotación en 2025
ax.annotate('En 2025: Asfixia Total\nCasi todo el combustible (50k BPD)\nse fue a electricidad y apenas sobraron 8.9k BPD',
            xy=(2025, 59000), xytext=(2023.2, 38000),
            arrowprops=dict(facecolor='#0f172a', arrowstyle='->', lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#64748b", lw=1),
            fontsize=8, color='#334155')

ax.set_title('¿A dónde va el combustible? Balance entre Electricidad y Resto de la Economía\n(Cálculo termodinámico oficial a 550 kWh/barril)', fontsize=11, fontweight='bold', pad=12)
ax.set_ylabel('Barriles por Día (BPD)', fontsize=10)
ax.set_ylim(0, 140000)
ax.legend(loc='lower left', fontsize=8.5, frameon=True)
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
for d in output_dirs:
    plt.savefig(os.path.join(d, "cuba_balance_termodinamico.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# GRÁFICA 2: ¿Explica la Energía Solar la Caída de Combustible?
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Comparación 2024 vs 2025
fuel_drop_24_25 = total_fuel_available[4] - total_fuel_available[5] # 92500 - 59000 = 33500 BPD perdidos
solar_increase_gwh = solar_gwh[5] - solar_gwh[4] # 620 - 510 = 110 GWh
solar_bpd_saved = (solar_increase_gwh * 1000 * bbl_per_mwh) / 365.0 # ~548 BPD

# Bar chart de proporciones
categories = ['Combustible Perdido\n(-33,500 BPD)', 'Ahorro por Solar\n(+548 BPD)']
values = [fuel_drop_24_25, solar_bpd_saved]
colors_bar = ['#dc2626', '#16a34a']

bars = ax1.bar(categories, values, color=colors_bar, width=0.45)
ax1.set_ylabel('Barriles Diarios Equivalentes (BPD)', fontsize=10)
ax1.set_title('Comparación 2024 vs 2025:\n¿Se redujo el combustible por la energía solar?', fontsize=10.5, fontweight='bold')
ax1.set_ylim(0, 38000)

for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 900, f'{val:,.0f} BPD', ha='center', fontweight='bold', fontsize=9.5)

pct_solar = (solar_bpd_saved / fuel_drop_24_25) * 100
ax1.text(0.5, 20000, f'La solar solo explica el\n{pct_solar:.1f}% de la caída.\nEl 98.4% restante\nes déficit puro.', 
         ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", fc="#fffbeb", ec="#d97706", lw=1.2),
         fontsize=9.5, fontweight='bold', color='#b45309')

# Panel 2: Evolución de Ahorro Solar vs Pérdida de Petróleo acumulada desde 2020
fuel_loss_vs_2020 = total_fuel_available[0] - total_fuel_available
solar_total_savings_bpd = (solar_gwh * 1000 * bbl_per_mwh) / 365.0

ax2.plot(years, fuel_loss_vs_2020, marker='s', color='#dc2626', linewidth=2.2, label='Petróleo Perdido vs 2020 (BPD)')
ax2.plot(years, solar_total_savings_bpd, marker='o', color='#16a34a', linewidth=2.2, label='Aporte Total de Toda la Solar (BPD equiv)')

ax2.set_title('Evolución: Petróleo Perdido vs Ahorro Solar Total\n(2020–2026 YTD)', fontsize=10.5, fontweight='bold')
ax2.set_ylabel('Barriles Diarios (BPD)', fontsize=10)
ax2.legend(loc='center left', fontsize=8.5, frameon=True)
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
for d in output_dirs:
    plt.savefig(os.path.join(d, "cuba_solar_vs_fuel_drop.png"), dpi=300)
plt.close()

print("Thermodynamic & Solar balance charts created successfully!")
