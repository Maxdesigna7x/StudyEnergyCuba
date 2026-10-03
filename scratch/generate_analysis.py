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
    "/home/randy/.gemini/antigravity/brain/d2701034-be2e-4caa-b2c3-bb906091a59a",
    "/home/randy/Game_Dev/3d/assets"
]
for d in output_dirs:
    os.makedirs(d, exist_ok=True)

years = np.array([2020, 2021, 2022, 2023, 2024, 2025, 2026])

# Importaciones Estatales para el Gobierno / SEN (BPD)
vzla = np.array([62000, 56000, 53500, 55000, 33500, 11000, 1500])
mexico = np.array([0, 0, 1000, 18500, 20000, 13000, 2500])
russia = np.array([1500, 2000, 4500, 5500, 5500, 3500, 2000])
others = np.array([3500, 3000, 2500, 2000, 1500, 1500, 1500])

state_imports = vzla + mexico + russia + others
domestic_crude = np.array([42000, 38000, 36000, 34000, 32000, 30000, 28000])

# Combustible REAL que tiene el Gobierno / SEN para la red nacional (BPD)
state_fuel_available = state_imports + domestic_crude

# Importaciones privadas no estatales de EE.UU. (destilados ligeros para MIPYMES / privados)
usa_private = np.array([0, 0, 0, 0, 0, 0, 32000])

# Total país incluyendo el sector privado
total_country_fuel = state_fuel_available + usa_private

# Déficit en MW - Promedios oficiales auditados de la UNE (2020-2026)
deficit_mw = np.array([150, 53, 596, 196, 777, 1571, 1914])

# -------------------------------------------------------------
# CHART 1: Importaciones Estado vs Sector Privado
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors = ['#dc2626', '#16a34a', '#1e40af', '#94a3b8', '#0284c7']

ax1.bar(years, vzla, label='Venezuela (PDVSA)', color=colors[0], width=0.58)
ax1.bar(years, mexico, bottom=vzla, label='México (PEMEX)', color=colors[1], width=0.58)
ax1.bar(years, russia, bottom=vzla+mexico, label='Rusia (Urals/Deriv.)', color=colors[2], width=0.58)
ax1.bar(years, others, bottom=vzla+mexico+russia, label='Otros (Spot)', color=colors[3], width=0.58)
ax1.bar(years, usa_private, bottom=vzla+mexico+russia+others, label='EE.UU. (Sector Privado / MIPYMES)', color=colors[4], hatch='//', width=0.58)

ax1.set_title('Importaciones de Combustible a Cuba (2020–2026 YTD)\n[Diferenciando Sector Estatal vs Sector Privado]', fontsize=11, fontweight='bold', pad=12)
ax1.set_ylabel('Barriles por Día (BPD)', fontsize=10)
ax1.set_xlabel('Año', fontsize=10)
ax1.set_ylim(0, 100000)

for y, s_tot, p_tot in zip(years, state_imports, usa_private):
    if p_tot > 0:
        ax1.annotate(f'Estatal: {s_tot:,}\nPrivado: {p_tot:,}', xy=(y, s_tot + p_tot), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=7.5, fontweight='bold')
    else:
        ax1.annotate(f'{s_tot:,} bpd', xy=(y, s_tot), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

ax1.legend(loc='upper right', frameon=True, fontsize=8.5)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Percentage share estatal vs privado
total_imp_all = state_imports + usa_private
vzla_pct = (vzla / total_imp_all) * 100
mex_pct = (mexico / total_imp_all) * 100
rus_pct = (russia / total_imp_all) * 100
oth_pct = (others / total_imp_all) * 100
usa_pct = (usa_private / total_imp_all) * 100

ax2.bar(years, vzla_pct, label='Venezuela %', color=colors[0], width=0.58)
ax2.bar(years, mex_pct, bottom=vzla_pct, label='México %', color=colors[1], width=0.58)
ax2.bar(years, rus_pct, bottom=vzla_pct+mex_pct, label='Rusia %', color=colors[2], width=0.58)
ax2.bar(years, oth_pct, bottom=vzla_pct+mex_pct+rus_pct, label='Otros %', color=colors[3], width=0.58)
ax2.bar(years, usa_pct, bottom=vzla_pct+mex_pct+rus_pct+oth_pct, label='EE.UU. (Privado) %', color=colors[4], hatch='//', width=0.58)

ax2.set_title('Evolución del Share de Proveedores (2020–2026 YTD)\n[% del Total Importado]', fontsize=11, fontweight='bold', pad=12)
ax2.set_ylabel('Participación Porcentual (%)', fontsize=10)
ax2.set_ylim(0, 100)
ax2.legend(loc='lower left', frameon=True, fontsize=8.5)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
for d in output_dirs:
    plt.savefig(os.path.join(d, "cuba_fuel_imports_by_country.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# CHART 2: Combustible REAL del Gobierno vs Déficit
# -------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(13.5, 6))
ax2 = ax1.twinx()

# Línea 1: Combustible Total Estatal Disponible para el Gobierno / SEN (Crudo Nacional + Importaciones)
l1 = ax1.plot(years, state_fuel_available, marker='o', color='#2563eb', linewidth=2.8, 
              label='Combustible Total Estatal Disponible (Nacional + Importado para el Gobierno)')

# Línea 2: Total Importaciones Vendidas / Entregadas al Gobierno desde el Exterior (Venezuela, México, Rusia, etc.)
l2 = ax1.plot(years, state_imports, marker='s', color='#0d9488', linewidth=2.2, linestyle='--',
              label='Total Importaciones Vendidas/Entregadas al Gobierno (Suministro Aliados)')

# Barras de déficit
bars = ax2.bar(years, deficit_mw, width=0.35, color='#dc2626', alpha=0.6, label='Déficit Promedio Pico Eléctrico (MW - UNE)')

ax1.set_xlabel('Año', fontsize=11, fontweight='bold')
ax1.set_ylabel('Suministro de Petróleo Estatal (BPD)', fontsize=11, color='#2563eb', fontweight='bold')
ax2.set_ylabel('Déficit de Generación Pico (MW - UNE)', fontsize=11, color='#dc2626', fontweight='bold')

ax1.set_ylim(130000, 0) # Eje invertido (menor arriba, mayor abajo)
ax2.set_ylim(0, 2500)

# Anotación y etiquetas en 2026 para ambas líneas del Gobierno
ax1.scatter([2026], [state_fuel_available[6]], color='#2563eb', s=100, zorder=5)
ax1.scatter([2026], [state_imports[6]], color='#0d9488', s=100, zorder=5)

ax1.annotate('Total Estatal 2026: 35,500 BPD\n(28,000 nacional + 7,500 importado)\nExplica el récord de 2,100 MW', 
             xy=(2026, state_fuel_available[6]), xytext=(2023.1, 46000),
             arrowprops=dict(facecolor='#2563eb', arrowstyle='->', lw=1.5),
             bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.2),
             fontsize=8.5, fontweight='bold', color='#1e40af')

ax1.annotate('Total Vendido al Gobierno: 7,500 BPD\n(Mínimo histórico de aliados:\nVzla 1.5k, Méx 2.5k, Rus 2k)', 
             xy=(2026, state_imports[6]), xytext=(2023.2, 14000),
             arrowprops=dict(facecolor='#0d9488', arrowstyle='->', lw=1.5),
             bbox=dict(boxstyle="round,pad=0.4", fc="#f0fdfa", ec="#0d9488", lw=1.2),
             fontsize=8.5, fontweight='bold', color='#0f766e')

# Cuadro explicativo de exclusión de combustible privado
ax1.text(0.02, 0.95, 
         "⚠️ EXCLUSIÓN TRANSPARENTE: NO se cuenta el combustible refinado de EE.UU. (32,000 BPD en 2026)\n"
         "porque es importación privada para MIPYMES y transporte particular; NO se le vende al gobierno ni a termoeléctricas.",
         transform=ax1.transAxes, fontsize=8.2, verticalalignment='top',
         bbox=dict(boxstyle="round,pad=0.4", fc="#fffbeb", ec="#f59e0b", lw=1.2),
         color='#92400e', fontweight='bold')

all_lines = l1 + l2 + [bars]
all_labels = [l.get_label() for l in all_lines]
ax1.legend(all_lines, all_labels, loc='center left', bbox_to_anchor=(0.02, 0.72), frameon=True, fontsize=8.5)

plt.title('Cuba: Combustible ESTATAL en Manos del Gobierno vs Déficit de Generación (2020–2026 YTD)', fontsize=12, fontweight='bold', pad=15)
plt.tight_layout()
for d in output_dirs:
    plt.savefig(os.path.join(d, "cuba_fuel_vs_deficit.png"), dpi=300)
plt.close()


# -------------------------------------------------------------
# CHART 3: Correlación estricta con combustible estatal
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

x_state = state_fuel_available
y_def = deficit_mw

corr_state = np.corrcoef(x_state, y_def)[0, 1]
p_fit = np.polyfit(x_state, y_def, 1)

ax1.scatter(x_state, y_def, color='#2563eb', s=120, zorder=5)
x_line = np.linspace(30000, 120000, 100)
ax1.plot(x_line, np.polyval(p_fit, x_line), color='#f97316', linestyle='--', linewidth=2, 
         label=f'Ajuste Lineal Estatal\nCorr r = {corr_state:.2f}')

for i, y in enumerate(years):
    ax1.annotate(str(y), (x_state[i], y_def[i]), xytext=(7, -2), textcoords='offset points', fontweight='bold', fontsize=9.5)

ax1.set_title('Relación: Combustible ESTATAL Disponible vs Déficit\n(Sin contar combustible privado que no va a la red)', fontsize=11, fontweight='bold')
ax1.set_xlabel('Combustible Estatal Disponible para el Gobierno (BPD)', fontsize=10)
ax1.set_ylabel('Déficit Eléctrico Pico (MW)', fontsize=10)
ax1.legend(loc='upper right', frameon=True)
ax1.grid(True, linestyle='--', alpha=0.5)

# Panel 2: Desglose 2026
cat_2026 = ['Combustible Estatal\n(Gobierno/SEN)\n35,500 BPD', 'Ventas Privadas\n(MIPYMES EE.UU.)\n32,000 BPD', 'Demanda Diaria\nTotal del País\n110,000 BPD']
val_2026 = [35500, 32000, 110000]
col_2026 = ['#2563eb', '#0284c7', '#64748b']

bars2 = ax2.bar(cat_2026, val_2026, color=col_2026, width=0.5)
ax2.set_ylabel('Barriles por Día (BPD)', fontsize=10)
ax2.set_title('Desglose de Combustible en Cuba (2026 YTD):\n¿Por qué el país sigue en apagón?', fontsize=11, fontweight='bold')
for b, v in zip(bars2, val_2026):
    ax2.text(b.get_x() + b.get_width()/2, v + 2500, f'{v:,} BPD', ha='center', fontweight='bold', fontsize=9.5)

ax2.set_ylim(0, 130000)

plt.tight_layout()
for d in output_dirs:
    plt.savefig(os.path.join(d, "cuba_correlation_regression.png"), dpi=300)
plt.close()

print("Corrected charts generated successfully!")
