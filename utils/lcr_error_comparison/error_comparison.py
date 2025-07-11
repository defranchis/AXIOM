import pandas as pd
import matplotlib.pyplot as plt

# Paths to your data files
file1 = 'cv_sweep.txt'
file2 = 'cv_sweep_fast.txt'

def load_errors(fname):
    # Read the data, skip '#' lines, whitespace‐delimited, no header
    df = pd.read_csv(
        fname,
        comment='#',
        delim_whitespace=True,
        header=None
    )
    # Extract columns 5 (R_Err) and 7 (X_Err)
    return df.iloc[:, 4], df.iloc[:, 6]

# Load the two sets of error columns
r_err1, x_err1 = load_errors(file1)
r_err2, x_err2 = load_errors(file2)

# Check same length
if len(r_err1) != len(r_err2):
    raise ValueError("Files have different numbers of data rows")

# Per‐row comparison DataFrame
comparison = pd.DataFrame({
    'R_Err_file1': r_err1,
    'R_Err_file2': r_err2,
    'ΔR_Err': r_err2 - r_err1,
    'X_Err_file1': x_err1,
    'X_Err_file2': x_err2,
    'ΔX_Err': x_err2 - x_err1,
})

# Total sums
total_r1 = r_err1.sum()
total_r2 = r_err2.sum()
total_x1 = x_err1.sum()
total_x2 = x_err2.sum()

# Averages (means)
mean_r1 = r_err1.mean()
mean_r2 = r_err2.mean()
mean_x1 = x_err1.mean()
mean_x2 = x_err2.mean()

# Differences of sums and means
delta_total_r = total_r2 - total_r1
delta_total_x = total_x2 - total_x1
delta_mean_r = mean_r2 - mean_r1
delta_mean_x = mean_x2 - mean_x1

# Output
print("Per‑row error comparison (first 5 rows):")
print(comparison.head().to_string(index=False))

print("\nTotal summed errors:")
print(f"  File 1  →  ΣR_Err = {total_r1:.6e},  ΣX_Err = {total_x1:.6e}")
print(f"  File 2  →  ΣR_Err = {total_r2:.6e},  ΣX_Err = {total_x2:.6e}")
print(f"  ΔΣR_Err = {delta_total_r:.6e}")
print(f"  ΔΣX_Err = {delta_total_x:.6e}")

print("\nAverage (mean) errors:")
print(f"  File 1  →  μR_Err = {mean_r1:.6e},  μX_Err = {mean_x1:.6e}")
print(f"  File 2  →  μR_Err = {mean_r2:.6e},  μX_Err = {mean_x2:.6e}")
print(f"  ΔμR_Err = {delta_mean_r:.6e}")
print(f"  ΔμX_Err = {delta_mean_x:.6e}")

# Optionally save per-row comparison
comparison.to_csv('error_comparison.csv', index=False)
print("\nFull per-row comparison saved to 'error_comparison.csv'")

# Plot errors
plt.figure(figsize=(10, 6))
plt.plot(r_err1, label='R_Err File 1', marker='o', linestyle='-', alpha=0.7)
plt.plot(r_err2, label='R_Err File 2', marker='o', linestyle='-', alpha=0.7)
plt.plot(x_err1, label='X_Err File 1', marker='x', linestyle='--', alpha=0.7)
plt.plot(x_err2, label='X_Err File 2', marker='x', linestyle='--', alpha=0.7)
plt.xlabel('Row Index')
plt.ylabel('Error Value')
plt.title('Error Comparison Between Two Data Sources')
plt.legend()
plt.tight_layout()
# Plot the differences between errors
plt.figure(figsize=(10, 6))
plt.plot(comparison['ΔR_Err'], label='ΔR_Err (File2 - File1)', marker='o', linestyle='-', alpha=0.7)
plt.plot(comparison['ΔX_Err'], label='ΔX_Err (File2 - File1)', marker='x', linestyle='--', alpha=0.7)
plt.xlabel('Row Index')
plt.ylabel('Error Difference')
plt.title('Difference Between Errors (File2 - File1)')
plt.legend()
plt.tight_layout()
# Calculate and print the average difference between errors
avg_delta_r = comparison['ΔR_Err'].mean()
avg_delta_x = comparison['ΔX_Err'].mean()
print(f"\nAverage difference ΔR_Err (File2 - File1): {avg_delta_r:.6e}")
print(f"Average difference ΔX_Err (File2 - File1): {avg_delta_x:.6e}")

plt.show()