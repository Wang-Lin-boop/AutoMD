#!/usr/bin/env python
"""
hbond_analysis.py - Advanced Hydrogen Bond Analysis Script for AutoTRJ
Part of AutoMD: https://github.com/Wang-Lin-boop/AutoMD

This script performs comprehensive hydrogen bond analysis on MD trajectories,
including occupancy, lifetime, and distance/angle distribution analysis.

Usage:
    $SCHRODINGER/run hbond_analysis.py <cms_file> <trajectory> <asl1> <asl2> <output_prefix>

Features:
    - H-bond occupancy: percentage of frames each donor-acceptor pair forms H-bond
    - H-bond lifetime: average and maximum duration of each H-bond
    - Distance/angle distributions: histograms of D-A distance and D-H-A angle

Author: AutoMD Development Team
"""

import sys
import os
import argparse
from collections import defaultdict

# Schrodinger imports
try:
    from schrodinger import structure
    from schrodinger.application.desmond.packages import traj, topo, analysis
    from schrodinger.structutils import analyze
    import numpy as np
except ImportError as e:
    print(f"ERROR: Required Schrodinger modules not found: {e}")
    print("Please run this script using: $SCHRODINGER/run hbond_analysis.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    print("WARNING: matplotlib not available, plots will not be generated.")


# H-bond geometric criteria
HBOND_DISTANCE_CUTOFF = 3.5  # Angstrom (Donor-Acceptor distance)
HBOND_ANGLE_CUTOFF = 120.0   # Degrees (D-H-A angle minimum)


class HydrogenBond:
    """Class to represent a hydrogen bond."""
    def __init__(self, donor_atom, hydrogen_atom, acceptor_atom):
        self.donor = donor_atom
        self.hydrogen = hydrogen_atom
        self.acceptor = acceptor_atom
        self.donor_resname = donor_atom.pdbres.strip()
        self.donor_resnum = donor_atom.resnum
        self.donor_chain = donor_atom.chain
        self.acceptor_resname = acceptor_atom.pdbres.strip()
        self.acceptor_resnum = acceptor_atom.resnum
        self.acceptor_chain = acceptor_atom.chain
    
    @property
    def key(self):
        """Unique identifier for this H-bond type."""
        return (f"{self.donor_chain}:{self.donor_resname}{self.donor_resnum}:{self.donor.pdbname.strip()}-"
                f"{self.acceptor_chain}:{self.acceptor_resname}{self.acceptor_resnum}:{self.acceptor.pdbname.strip()}")
    
    @property
    def residue_pair(self):
        """Residue pair identifier."""
        return (f"{self.donor_chain}:{self.donor_resname}{self.donor_resnum}",
                f"{self.acceptor_chain}:{self.acceptor_resname}{self.acceptor_resnum}")


def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions."""
    return np.sqrt(np.sum((np.array(pos1) - np.array(pos2))**2))


def calculate_angle(pos1, pos2, pos3):
    """Calculate angle (in degrees) between three positions (pos1-pos2-pos3)."""
    v1 = np.array(pos1) - np.array(pos2)
    v2 = np.array(pos3) - np.array(pos2)
    
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    
    return np.degrees(np.arccos(cos_angle))


def get_potential_donors(st, asl):
    """
    Get potential H-bond donors (N-H, O-H) from structure based on ASL.
    Returns list of (donor_atom, hydrogen_atom) tuples.
    """
    donors = []
    atom_indices = analyze.evaluate_asl(st, asl)
    
    for idx in atom_indices:
        atom = st.atom[idx]
        # Check if atom could be a donor (N or O with attached H)
        if atom.element in ['N', 'O', 'S']:
            for bonded_atom in atom.bonded_atoms:
                if bonded_atom.element == 'H':
                    donors.append((atom, bonded_atom))
    
    return donors


def get_potential_acceptors(st, asl):
    """
    Get potential H-bond acceptors (N, O, S with lone pairs) from structure based on ASL.
    Returns list of acceptor atoms.
    """
    acceptors = []
    atom_indices = analyze.evaluate_asl(st, asl)
    
    for idx in atom_indices:
        atom = st.atom[idx]
        # Check if atom could be an acceptor (N, O, S)
        if atom.element in ['N', 'O', 'S']:
            acceptors.append(atom)
    
    return acceptors


def detect_hbonds_in_frame(st, donors, acceptors, frame_coords=None):
    """
    Detect hydrogen bonds in a single frame.
    Returns list of (HydrogenBond, distance, angle) tuples.
    """
    hbonds = []
    
    for donor, hydrogen in donors:
        donor_idx = donor.index - 1  # 0-based index
        h_idx = hydrogen.index - 1
        
        if frame_coords is not None:
            donor_pos = frame_coords[donor_idx]
            h_pos = frame_coords[h_idx]
        else:
            donor_pos = [donor.x, donor.y, donor.z]
            h_pos = [hydrogen.x, hydrogen.y, hydrogen.z]
        
        for acceptor in acceptors:
            # Skip if donor and acceptor are the same atom or same residue
            if donor.index == acceptor.index:
                continue
            if donor.resnum == acceptor.resnum and donor.chain == acceptor.chain:
                continue
            
            acceptor_idx = acceptor.index - 1
            
            if frame_coords is not None:
                acceptor_pos = frame_coords[acceptor_idx]
            else:
                acceptor_pos = [acceptor.x, acceptor.y, acceptor.z]
            
            # Check distance criterion (D-A distance)
            da_distance = calculate_distance(donor_pos, acceptor_pos)
            if da_distance > HBOND_DISTANCE_CUTOFF:
                continue
            
            # Check angle criterion (D-H-A angle)
            dha_angle = calculate_angle(donor_pos, h_pos, acceptor_pos)
            if dha_angle < HBOND_ANGLE_CUTOFF:
                continue
            
            # Valid H-bond found
            hb = HydrogenBond(donor, hydrogen, acceptor)
            hbonds.append((hb, da_distance, dha_angle))
    
    return hbonds


def analyze_trajectory(cms_file, trj_path, asl1, asl2, output_prefix):
    """
    Main function to analyze hydrogen bonds across trajectory.
    """
    print(f"Loading system from: {cms_file}")
    msys_model, cms_model = topo.read_cms(cms_file)
    
    print(f"Loading trajectory from: {trj_path}")
    trj_frames = traj.read_traj(trj_path)
    n_frames = len(trj_frames)
    print(f"Total frames: {n_frames}")
    
    # Get full system structure
    st = cms_model.fsys_ct
    
    # Get donors from ASL1 and acceptors from ASL2 (and vice versa for bidirectional)
    print(f"Finding donors/acceptors for ASL1: {asl1}")
    print(f"Finding donors/acceptors for ASL2: {asl2}")
    
    donors_1 = get_potential_donors(st, asl1)
    acceptors_1 = get_potential_acceptors(st, asl1)
    donors_2 = get_potential_donors(st, asl2)
    acceptors_2 = get_potential_acceptors(st, asl2)
    
    print(f"ASL1: {len(donors_1)} potential donors, {len(acceptors_1)} potential acceptors")
    print(f"ASL2: {len(donors_2)} potential donors, {len(acceptors_2)} potential acceptors")
    
    # Data storage
    hbond_frames = defaultdict(list)  # hbond_key -> list of frame indices
    all_distances = defaultdict(list)  # hbond_key -> list of distances
    all_angles = defaultdict(list)     # hbond_key -> list of angles
    global_distances = []  # All H-bond distances
    global_angles = []     # All H-bond angles
    
    print("\nAnalyzing frames...")
    for frame_idx, frame in enumerate(trj_frames):
        if frame_idx % 100 == 0:
            print(f"  Processing frame {frame_idx}/{n_frames}...")
        
        coords = frame.pos()
        
        # Detect H-bonds: ASL1 donors -> ASL2 acceptors
        hbonds_1to2 = detect_hbonds_in_frame(st, donors_1, acceptors_2, coords)
        
        # Detect H-bonds: ASL2 donors -> ASL1 acceptors
        hbonds_2to1 = detect_hbonds_in_frame(st, donors_2, acceptors_1, coords)
        
        # Combine results
        all_hbonds = hbonds_1to2 + hbonds_2to1
        
        for hb, dist, angle in all_hbonds:
            key = hb.key
            hbond_frames[key].append(frame_idx)
            all_distances[key].append(dist)
            all_angles[key].append(angle)
            global_distances.append(dist)
            global_angles.append(angle)
    
    print(f"\nFound {len(hbond_frames)} unique H-bond types")
    
    # Calculate statistics
    results = calculate_statistics(hbond_frames, all_distances, all_angles, n_frames)
    
    # Write outputs
    write_occupancy_csv(results, output_prefix, n_frames)
    write_lifetime_csv(results, output_prefix, n_frames)
    write_detailed_csv(results, output_prefix, n_frames)
    
    # Generate plots
    if plt is not None:
        plot_distributions(global_distances, global_angles, output_prefix)
        plot_occupancy_bar(results, output_prefix)
    
    print(f"\nAnalysis complete!")
    print(f"Output files generated with prefix: {output_prefix}")
    
    return results


def calculate_statistics(hbond_frames, all_distances, all_angles, n_frames):
    """Calculate occupancy and lifetime statistics for each H-bond."""
    results = []
    
    for key in hbond_frames:
        frames = sorted(hbond_frames[key])
        occupancy = len(frames) / n_frames * 100
        
        # Calculate lifetimes (consecutive frame stretches)
        lifetimes = []
        if frames:
            current_lifetime = 1
            for i in range(1, len(frames)):
                if frames[i] == frames[i-1] + 1:
                    current_lifetime += 1
                else:
                    lifetimes.append(current_lifetime)
                    current_lifetime = 1
            lifetimes.append(current_lifetime)
        
        avg_lifetime = np.mean(lifetimes) if lifetimes else 0
        max_lifetime = max(lifetimes) if lifetimes else 0
        
        # Distance and angle statistics
        distances = all_distances[key]
        angles = all_angles[key]
        
        results.append({
            'key': key,
            'occupancy': occupancy,
            'n_frames': len(frames),
            'avg_lifetime': avg_lifetime,
            'max_lifetime': max_lifetime,
            'n_events': len(lifetimes),
            'avg_distance': np.mean(distances),
            'std_distance': np.std(distances),
            'avg_angle': np.mean(angles),
            'std_angle': np.std(angles),
        })
    
    # Sort by occupancy (descending)
    results.sort(key=lambda x: x['occupancy'], reverse=True)
    
    return results


def write_occupancy_csv(results, output_prefix, n_frames):
    """Write H-bond occupancy data to CSV."""
    filename = f"{output_prefix}_occupancy.csv"
    with open(filename, 'w') as f:
        f.write("Rank,H-bond,Occupancy(%),Frames_Present,Total_Frames\n")
        for i, r in enumerate(results, 1):
            f.write(f"{i},{r['key']},{r['occupancy']:.2f},{r['n_frames']},{n_frames}\n")
    print(f"  Written: {filename}")


def write_lifetime_csv(results, output_prefix, n_frames):
    """Write H-bond lifetime data to CSV."""
    filename = f"{output_prefix}_lifetime.csv"
    with open(filename, 'w') as f:
        f.write("Rank,H-bond,Avg_Lifetime(frames),Max_Lifetime(frames),N_Events,Occupancy(%)\n")
        for i, r in enumerate(results, 1):
            f.write(f"{i},{r['key']},{r['avg_lifetime']:.2f},{r['max_lifetime']},{r['n_events']},{r['occupancy']:.2f}\n")
    print(f"  Written: {filename}")


def write_detailed_csv(results, output_prefix, n_frames):
    """Write detailed H-bond statistics to CSV."""
    filename = f"{output_prefix}_detailed.csv"
    with open(filename, 'w') as f:
        f.write("Rank,H-bond,Occupancy(%),Avg_Lifetime,Max_Lifetime,N_Events,")
        f.write("Avg_Distance(A),Std_Distance(A),Avg_Angle(deg),Std_Angle(deg)\n")
        for i, r in enumerate(results, 1):
            f.write(f"{i},{r['key']},{r['occupancy']:.2f},{r['avg_lifetime']:.2f},")
            f.write(f"{r['max_lifetime']},{r['n_events']},{r['avg_distance']:.3f},")
            f.write(f"{r['std_distance']:.3f},{r['avg_angle']:.2f},{r['std_angle']:.2f}\n")
    print(f"  Written: {filename}")


def plot_distributions(distances, angles, output_prefix):
    """Plot distance and angle distributions."""
    if not distances or not angles:
        print("  No H-bond data for distribution plots.")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Distance distribution
    ax1.hist(distances, bins=50, color='#2E86AB', edgecolor='black', alpha=0.7)
    ax1.axvline(np.mean(distances), color='#E94F37', linestyle='--', 
                linewidth=2, label=f"Mean: {np.mean(distances):.2f} A")
    ax1.set_xlabel('Donor-Acceptor Distance (A)', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('H-bond Distance Distribution', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Angle distribution
    ax2.hist(angles, bins=50, color='#28A745', edgecolor='black', alpha=0.7)
    ax2.axvline(np.mean(angles), color='#E94F37', linestyle='--', 
                linewidth=2, label=f"Mean: {np.mean(angles):.1f} deg")
    ax2.set_xlabel('D-H-A Angle (degrees)', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('H-bond Angle Distribution', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_distributions.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_distributions.pdf", bbox_inches='tight')
    plt.close()
    print(f"  Written: {output_prefix}_distributions.png/pdf")


def plot_occupancy_bar(results, output_prefix, top_n=20):
    """Plot top H-bonds by occupancy."""
    if not results:
        print("  No H-bond data for occupancy plot.")
        return
    
    # Get top N H-bonds
    top_results = results[:min(top_n, len(results))]
    
    # Shorten labels for display
    labels = []
    for r in top_results:
        key = r['key']
        # Simplify: "A:ALA123:N-B:GLU456:O" -> "ALA123-GLU456"
        parts = key.split('-')
        if len(parts) == 2:
            donor_parts = parts[0].split(':')
            acc_parts = parts[1].split(':')
            if len(donor_parts) >= 2 and len(acc_parts) >= 2:
                label = f"{donor_parts[1]}-{acc_parts[1]}"
            else:
                label = key[:30]
        else:
            label = key[:30]
        labels.append(label)
    
    occupancies = [r['occupancy'] for r in top_results]
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(labels) * 0.4)))
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, occupancies, color='#2E86AB', edgecolor='black', alpha=0.8)
    
    # Color bars by occupancy level
    for i, (bar, occ) in enumerate(zip(bars, occupancies)):
        if occ >= 50:
            bar.set_color('#28A745')  # Green for high occupancy
        elif occ >= 25:
            bar.set_color('#FFC107')  # Yellow for medium
        else:
            bar.set_color('#2E86AB')  # Blue for low
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Occupancy (%)', fontsize=12)
    ax.set_title(f'Top {len(labels)} Hydrogen Bonds by Occupancy', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (occ, bar) in enumerate(zip(occupancies, bars)):
        ax.text(occ + 1, i, f'{occ:.1f}%', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_occupancy.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_prefix}_occupancy.pdf", bbox_inches='tight')
    plt.close()
    print(f"  Written: {output_prefix}_occupancy.png/pdf")


def main():
    if len(sys.argv) != 6:
        print("Usage: $SCHRODINGER/run hbond_analysis.py <cms_file> <trajectory> <asl1> <asl2> <output_prefix>")
        print("\nExample:")
        print('  $SCHRODINGER/run hbond_analysis.py system-out.cms system_trj "protein" "ligand" hbond_analysis')
        sys.exit(1)
    
    cms_file = sys.argv[1]
    trj_path = sys.argv[2]
    asl1 = sys.argv[3]
    asl2 = sys.argv[4]
    output_prefix = sys.argv[5]
    
    # Validate inputs
    if not os.path.exists(cms_file):
        print(f"ERROR: CMS file not found: {cms_file}")
        sys.exit(1)
    
    if not os.path.exists(trj_path):
        print(f"ERROR: Trajectory not found: {trj_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Advanced Hydrogen Bond Analysis")
    print("=" * 60)
    print(f"CMS file:    {cms_file}")
    print(f"Trajectory:  {trj_path}")
    print(f"ASL 1:       {asl1}")
    print(f"ASL 2:       {asl2}")
    print(f"Output:      {output_prefix}_*")
    print(f"\nH-bond criteria:")
    print(f"  D-A distance cutoff: {HBOND_DISTANCE_CUTOFF} A")
    print(f"  D-H-A angle cutoff:  {HBOND_ANGLE_CUTOFF} degrees")
    print("=" * 60)
    
    analyze_trajectory(cms_file, trj_path, asl1, asl2, output_prefix)


if __name__ == '__main__':
    main()
