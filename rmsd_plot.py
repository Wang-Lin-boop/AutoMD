#!/usr/bin/env python
"""
rmsd_plot.py - RMSD Time-Series Plotting Script for AutoTRJ
Part of AutoMD: https://github.com/Wang-Lin-boop/AutoMD

This script generates publication-quality RMSD time-series plots from CSV data
produced by Desmond's analyze_simulation.py.

Usage:
    python rmsd_plot.py -f <input.csv> -o <output_prefix> [-t <title>] [--total-time <ns>]

Author: AutoMD Development Team
"""

import argparse
import sys
import os

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"ERROR: Required package not found: {e}")
    print("Please ensure matplotlib and numpy are installed.")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Plot RMSD time-series from CSV data'
    )
    parser.add_argument(
        '-f', '--file', 
        required=True,
        help='Input CSV file from Desmond analyze_simulation'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output file prefix (will generate .png and .pdf)'
    )
    parser.add_argument(
        '-t', '--title',
        default='RMSD vs Time',
        help='Plot title (default: "RMSD vs Time")'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='Output resolution in DPI (default: 300)'
    )
    parser.add_argument(
        '--total-time',
        type=float,
        default=None,
        help='Total simulation time in ns (if provided, x-axis shows time in ns instead of frames)'
    )
    parser.add_argument(
        '--time-unit',
        choices=['ns', 'ps', 'frame'],
        default='ns',
        help='Time unit for x-axis when --total-time is provided (default: ns)'
    )
    return parser.parse_args()


def read_csv_data(filename):
    """
    Read RMSD data from CSV file.
    Expected format: Time/Frame, RMSD value(s)
    Returns time array and RMSD array.
    """
    time_data = []
    rmsd_data = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip header line if present
    start_idx = 0
    if lines and not lines[0].strip()[0].isdigit():
        start_idx = 1
    
    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue
        
        # Handle both comma and space-separated values
        if ',' in line:
            parts = line.split(',')
        else:
            parts = line.split()
        
        try:
            # First column is typically time/frame, second is RMSD
            if len(parts) >= 2:
                time_data.append(float(parts[0]))
                rmsd_data.append(float(parts[1]))
        except ValueError:
            continue
    
    return np.array(time_data), np.array(rmsd_data)


def calculate_statistics(rmsd_data):
    """Calculate basic statistics for RMSD data."""
    stats = {
        'mean': np.mean(rmsd_data),
        'std': np.std(rmsd_data),
        'min': np.min(rmsd_data),
        'max': np.max(rmsd_data),
        'median': np.median(rmsd_data)
    }
    return stats


def create_rmsd_plot(time_data, rmsd_data, output_prefix, title, dpi, time_unit, total_time=None):
    """Create and save RMSD time-series plot."""
    
    # Convert frame numbers to actual time if total_time is provided
    n_frames = len(time_data)
    if total_time is not None:
        # Calculate time per frame
        time_per_frame = total_time / (n_frames - 1) if n_frames > 1 else total_time
        time_data = np.arange(n_frames) * time_per_frame
        
        # Convert to ps if requested
        if time_unit == 'ps':
            time_data = time_data * 1000  # ns to ps
        
        x_label = f'Time ({time_unit})'
        time_range_str = f"{time_data[0]:.2f} - {time_data[-1]:.2f} {time_unit}"
    else:
        x_label = 'Frame'
        time_range_str = f"Frame 0 - {n_frames - 1}"
    
    # Calculate statistics
    stats = calculate_statistics(rmsd_data)
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), 
                                    gridspec_kw={'width_ratios': [3, 1]})
    
    # Main RMSD time-series plot
    ax1.plot(time_data, rmsd_data, color='#2E86AB', linewidth=0.8, alpha=0.9)
    ax1.axhline(y=stats['mean'], color='#E94F37', linestyle='--', 
                linewidth=1.5, label=f"Mean: {stats['mean']:.3f} A")
    ax1.fill_between(time_data, 
                     stats['mean'] - stats['std'], 
                     stats['mean'] + stats['std'],
                     alpha=0.2, color='#E94F37', 
                     label=f"Std Dev: {stats['std']:.3f} A")
    
    # Labels and formatting
    ax1.set_xlabel(x_label, fontsize=12)
    ax1.set_ylabel('RMSD (Angstrom)', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='-')
    ax1.set_xlim(time_data[0], time_data[-1])
    
    # RMSD distribution histogram
    ax2.hist(rmsd_data, bins=50, orientation='horizontal', 
             color='#2E86AB', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.axhline(y=stats['mean'], color='#E94F37', linestyle='--', linewidth=1.5)
    ax2.axhline(y=stats['median'], color='#28A745', linestyle=':', 
                linewidth=1.5, label=f"Median: {stats['median']:.3f} A")
    ax2.set_xlabel('Frequency', fontsize=12)
    ax2.set_ylabel('RMSD (Angstrom)', fontsize=12)
    ax2.set_title('Distribution', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3, linestyle='-')
    
    # Match y-axis limits
    y_min = min(rmsd_data) - 0.1 * (max(rmsd_data) - min(rmsd_data))
    y_max = max(rmsd_data) + 0.1 * (max(rmsd_data) - min(rmsd_data))
    ax1.set_ylim(y_min, y_max)
    ax2.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    
    # Save figures
    plt.savefig(f"{output_prefix}.png", dpi=dpi, bbox_inches='tight')
    plt.savefig(f"{output_prefix}.pdf", bbox_inches='tight')
    plt.close()
    
    return stats, time_range_str


def write_statistics(output_prefix, stats, n_frames, time_range_str, total_time=None):
    """Write statistics to a summary file."""
    with open(f"{output_prefix}_statistics.txt", 'w') as f:
        f.write("RMSD Analysis Statistics\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Number of frames: {n_frames}\n")
        if total_time is not None:
            f.write(f"Total simulation time: {total_time} ns\n")
            time_per_frame = total_time / (n_frames - 1) if n_frames > 1 else total_time
            f.write(f"Time per frame: {time_per_frame:.4f} ns ({time_per_frame * 1000:.2f} ps)\n")
        f.write(f"Time range: {time_range_str}\n\n")
        f.write("RMSD Statistics (Angstrom):\n")
        f.write("-" * 30 + "\n")
        f.write(f"  Mean:     {stats['mean']:.4f}\n")
        f.write(f"  Std Dev:  {stats['std']:.4f}\n")
        f.write(f"  Median:   {stats['median']:.4f}\n")
        f.write(f"  Min:      {stats['min']:.4f}\n")
        f.write(f"  Max:      {stats['max']:.4f}\n")
        f.write(f"  Range:    {stats['max'] - stats['min']:.4f}\n")


def main():
    args = parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.file):
        print(f"ERROR: Input file not found: {args.file}")
        sys.exit(1)
    
    print(f"Reading RMSD data from: {args.file}")
    time_data, rmsd_data = read_csv_data(args.file)
    
    if len(rmsd_data) == 0:
        print("ERROR: No valid data found in input file.")
        sys.exit(1)
    
    n_frames = len(rmsd_data)
    print(f"Found {n_frames} data points")
    
    if args.total_time:
        time_per_frame = args.total_time / (n_frames - 1) if n_frames > 1 else args.total_time
        print(f"Total simulation time: {args.total_time} ns")
        print(f"Time per frame: {time_per_frame:.4f} ns ({time_per_frame * 1000:.2f} ps)")
    
    print(f"Generating plot: {args.output}.png")
    
    stats, time_range_str = create_rmsd_plot(
        time_data, rmsd_data, 
        args.output, args.title, 
        args.dpi, args.time_unit,
        args.total_time
    )
    
    write_statistics(args.output, stats, n_frames, time_range_str, args.total_time)
    
    print(f"\nRMSD Statistics:")
    print(f"  Mean:   {stats['mean']:.4f} A")
    print(f"  Std:    {stats['std']:.4f} A")
    print(f"  Min:    {stats['min']:.4f} A")
    print(f"  Max:    {stats['max']:.4f} A")
    print(f"\nOutput files:")
    print(f"  {args.output}.png")
    print(f"  {args.output}.pdf")
    print(f"  {args.output}_statistics.txt")


if __name__ == '__main__':
    main()
