#!/usr/bin/env python3
"""
LatticeSound 2D Installation Test Script

This script tests if all components are properly installed and working.
"""

import sys
import os
import subprocess

def test_python_dependencies():
    """Test if all Python dependencies are available."""
    print("Testing Python dependencies...")
    
    dependencies = ['numpy', 'matplotlib', 'sysv_ipc']
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  [OK] {dep}")
        except ImportError as e:
            print(f"  [FAIL] {dep}: {e}")
            return False
    
    return True

def test_c_executable():
    """Test if the C executable exists and is runnable."""
    print("Testing C executable...")
    
    # Check if executable exists in root directory
    if os.path.exists("C_Lattice"):
        print("  [OK] C_Lattice executable found in root directory")
    else:
        print("  [FAIL] C_Lattice executable not found in root directory")
        return False
    
    # Check if executable exists in lattice_sound_engine directory
    if os.path.exists("lattice_sound_engine/C_Lattice"):
        print("  [OK] C_Lattice executable found in lattice_sound_engine directory")
    else:
        print("  [FAIL] C_Lattice executable not found in lattice_sound_engine directory")
        return False
    
    return True

def test_configuration_file():
    """Test if configuration file exists."""
    print("Testing configuration file...")
    
    if os.path.exists("orchestrator/Starter.flsm"):
        print("  [OK] Starter.flsm configuration file found")
        return True
    else:
        print("  [FAIL] Starter.flsm configuration file not found")
        return False

def test_makefile():
    """Test if Makefile can be executed."""
    print("Testing Makefile...")
    
    try:
        result = subprocess.run(
            ["make", "-C", "lattice_sound_engine", "check-gsl"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  [OK] Makefile check-gsl target works")
            return True
        else:
            print(f"  [FAIL] Makefile check-gsl failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  [FAIL] Makefile check-gsl timed out")
        return False
    except FileNotFoundError:
        print("  [FAIL] make command not found")
        return False

def main():
    """Run all tests."""
    print("=== LatticeSound 2D Installation Test ===\n")
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("C Executable", test_c_executable),
        ("Configuration File", test_configuration_file),
        ("Makefile", test_makefile),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            print(f"  [OK] {test_name} test PASSED\n")
            passed += 1
        else:
            print(f"  [FAIL] {test_name} test FAILED\n")
    
    print("=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed. Installation appears to be successful.")
        print("\nYou can now run LatticeSound 2D with:")
        print("  python3 __main__.py")
        return 0
    else:
        print("Some tests failed. Please check the installation.")
        print("\nCommon solutions:")
        print("  - Run: ./install_linux.sh (for Linux)")
        print("  - Install missing dependencies")
        print("  - Check file permissions")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 