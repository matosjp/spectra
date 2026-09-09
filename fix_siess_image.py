import matplotlib.pyplot as plt
import matplotlib.image as mpimg

img_path = 'publishing/mnras_paper/figures/isocfit_results_siess.png'
img = mpimg.imread(img_path)

# 3600 x 2400
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.imshow(img)
ax.axis('off')

# Cover the title
plt.text(1800, 50, "Isochrone Fitting Results (Mass)", 
         fontsize=20, fontweight='bold', ha='center', va='center',
         bbox=dict(facecolor='white', edgecolor='white', pad=20))

# Cover the y-axis label (left side)
plt.text(50, 1200, "Calculated Mass ($M_\\odot$)", 
         fontsize=14, fontweight='bold', ha='center', va='center', rotation=90,
         bbox=dict(facecolor='white', edgecolor='white', pad=20))

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig('publishing/mnras_paper/figures/isocfit_results_siess.png', bbox_inches='tight', pad_inches=0, dpi=300)
