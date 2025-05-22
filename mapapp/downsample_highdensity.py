import os
import xarray as xr
import numpy as np

# PARAMETERS
interval = "60S"  # downsample to 60 seconds
input_dir = "/home/exouser/xylin01/noaa-2021"
output_path = "merged_60s.nc"

# Collect zarr files
zarr_files = [f for f in os.listdir(input_dir) if f.endswith(".zarr")]

datasets = []
for zarr_file in zarr_files:
    zarr_path = os.path.join(input_dir, zarr_file)
    print(f"Processing {zarr_path}...")
    
    ds = xr.open_zarr(zarr_path, consolidated=True)
    
    # Rename depth → echo_range
    if "depth" in ds.dims:
        ds = ds.rename({"depth": "echo_range"})
    if "depth" in ds.coords:
        ds = ds.rename({'depth': 'echo_range'})

    # Downsample
    ds_resampled = ds.resample(ping_time=interval).mean()

    datasets.append(ds_resampled)

print(f"\n✅ {len(datasets)} files downsampled. Merging...")

# Merge all downsampled datasets
ds_merged = xr.concat(datasets, dim="ping_time")

# Sort by ping_time
ds_merged = ds_merged.sortby("ping_time")

# Drop duplicate ping_time (keep first occurrence)
_, index = np.unique(ds_merged.ping_time, return_index=True)
ds_merged = ds_merged.isel(ping_time=index)

# Save merged netCDF
ds_merged.to_netcdf(output_path)
print(f"\n✅ Merged 60s downsampled dataset saved to: {output_path}")
