# LatticeSound 2D - New Repository Structure

This document describes the new organized repository structure for LatticeSound 2D.

## Repository Structure

```
LatticeSound2D_publ/
├── lattice_sound_engine/     # C code components
│   ├── C_Lattice.c
│   ├── C_Lattice_dif_sys.c
│   ├── C_Lattice_dif_sys.h
│   ├── C_Lattice_Worker.c
│   ├── C_Lattice_Worker.h
│   ├── h_shape.c
│   └── h_shape.h
├── orchestrator/             # Python orchestration code
│   ├── LSM.py               # Main LatticeSound Manager
│   ├── Py_Analyses.py       # Analysis and plotting
│   ├── LSM_Lib.py           # Library functions
│   └── Starter.flsm         # Configuration file
├── results/                 # Output directory
├── run_lattice_sound.py     # Main entry point
├── README_NEW_STRUCTURE.md  # This file
└── [other project files...]
```

## Installation

### Linux Installation

#### Option 1: Automated Installation (Recommended)
```bash
# Run the automated installation script
./install_linux.sh
```

#### Option 2: Manual Installation

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-dev build-essential libgsl-dev
   
   # CentOS/RHEL/Fedora
   sudo yum install python3 python3-pip python3-devel gcc gsl-devel
   # or for newer versions:
   sudo dnf install python3 python3-pip python3-devel gcc gsl-devel
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r linux-requirements.txt
   ```

3. **Compile the C engine:**
   ```bash
   cd lattice_sound_engine
   make
   ```

### macOS Installation

1. **Install Homebrew (if not already installed):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install system dependencies:**
   ```bash
   brew install gsl
   ```

3. **Install Python dependencies:**
   ```bash
   pip3 install -r mac-os-requirements.txt
   ```

4. **Compile the C engine:**
   ```bash
   cd lattice_sound_engine
   make
   ```

## Key Changes

### 1. **Separation of Concerns**
- **`lattice_sound_engine/`**: Contains all C code components for the computational engine
- **`orchestrator/`**: Contains all Python code for orchestration, analysis, and configuration

### 2. **Improved Organization**
- C code is isolated in its own directory for better compilation management
- Python code is organized in the orchestrator directory
- Configuration files are kept with the Python code that uses them

### 3. **New Entry Point**
- `run_lattice_sound.py` serves as the main entry point from the project root
- Provides a clean interface to run the system

## Usage

### Running the System

#### Option 1: Using the new entry point (Recommended)
```bash
# From the project root directory
python3 run_lattice_sound.py

# With custom config file
python3 run_lattice_sound.py path/to/config.flsm
```

#### Option 2: Running directly from orchestrator
```bash
# From the orchestrator directory
cd orchestrator
python3 LSM.py

# With custom config file
python3 LSM.py --config path/to/config.flsm
```

### Configuration

The system uses the `Starter.flsm` configuration file located in the `orchestrator/` directory. The configuration file contains:

- System dimensions and parameters
- Material properties
- Time settings
- Output configuration
- Plot settings

### Output

Results are saved to the `results/` directory in the project root. The system automatically:

1. Creates the output directory if it doesn't exist
2. Saves analysis results to `LS_result.txt`
3. Creates plots in `results/plots/` (if plotting is enabled)

## Development

### Adding New C Components

1. Place new C files in `lattice_sound_engine/`
2. Update the compilation command in `orchestrator/LSM.py` if needed
3. Ensure proper header file organization

### Adding New Python Components

1. Place new Python files in `orchestrator/`
2. Update imports and dependencies as needed
3. Consider adding new configuration options to `Starter.flsm`

### Modifying Configuration

1. Edit `orchestrator/Starter.flsm` for system parameters
2. The configuration parser handles semicolons and various data types automatically
3. Use the `--config` option to specify custom configuration files

## Benefits of the New Structure

1. **Clear Separation**: C and Python code are clearly separated
2. **Better Maintainability**: Each component has its own directory
3. **Easier Compilation**: C code compilation is isolated
4. **Improved Testing**: Components can be tested independently
5. **Better Documentation**: Structure is self-documenting
6. **Scalability**: Easy to add new components or modify existing ones

## Migration Notes

- The old `C_Lattice` executable in the root directory is kept for compatibility
- All existing functionality is preserved
- Configuration files work exactly as before
- Output directories and file formats remain unchanged

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory
2. **Compilation Errors**: Check that all C files are in `lattice_sound_engine/`
3. **Configuration Errors**: Verify the `Starter.flsm` file is in `orchestrator/`
4. **Output Directory**: The system automatically creates output directories

### Linux-Specific Issues

1. **GSL library not found**: Install `libgsl-dev` package
2. **sysv_ipc import error**: Install with `pip3 install sysv-ipc`
3. **Permission errors**: Ensure proper file permissions and try running with appropriate user privileges

### Testing Installation

After installation, you can test if everything is working correctly:

```bash
python3 test_installation.py
```

This will check:
- Python dependencies (numpy, matplotlib, sysv_ipc)
- C executable compilation
- Configuration files
- Makefile functionality

### Getting Help

- Check the original `README.txt` and `MANUAL.txt` for detailed usage information
- Review the `Starter.flsm` file for configuration options
- Examine the code comments for implementation details 

## License

This project is licensed under the GNU General Public License v3.0.  
See the [LICENSE](./LICENSE) file for details.

## Disclaimer

See [DISCLAIMER.md](./DISCLAIMER.md) for information about liability and responsible use.
