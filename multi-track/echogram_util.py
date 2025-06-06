#!/usr/bin/env python
"""
Echogram Batch Processing Tool - Used to generate echogram images in bulk
"""

import os
import argparse
import matplotlib.pyplot as plt
from data_processor import MVBSProcessor
from data_processor import MVBSManager
from multiprocessing import Pool, cpu_count
import numpy as np
import tqdm
import json

def process_point(args):
    """Process a single echogram point - used for parallel processing"""
    point_index, channel_index, config = args
    
    files = ["x0001.zarr", "x0002.zarr", "x0003.zarr"]
    manager = MVBSManager(files)
    processor = manager.processors[0]
    #processor = MVBSProcessor(config['data_file'])
    output_path = os.path.join(
        config['output_dir'], 
        f"echogram_point{point_index:04d}_channel{channel_index}.png"
    )
    
    try:
        processor.plot_echogram(
            point_index=point_index,
            channel_index=channel_index,
            vmin=config['vmin'],
            vmax=config['vmax'],
            save_path=output_path
        )
        processor.close()
        return True
    except Exception as e:
        print(f"Error processing point {point_index}, channel {channel_index}: {e}")
        processor.close()
        return False

def generate_echograms(data_file, output_dir, channels=None, points=None, 
                      step=1, vmin=-80, vmax=-30, workers=None):
    """
    Generate a series of echograms
    
    Args:
        data_file (str): Path to NetCDF data file
        output_dir (str): Output directory for images
        channels (list, optional): List of channel indices to process (default: all)
        points (list, optional): List of ping point indices to process (default: all)
        step (int): Step size between pings (default: 1)
        vmin (float): Minimum value for color scale
        vmax (float): Maximum value for color scale
        workers (int, optional): Number of parallel workers (default: CPU cores - 1)
    
    Returns:
        int: Number of successfully generated echograms
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load dataset and get metadata
    processor = MVBSProcessor(data_file)
    total_channels = len(processor.dataset.channel)
    total_points = len(processor.dataset.ping_time)
    
    # Save dataset summary
    summary = processor.get_summary()
    with open(os.path.join(output_dir, 'dataset_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Determine channels to process
    if channels is None:
        channels = list(range(total_channels))
    else:
        channels = [c for c in channels if 0 <= c < total_channels]
    
    # Determine points to process
    if points is None:
        points = list(range(0, total_points, step))
    else:
        points = [p for p in points if 0 <= p < total_points]
    
    processor.close()
    
    print(f"Generating echograms for {len(points)} points across {len(channels)} channels.")
    
    # Build task list
    tasks = []
    for point_index in points:
        for channel_index in channels:
            tasks.append((
                point_index, 
                channel_index, 
                {
                    'data_file': data_file,
                    'output_dir': output_dir,
                    'vmin': vmin,
                    'vmax': vmax
                }
            ))
    
    # Determine number of workers
    if workers is None:
        workers = max(1, cpu_count() - 1)
    
    # Run in parallel using process pool
    successful = 0
    with Pool(processes=workers) as pool:
        results = list(tqdm.tqdm(
            pool.imap(process_point, tasks),
            total=len(tasks),
            desc="Generating Echograms"
        ))
        successful = sum(results)
    
    print(f"Done! Successfully generated {successful}/{len(tasks)} echograms.")
    return successful

def generate_video_frames(data_file, output_dir, channel_index=0, 
                         vmin=-80, vmax=-30, format='png'):
    """
    Generate echogram frames for all points in a specific channel for video creation
    
    Args:
        data_file (str): Path to NetCDF data file
        output_dir (str): Output directory
        channel_index (int): Channel index to process
        vmin (float): Minimum color scale value
        vmax (float): Maximum color scale value
        format (str): Output image format (default: png)
    
    Returns:
        int: Number of successfully generated frames
    """
    frames_dir = os.path.join(output_dir, f'channel{channel_index}_frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    processor = MVBSProcessor(data_file)
    total_points = len(processor.dataset.ping_time)
    channel_name = processor.dataset.channel.values[channel_index]
    
    print(f"Generating {total_points} frames for channel {channel_name}")
    
    successful = 0
    for point_index in tqdm.tqdm(range(total_points), desc="Generating Video Frames"):
        try:
            output_path = os.path.join(frames_dir, f"frame_{point_index:04d}.{format}")
            processor.plot_echogram(
                point_index=point_index,
                channel_index=channel_index,
                vmin=vmin,
                vmax=vmax,
                save_path=output_path
            )
            successful += 1
        except Exception as e:
            print(f"Error processing frame {point_index}: {e}")
    
    processor.close()
    print(f"Done! Successfully generated {successful}/{total_points} frames.")
    
    print("\nTo create a video, you can use the following FFmpeg command:")
    print(f"ffmpeg -framerate 10 -i {frames_dir}/frame_%04d.{format} -c:v libx264 -pix_fmt yuv420p -crf 23 {output_dir}/channel{channel_index}_echogram.mp4")
    
    return successful

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Echogram Batch Processing Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Batch generation command
    batch_parser = subparsers.add_parser("batch", help="Generate echograms in batch")
    batch_parser.add_argument("data_file", help="Path to NetCDF data file")
    batch_parser.add_argument("output_dir", help="Output directory")
    batch_parser.add_argument("--channels", type=int, nargs="+", help="List of channel indices to process")
    batch_parser.add_argument("--points", type=int, nargs="+", help="List of point indices to process")
    batch_parser.add_argument("--step", type=int, default=10, help="Index step (default: 10)")
    batch_parser.add_argument("--vmin", type=float, default=-80, help="Minimum color scale value")
    batch_parser.add_argument("--vmax", type=float, default=-30, help="Maximum color scale value")
    batch_parser.add_argument("--workers", type=int, help="Number of parallel workers")
    
    # Video frame generation command
    video_parser = subparsers.add_parser("video", help="Generate echogram video frames")
    video_parser.add_argument("data_file", help="Path to NetCDF data file")
    video_parser.add_argument("output_dir", help="Output directory")
    video_parser.add_argument("--channel", type=int, default=0, help="Channel index to process")
    video_parser.add_argument("--vmin", type=float, default=-80, help="Minimum color scale value")
    video_parser.add_argument("--vmax", type=float, default=-30, help="Maximum color scale value")
    video_parser.add_argument("--format", choices=["png", "jpg"], default="png", help="Image format for output")
    
    args = parser.parse_args()
    
    if args.command == "batch":
        generate_echograms(
            data_file=args.data_file,
            output_dir=args.output_dir,
            channels=args.channels,
            points=args.points,
            step=args.step,
            vmin=args.vmin,
            vmax=args.vmax,
            workers=args.workers
        )
    elif args.command == "video":
        generate_video_frames(
            data_file=args.data_file,
            output_dir=args.output_dir,
            channel_index=args.channel,
            vmin=args.vmin,
            vmax=args.vmax,
            format=args.format
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
