# engine_echo_data_viz

### Xinyuan Lin

I contributed the interactive map-based echogram visualization system in the [`mapapp/`](./mapapp/) folder. This includes both frontend and backend components to support real-time rendering of ocean acoustic data.

**Key contributions:**

- Developed a basemap viewer with selectable layers (standard, terrain, ocean)
- Enabled users to click on map trajectory points, select time ranges, and generate echograms dynamically
- Implemented trajectory highlighting based on user-selected time ranges
- Built the backend Flask API (`app.py`) and frontend logic (`app.js`) for dynamic echogram generation with custom Sv range and channel selection
- Set up benchmarking and multi-resolution resampling via `downsample.py` to support:
  - Low-resolution track data for lightweight map rendering
  - High-resolution echogram slices rendered on demand

The high-resolution and low-resolution datasets were processed using `downsample.py`, `downsample_highdensity.py` and integrated into the `mapapp/` folder for use by the map interface and echogram renderer.

**How to Run the Map App Locally**

To run the echogram map application on your local machine:

1. Download the high-resolution dataset `merged_60s.nc` (approx. 314MB) from the following link:  
[Download from Google Drive](https://drive.google.com/file/d/1GZg0OgjFfSqn3D24pGU2mcwDawWS7f4Z/view?usp=drive_link)

2. Place the file in the following directory:
`mapapp/merged_60s.nc`

3. In your terminal, navigate to the `mapapp/` folder and start the Flask server:
```bash
cd mapapp
python run.py
```


### Sasha Lai

Developed an interactive prototype for echogram-based region selection and export using Jupyter notebooks, located in the `region-browser/` directory. This tool supports both manual polygon annotation and the matching of pre-existing region labels to NOAA acoustic datasets.

- `region-browser/polygon_selection.ipynb`: Interactive tool for drawing and editing polygons on echograms

- `region-browser/match_region_labels_v1.ipynb`: Matches existing region label CSVs to their corresponding MVBS `.zarr` files on S3 based on `ping_time` overlap

- `region-browser/echogram_annotation_tool.ipynb`: Consolidated notebook combining interactive annotation, region matching, and export functionality

**Key contributions:**

- Real-time polygon drawing and editing on echograms using `PolyDraw` and `PolyEdit` tools with HoloViews/Panel integration

- Interactive loading of region label files and matching with corresponding MVBS datasets on S3

- Matching algorithm to link labeled regions with their source `.zarr` files based on `ping_time` range overlap 

- Export functionality for newly drawn region polygons with timestamped CSV output

- Real-time histogram visualizations and statistical summaries of Sv (volume backscattering strength) values within user-selected regions