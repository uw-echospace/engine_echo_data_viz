from flask import Flask, jsonify, request, send_from_directory, make_response, send_file
import xarray as xr
import numpy as np
import os
import json
import echoshader  # Import echoshader
import panel as pn  # Panel is used to display echogram
from datetime import datetime
import warnings
from custom_json import NumpyJSONEncoder, preprocess_data, safe_json_dumps
import traceback  # To print detailed error logs
import pandas as pd
import time
# Ignore warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, static_folder='static')

# Global variables to store loaded data
# Store datasets by ID
data_cache = {} # {"dataset_id": xarray.Dataset}

# Ensure the static directory exists
OUTPUT_DIR = "static/echograms"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_datasets(dataset_id):
    if dataset_id in data_cache:
        return data_cache[dataset_id]
    try:
        start_time = time.time()
        path = f"data/2023/{dataset_id}.zarr"
        ds = xr.open_zarr(path).rename({"depth": "echo_range"})
        data_cache[dataset_id] = ds
        end_time = time.time()
        print(f"Loaded dataset: {dataset_id}")
        print(f"Processing Time: {end_time - start_time}")
        return ds
    except Exception as e:
        print(f"Error loading dataset {dataset_id}: {e}")
        return None
    
@app.route('/')
def index():
    """Provide the main page"""
    return send_from_directory('.', 'index.html')

@app.route("/api/datasets")
def get_datasets():
    """Provide list of available datasets"""
    try:
        dataset_list = [dataset.replace(".zarr", "") for dataset in os.listdir("data/2023") if dataset.endswith(".zarr")]
        return jsonify(dataset_list)
    except Exception as e:
        error_msg = f"Error fetching dataset list: {str(e)}"
        app.logger.error(error_msg)
        traceback.print_exc()  # Print full error traceback
        return jsonify({'error': error_msg}), 500

@app.route('/api/acoustic-data')
def get_acoustic_data():
    dataset_id = request.args.get('datasetId', 'default')
    ds = load_datasets(dataset_id).resample(ping_time="30Min").mean()

    if ds is None:
        return jsonify({"error": "Failed to load dataset"}), 500

    def replace_nan(arr):
        return [None if isinstance(val, float) and np.isnan(val) else val for val in arr]

    try:
        data = {
            'latitude': replace_nan(ds.latitude.values.tolist()),
            'longitude': replace_nan(ds.longitude.values.tolist()),
            'time': [str(t) for t in ds.ping_time.values],
            'channels': [str(c) for c in ds.channel.values],
            'echo_range': ds.echo_range.values.tolist()
        }
        response = make_response(safe_json_dumps(data))
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/echogram')
def get_echogram():
    try:
        start = time.time()
        dataset_id = request.args.get('datasetId', 'default')
        print(dataset_id)
        point_index = int(request.args.get('pointIndex', 0))
        channel_index = int(request.args.get('channelIndex', 0))
        vmin = float(request.args.get('vmin', -80))
        vmax = float(request.args.get('vmax', -30))
        start_time = request.args.get('startTime', None)
        end_time = request.args.get('endTime', None)

        ds = load_datasets(dataset_id)
        if ds is None:
            return jsonify({"error": "Unable to load dataset"}), 500

        channels = ds.channel.values
        if channel_index >= len(channels):
            return jsonify({"error": "Invalid channel index"}), 400

        channel_name = channels[channel_index]

        if start_time and end_time:
            start_time = pd.to_datetime(start_time)
            end_time = pd.to_datetime(end_time)
            ds_filtered = ds.sel(ping_time=slice(start_time, end_time))
        else:
            if point_index >= len(ds.ping_time):
                return jsonify({"error": "Invalid time index"}), 400
            ds_filtered = ds
            time_point = ds.ping_time.values[point_index]

        echogram = ds_filtered.eshader.echogram(
            channel=[channel_name],
            cmap=[
                "#FFFFFF", "#9F9F9F", "#5F5F5F", "#0000FF", "#00007F",
                "#00BF00", "#007F00", "#FFFF00", "#FF7F00", "#FF00BF",
                "#FF0000", "#A6533C", "#783C28"
            ],
            vmin=vmin,
            vmax=vmax
        )

        title = f"Echogram from {start_time} to {end_time} - Channel: {channel_name}" if start_time and end_time else f"Echogram at {str(time_point).split('.')[0]} - Channel: {channel_name}"

        layout = pn.Column(
            pn.pane.Markdown(f"# {title}"),
            pn.pane.Markdown(f"Sv range: {vmin} to {vmax} dB"),
            echogram
        )

        filename = f"echogram_{dataset_id}_{point_index}_{channel_index}_{vmin}_{vmax}"
        if start_time and end_time:
            filename += f"_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}"

        output_path = os.path.join(OUTPUT_DIR, f"{filename}.html")
        layout.save(output_path)

        end = time.time()
        print(f"Echogram generation time: {end - start}")

        return send_file(output_path, mimetype='text/html')

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)