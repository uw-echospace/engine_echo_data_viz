# downsample data to 600S 
# rename dimension 'depth' to 'echo_range' for echogram generation

import os
import xarray as xr

interval = "600S"

# Firstly, need to download the NOAA data from agr230002-bucket01/hake_data/data_zarr/MVBS
# store these zarr files in input_dir
# downsample the data
input_dir = "noaa-2021"
output_dir = "downsampled-noaa-2021"
os.makedirs(output_dir, exist_ok=True)

zarr_files = [f for f in os.listdir(input_dir) if f.endswith(".zarr")]

for zarr_file in zarr_files:
    zarr_path = os.path.join(input_dir, zarr_file)
    print(f"Processing {zarr_path}...")
    
    ds = xr.open_zarr(zarr_path, consolidated=True)
    # resample
    ds_resampled = ds.resample(ping_time=interval).mean()
    if "depth" in ds_resampled.dims:
        ds_resampled = ds_resampled.rename({"depth": "echo_range"})
        if 'depth' in ds_resampled.coords:
            ds_resampled = ds_resampled.rename({'depth': 'echo_range'})


    output_filename = zarr_file.rstrip("/").replace(".zarr", "_600s.nc")
    output_path = os.path.join(output_dir, output_filename)
    ds_resampled.to_netcdf(output_path)
    print(f"save to {output_path}")



# merge resampled files into one netcdf
import xarray as xr
import os
import numpy as np

# set directory
nc_dir = "downsampled-noaa-2021"
nc_files = sorted([os.path.join(nc_dir, f) for f in os.listdir(nc_dir) if f.endswith(".nc")])

# set the first file's echo_range as reference
ref_ds = xr.open_dataset(nc_files[0])
ref_echo_range = ref_ds['echo_range'].values
ref_ds.close()

# filter files with same echo_range 
matching_files = []
for f in nc_files:
    try:
        ds = xr.open_dataset(f)
        if np.array_equal(ds['echo_range'].values, ref_echo_range):
            matching_files.append(f)
        ds.close()
    except Exception as e:
        print(f"?? Failed to read {f}: {e}")


print("? Matching files to be merged:")
for fname in matching_files:
    print(" -", os.path.basename(fname))

# merge the files
if matching_files:
    ds_merged = xr.open_mfdataset(matching_files, combine="by_coords")
    output_path = "mapapp/merged_600s_v2.nc"
    ds_merged.to_netcdf(output_path)
    print(f"\n Merged file saved to: {output_path}")
else:
    print("No matching files found with the same echo_range.")


   
