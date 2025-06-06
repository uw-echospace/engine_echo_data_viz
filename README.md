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

Developed an interactive prototype for echogram-based region selection and export using Jupyter notebooks, located in the [`region-browser/`](region-browser) directory. This tool supports both manual polygon annotation and the matching of pre-existing region labels to NOAA acoustic datasets.

- [`region-browser/polygon_selection.ipynb`](region-browser/polygon_selection.ipynb): Interactive tool for drawing and editing polygons on echograms

- [`region-browser/match_region_labels_v1.ipynb`](region-browser/match_region_labels_v1.ipynb): Matches existing region label CSVs to their corresponding MVBS `.zarr` files on S3 based on `ping_time` overlap

- [`region-browser/echogram_annotation_tool.ipynb`](region-browser/echogram_annotation_tool.ipynb): Consolidated notebook combining interactive annotation, region matching, and export functionality

**Key contributions:**

- Real-time polygon drawing and editing on echograms using `PolyDraw` and `PolyEdit` tools with HoloViews/Panel integration

- Interactive loading of region label files and matching with corresponding MVBS datasets on S3

- Matching algorithm to link labeled regions with their source `.zarr` files based on `ping_time` range overlap 

- Export functionality for newly drawn region polygons with timestamped CSV output

- Real-time histogram visualizations and statistical summaries of Sv (volume backscattering strength) values within user-selected regions

### Siyu Meng
I mainly contributed to the echshader package by fixing existing bugs, improving code robustness, and adding new features.

**Key contributions:**

- [Resolve pandas version conflict](https://github.com/OSOceanAcoustics/echoshader/pull/183): I update DataFrame processing to align with pandas API changes. Therefore, echoshader can support pandas versions greater than 2.0.

- [Check the input dataset](https://github.com/OSOceanAcoustics/echoshader/pull/185): Add input validation to ensure that users provide the correct type of dataset.

- [Generate 3D curtain by plotly](https://github.com/OSOceanAcoustics/echoshader/pull/192): Upgrade the curtain plot method in the echoshader package. This was previously drawn using pyvista, which was relatively crude and could only be used for simple observation. I upgraded it using plotly, and the image is more intuitive and you can see the specific coordinate information. In addition, the rendering time was reduced by around 50%.
- 

### Ethan Takahashi
I contributed to the frontend code and the option to display multiple sources of data simultaneously in the [`multi-track](./multi-track/) folder.
** Key Contributions**

- Utilized maplibre-gl to display geospatial context for ship data.
- Modified display to allow multiple data sources to be displayed simultaneously.
- Add toggleable and individually controllable buttons for each specific data source.
