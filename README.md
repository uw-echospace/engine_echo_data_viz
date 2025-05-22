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
python app.py

