import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

csv_path = "articles/tcc/Resultados/tabelas_com_binarias_backup_2023/Pleiades_mass-results.csv"
output_path = "publishing/mnras_paper/figures/isocfit_results_siess.png"

df = pd.read_csv(csv_path)

# Drop missing values
df = df.dropna(subset=['expected masses', 'masses', 'mass_e'])

# Create scatter plot
plt.figure(figsize=(8, 6))

# Plot error bars in background
plt.errorbar(df['expected masses'], df['masses'], yerr=df['mass_e'], fmt='none', ecolor='lightsteelblue', alpha=0.5, elinewidth=1, zorder=1)

# Plot scatter points on top
plt.scatter(df['expected masses'], df['masses'], color='steelblue', s=15, alpha=0.9, edgecolors='white', linewidths=0.5, zorder=2, label='Calculated Mass')

# Calculate metrics
r2 = r2_score(df['expected masses'], df['masses'])
rmse = np.sqrt(mean_squared_error(df['expected masses'], df['masses']))
mae = mean_absolute_error(df['expected masses'], df['masses'])

# Plot 1:1 line
min_val = min(df['expected masses'].min(), df['masses'].min())
max_val = max(df['expected masses'].max(), df['masses'].max())
plt.plot([min_val, max_val], [min_val, max_val], 'k--', label='1:1 Identity')

# Set labels and title
plt.xlabel("Reference Mass ($M_\odot$)", fontsize=12)
plt.ylabel("Calculated Mass ($M_\odot$)", fontsize=12)
plt.title(f"Validation on Pleiades Binaries\n$R^2 = {r2:.3f}$, $RMSE = {rmse:.3f}$, $MAE = {mae:.3f}$", fontsize=14)

plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()

# Save figure
plt.savefig(output_path, dpi=300)
print(f"Saved figure to {output_path}")
