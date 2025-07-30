#!/usr/bin/env python3
"""
LatticeSound 2D - Main Entry Point

This script serves as the main entry point for the LatticeSound 2D system.
It runs the LatticeSound Manager from the orchestrator directory.

Usage:
    python run_lattice_sound.py [config_file]

Arguments:
    config_file (optional): Path to configuration file (default: orchestrator/Starter.flsm)
"""

import sys
import os

# Add orchestrator directory to Python path
orchestrator_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orchestrator")
sys.path.insert(0, orchestrator_dir)

from LSM import LatticeSoundManager


def main():
    """Main entry point for LatticeSound 2D."""
    # Get config file from command line argument or use default
    config_file = sys.argv[1] if len(sys.argv) > 1 else "Starter.flsm"
    
    try:
        # Create and run the LatticeSound Manager
        lsm = LatticeSoundManager(config_file)
        lsm.run()
        print("LatticeSound 2D execution completed successfully!")
        
    except Exception as e:
        print(f"Error running LatticeSound 2D: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 