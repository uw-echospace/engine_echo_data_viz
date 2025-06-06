import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class MVBSProcessor:
    """Tool class for processing MVBS (Mean Volume Backscattering Strength) data"""
    
    def __init__(self, file_path):
        """
        Initialize the processor
        
        Args:
            file_path (str): Path to MVBS NetCDF file
        """
        self.file_path = file_path
        self.dataset = None
        self.load_dataset()
    
    def load_dataset(self):
        """Load MVBS dataset"""
        self.dataset = xr.open_zarr(self.file_path)
        print(f"Loaded dataset: {self.file_path}")
        print(f"Dataset dimensions: {dict(self.dataset.dims)}")
        return self.dataset
    
    def get_summary(self):
        """Get basic summary info of the dataset"""
        if self.dataset is None:
            return "Dataset not loaded"
        
        summary = {
            "Time Range": [
                str(self.dataset.ping_time.values[0]),
                str(self.dataset.ping_time.values[-1])
            ],
            "Longitude Range": [
                float(self.dataset.longitude.min().values),
                float(self.dataset.longitude.max().values)
            ],
            "Latitude Range": [
                float(self.dataset.latitude.min().values),
                float(self.dataset.latitude.max().values)
            ],
            "Depth Range": [
                float(self.dataset.depth.min().values),
                float(self.dataset.depth.max().values)
            ],
            "Sv Range": [
                float(self.dataset.Sv.min().values),
                float(self.dataset.Sv.max().values)
            ],
            "Channels": list(self.dataset.channel.values),
            "Ping Count": len(self.dataset.ping_time),
            "Depth Samples": len(self.dataset.depth)
        }
        return summary
    
    def extract_trajectory(self):
        """Extract ship trajectory information"""
        if self.dataset is None:
            return None
        
        trajectory = {
            "latitude": self.dataset.latitude.values.tolist(),
            "longitude": self.dataset.longitude.values.tolist(),
            "time": [str(t) for t in self.dataset.ping_time.values],
        }
        return trajectory
    
    def plot_echogram(self, point_index, channel_index, vmin=-80, vmax=-30, save_path=None):
        """Plot echogram and optionally save it to file"""
        if self.dataset is None:
            return None
        
        channel_name = self.dataset.channel.values[channel_index]
        time_point = self.dataset.ping_time.values[point_index]
        
        sv_data = self.dataset.Sv.sel(
            channel=channel_name, 
            ping_time=time_point
        ).values
        
        depths = self.dataset.depth.values
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(sv_data.reshape(1, -1), aspect='auto', cmap='jet', 
                       extent=[0, 1, depths[-1], depths[0]], vmin=vmin, vmax=vmax)
        
        ax.set_title(f"{channel_name} Echogram at {time_point}")
        ax.set_ylabel('Depth (m)')
        ax.set_xlabel('Position')
        
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Sv (dB re 1 m⁻¹)')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()
        
        return fig
    
    def export_transect(self, channel_index, depth_range=None, output_file=None):
        """Export transect data from a specific channel and optional depth range"""
        if self.dataset is None:
            return None
        
        channel_name = self.dataset.channel.values[channel_index]
        channel_data = self.dataset.Sv.sel(channel=channel_name)
        
        if depth_range:
            min_depth, max_depth = depth_range
            depth_mask = (self.dataset.depth >= min_depth) & (self.dataset.depth <= max_depth)
            channel_data = channel_data.sel(depth=self.dataset.depth[depth_mask])
        
        df = channel_data.to_dataframe().reset_index()
        
        if output_file:
            df.to_csv(output_file, index=False)
        
        return df
    
    def close(self):
        """Close dataset and release resources"""
        if self.dataset is not None:
            self.dataset.close()
            self.dataset = None
            print("Dataset closed.")

class MVBSManager:
    """Manages multiple MVBS processors"""
    
    def __init__(self, file_paths):
        self.processors = [MVBSProcessor("test_data/" + path) for path in file_paths]
    
    def extract_all_trajectories(self):
        all_trajectories = []
        for i, processor in enumerate(self.processors):
            traj = processor.extract_trajectory()
            traj['source'] = f"Dataset {i+1}"
            all_trajectories.append(traj)
        return all_trajectories
    
    def close_all(self):
        for processor in self.processors:
            processor.close()

def plot_trajectories_on_map(trajectories):
    """Plot multiple ship trajectories on a single map"""
    plt.figure(figsize=(10, 8))
    for traj in trajectories:
        plt.plot(traj['longitude'], traj['latitude'], marker='o', label=traj['source'])
    
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Ship Trajectories")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    files = ["x0001.zarr", "x0002.zarr", "x0003.zarr"]
    manager = MVBSManager(files)

    for processor in manager.processors:
        print("Summary: ", processor.get_summary())
        print("Trajectory: ", len(processor.extract_trajectory()["latitude"]))
        processor.plot_echogram(
            point_index=0,
            channel_index=0,
            save_path="sample_echogram.png"
        )
        processor.export_transect(
            channel_index=0,
            depth_range=(0, 500),
            output_file="transect_data.csv"
        )

    manager.close_all()
