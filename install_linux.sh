#!/bin/bash

# LatticeSound 2D Linux Installation Script
# This script automates the installation process for Linux systems

set -e  # Exit on any error

echo "=== LatticeSound 2D Linux Installation ==="
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "Error: Could not detect Linux distribution"
    exit 1
fi

echo "Detected OS: $OS $VER"
echo ""

# Function to install dependencies based on distribution
install_dependencies() {
    echo "Installing system dependencies..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        echo "Using apt package manager..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-dev build-essential libgsl-dev pkg-config
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        echo "Using yum package manager..."
        sudo yum install -y python3 python3-pip python3-devel gcc gsl-devel pkgconfig
    elif [[ "$OS" == *"Fedora"* ]]; then
        echo "Using dnf package manager..."
        sudo dnf install -y python3 python3-pip python3-devel gcc gsl-devel pkgconfig
    elif [[ "$OS" == *"Arch"* ]]; then
        echo "Using pacman package manager..."
        sudo pacman -S --noconfirm python python-pip base-devel gsl pkg-config
    else
        echo "Warning: Unsupported distribution. Please install the following packages manually:"
        echo "  - python3, python3-pip, python3-dev"
        echo "  - build-essential (or equivalent)"
        echo "  - libgsl-dev (or gsl-devel)"
        echo "  - pkg-config"
        echo ""
        read -p "Press Enter to continue if you have installed the dependencies manually..."
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo "Installing Python dependencies..."
    pip3 install -r linux-requirements.txt
}

# Function to compile C code
compile_c_code() {
    echo "Compiling C engine..."
    cd lattice_sound_engine
    
    # Check if GSL is available
    if ! pkg-config --exists gsl; then
        echo "Warning: GSL not found via pkg-config. Trying to compile anyway..."
    fi
    
    make clean
    if make; then
        echo "C compilation successful!"
        make install
    else
        echo "Error: C compilation failed!"
        echo "Please ensure GSL is properly installed."
        exit 1
    fi
    
    cd ..
}

# Function to test installation
test_installation() {
    echo "Testing installation..."
    
    # Test Python imports
    python3 -c "import numpy; import matplotlib; import sysv_ipc; print('Python dependencies OK')"
    
    # Test C executable
    if [ -f "C_Lattice" ]; then
        echo "C executable found: OK"
    else
        echo "Warning: C executable not found in root directory"
    fi
    
    echo "Installation test completed!"
}

# Main installation process
main() {
    echo "Starting installation process..."
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        echo "Error: Please do not run this script as root"
        exit 1
    fi
    
    # Install system dependencies
    install_dependencies
    
    # Install Python dependencies
    install_python_deps
    
    # Compile C code
    compile_c_code
    
    # Test installation
    test_installation
    
    echo ""
    echo "=== Installation Complete! ==="
    echo ""
    echo "To run LatticeSound 2D:"
    echo "  python3 __main__.py"
    echo ""
    echo "Or from the orchestrator directory:"
    echo "  cd orchestrator"
    echo "  python3 LSM.py"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@" 