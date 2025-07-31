# Linux Compatibility Changes

This document summarizes the changes made to ensure LatticeSound 2D works properly on Linux systems.

## Changes Made

### 1. Updated Makefile (`lattice_sound_engine/Makefile`)

**Problem**: The original Makefile had hardcoded macOS Homebrew paths (`/opt/homebrew/Cellar/gsl/2.8/`).

**Solution**: 
- Removed hardcoded macOS paths
- Added automatic OS detection using `uname -s`
- Added support for `pkg-config` on Linux systems
- Added fallback paths for different macOS Homebrew installations
- Added `check-gsl` target for debugging GSL installation

**Key changes**:
```makefile
# Detect OS and set GSL paths accordingly
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    # macOS - try Homebrew paths
    ifeq ($(shell test -d /opt/homebrew/Cellar/gsl && echo "exists"),exists)
        CFLAGS += -I/opt/homebrew/Cellar/gsl/2.8/include
        LDFLAGS += -L/opt/homebrew/Cellar/gsl/2.8/lib
    else ifeq ($(shell test -d /usr/local/Cellar/gsl && echo "exists"),exists)
        CFLAGS += -I/usr/local/Cellar/gsl/2.8/include
        LDFLAGS += -L/usr/local/Cellar/gsl/2.8/lib
    endif
else ifeq ($(UNAME_S),Linux)
    # Linux - use pkg-config if available, otherwise use standard paths
    ifeq ($(shell pkg-config --exists gsl && echo "exists"),exists)
        CFLAGS += $(shell pkg-config --cflags gsl)
        LDFLAGS += $(shell pkg-config --libs gsl)
    endif
endif
```

### 2. Created Linux Requirements File (`linux-requirements.txt`)

**Problem**: The existing `mac-os-requirements.txt` contained macOS-specific package versions and paths.

**Solution**: Created a clean Linux requirements file with essential dependencies:
```
numpy>=1.20.0
matplotlib>=3.3.0
sysv-ipc>=1.1.0
tqdm>=4.60.0
```

### 3. Updated README.md

**Added sections**:
- Linux installation instructions
- Automated installation script usage
- Manual installation steps for different Linux distributions
- Linux-specific troubleshooting
- Installation testing instructions

### 4. Created Installation Script (`install_linux.sh`)

**Features**:
- Automatic Linux distribution detection
- Support for Ubuntu/Debian, CentOS/RHEL, Fedora, and Arch Linux
- Automatic system dependency installation
- Python dependency installation
- C code compilation
- Installation testing

**Usage**:
```bash
./install_linux.sh
```

### 5. Created Test Script (`test_installation.py`)

**Purpose**: Verify that all components are properly installed and working.

**Tests**:
- Python dependencies (numpy, matplotlib, sysv_ipc)
- C executable compilation
- Configuration files
- Makefile functionality

**Usage**:
```bash
python3 test_installation.py
```

## Linux System Requirements

### Supported Distributions
- Ubuntu/Debian
- CentOS/RHEL
- Fedora
- Arch Linux
- Other distributions (manual installation)

### Required System Packages
- `python3`
- `python3-pip`
- `python3-dev` (or `python3-devel`)
- `build-essential` (or equivalent)
- `libgsl-dev` (or `gsl-devel`)
- `pkg-config`

### Required Python Packages
- `numpy>=1.20.0`
- `matplotlib>=3.3.0`
- `sysv-ipc>=1.1.0`
- `tqdm>=4.60.0`

## Installation Methods

### Method 1: Automated Installation (Recommended)
```bash
./install_linux.sh
```

### Method 2: Manual Installation
1. Install system dependencies
2. Install Python dependencies: `pip3 install -r linux-requirements.txt`
3. Compile C code: `cd lattice_sound_engine && make`

## Verification

After installation, run the test script:
```bash
python3 test_installation.py
```

## Troubleshooting

### Common Issues

1. **GSL library not found**
   - Install: `sudo apt-get install libgsl-dev` (Ubuntu/Debian)
   - Install: `sudo yum install gsl-devel` (CentOS/RHEL)

2. **sysv_ipc import error**
   - Install: `pip3 install sysv-ipc`

3. **Permission errors**
   - Ensure proper file permissions
   - Don't run installation script as root

4. **Compilation errors**
   - Ensure all system dependencies are installed
   - Check that GSL is properly installed

## Backward Compatibility

All changes maintain backward compatibility with macOS:
- The Makefile automatically detects the OS and uses appropriate paths
- The installation script only runs on Linux systems
- All existing functionality is preserved
- Configuration files and output formats remain unchanged

## Files Modified/Created

### Modified Files
- `lattice_sound_engine/Makefile` - Added OS detection and Linux support
- `README.md` - Added Linux installation instructions

### New Files
- `linux-requirements.txt` - Linux Python dependencies
- `install_linux.sh` - Automated Linux installation script
- `test_installation.py` - Installation verification script
- `LINUX_COMPATIBILITY.md` - This documentation file 