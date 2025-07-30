# LatticeSound 2D open-source
#
# Copyright (C) 2025  Giorgio Lo Presti (MPMpublic)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Lattice Sound Manager (LSM)

This script initializes the C_Lattice system, providing system dimensions and initial conditions.
It prepares shared memory slots for dynamic C codes through sysv_ipc and launches Py_Analyses
to analyze the system. Configuration is read from Starter.flsm and matrices are built using LSM_lib.

The oscillator is defined as: [xi, yi, zi, vxi, vyi, vzi]
The dual lattice is of type: [mu, km, gamm, 1]
All quantities are referenced to the "base element" quantities.

Memory Allocation: Prepares location and semaphores for multithreaded C_Lattice operations.
Memory size = system_dimension * 8 (double) * 2 (initial position and speed).
"""

import subprocess
import os
import sysv_ipc  # type: ignore for suppress warning
from multiprocessing import Process
import numpy as np
from LSM_Lib import build_lattice, insert_object_2D, TwoD_object, rectangle, ellipse, leng, elastic_const, mass, scale_back2D


class ConfigurationManager:
    """Manages configuration loading and parsing from Starter.flsm file."""
    
    def __init__(self, config_file="Starter.flsm"):
        # If config_file is a relative path, make it relative to orchestrator directory
        if not os.path.isabs(config_file):
            orchestrator_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_file = os.path.join(orchestrator_dir, config_file)
        else:
            self.config_file = config_file
        self.config = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load and parse configuration from Starter.flsm file."""
        try:
            with open(self.config_file, "r") as file:
                lines = file.readlines()
            
            self._parse_configuration_lines(lines)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found")
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")
    
    def _parse_configuration_lines(self, lines):
        """Parse configuration lines and extract parameters."""
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Parse basic parameters
            if "debug" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['debug'] = eval(value)
            elif "thread_num" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['thread_num'] = int(value)
            elif "chamX" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['chamX'] = int(value)
            elif "chamY" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['chamY'] = int(value)
            elif "chamZ" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['chamZ'] = int(value)
            elif "D" in line and "=" in line and not line.startswith("duallattice"):
                value = line.split("=")[1].strip().rstrip(';')
                self.config['D'] = int(value)
            elif "Temperature" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['temperature'] = float(value)
            elif "scaling" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['scaling'] = float(value)
            elif "thermal_coupling" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['thermal_coupling'] = float(value)
            elif "temporal_sensitivity" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['temporal_sensitivity_numerical'] = float(value)
            elif "temporal_steps" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['temporal_steps'] = int(value)
            elif "material" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['substance'] = str(value)
            elif "state" in line and "=" in line:
                value = line.split("=")[1].strip().rstrip(';')
                self.config['state'] = value
            
            # Parse FORCING section
            elif "FORCING" in line:
                self._parse_forcing_section(lines, i)
            
            # Parse BUILDINGS section
            elif "BUILDINGS" in line:
                self._parse_buildings_section(lines, i)
            
            # Parse OUTPUT section
            elif "OUTPUT" in line:
                self._parse_output_section(lines, i)
    
    def _parse_forcing_section(self, lines, start_index):
        """Parse the FORCING section of the configuration."""
        # X direction forcing
        self.config['forcing_amplitude_x'] = eval(lines[start_index + 1])
        self.config['forcing_amplitude_str_x'] = lines[start_index + 1].strip()
        self.config['forcing_omega_x'] = eval(lines[start_index + 2])
        self.config['forcing_omega_str_x'] = lines[start_index + 2].strip()
        
        # Y direction forcing
        self.config['forcing_amplitude_y'] = eval(lines[start_index + 4])
        self.config['forcing_amplitude_str_y'] = lines[start_index + 4].strip()
        self.config['forcing_omega_y'] = eval(lines[start_index + 5])
        self.config['forcing_omega_str_y'] = lines[start_index + 5].strip()
        
        # Z direction forcing
        self.config['forcing_amplitude_z'] = eval(lines[start_index + 7])
        self.config['forcing_amplitude_str_z'] = lines[start_index + 7].strip()
        self.config['forcing_omega_z'] = eval(lines[start_index + 8])
        self.config['forcing_omega_str_z'] = lines[start_index + 8].strip()
    
    def _parse_buildings_section(self, lines, start_index):
        """Parse the BUILDINGS section of the configuration."""
        n_build_value = lines[start_index + 1].split("=")[1].strip().rstrip(';')
        n_build = int(n_build_value)
        self.config['n_build'] = n_build
        
        building_commands = []
        for j in range(n_build):
            command = lines[start_index + 2 + j].strip().rstrip(';')
            building_commands.append(command)
        self.config['building_commands'] = building_commands
    
    def _parse_output_section(self, lines, start_index):
        """Parse the OUTPUT section of the configuration."""
        output_time_value = lines[start_index + 1].split("=")[1].strip().rstrip(';')
        self.config['output_time'] = int(output_time_value)
        self.config['output_dir'] = lines[start_index + 2].strip()
        plot_value = lines[start_index + 3].split("=")[1].strip().rstrip(';')
        self.config['plot'] = plot_value
        
        # Parse plot dimensions - handle semicolons and clean the values
        chamx_value = lines[start_index + 4].split("=")[1].strip().rstrip(';')
        chamy_value = lines[start_index + 5].split("=")[1].strip().rstrip(';')
        chamz_value = lines[start_index + 6].split("=")[1].strip().rstrip(';')
        
        self.config['ChamX_plot'] = eval(chamx_value)
        self.config['ChamY_plot'] = eval(chamy_value)
        self.config['ChamZ_plot'] = eval(chamz_value)
    
    def get_config(self):
        """Get the loaded configuration."""
        return self.config
    
    def validate_plot_dimensions(self):
        """Validate that plot dimensions are within lattice bounds."""
        chamX = self.config.get('chamX', 0)
        chamY = self.config.get('chamY', 0)
        chamZ = self.config.get('chamZ', 0)
        ChamX_plot = self.config.get('ChamX_plot', [0, 0])
        ChamY_plot = self.config.get('ChamY_plot', [0, 0])
        ChamZ_plot = self.config.get('ChamZ_plot', [0, 0])
        
        if ((int(ChamX_plot[1]) > int(chamX)) or 
            (int(ChamY_plot[1]) > int(chamY)) or 
            (int(ChamZ_plot[1]) > int(chamZ))):
            print("-------------------  WARNING: PLOT DIMENSION OUTSIDE THE LATTICE  -------------------")


class LatticeBuilder:
    """Handles lattice construction and manipulation."""
    
    def __init__(self, config):
        self.config = config
        self.lattice = None
    
    def build_lattice_system(self):
        """Build the complete lattice system based on configuration."""
        config = self.config
        
        # Calculate reticular distance
        substance = config['substance']
        scaling = config['scaling']
        reticular_distance = leng[substance] / scaling
        
        if config.get('debug', False):
            x_len = config['chamX'] * reticular_distance
            y_len = config['chamY'] * reticular_distance
            z_len = config['chamZ'] * reticular_distance
            print("Body dimensions:", x_len, y_len, z_len)
        
        # Build base lattice
        if config['D'] == 2:
            self.lattice = build_lattice([config['chamX'], config['chamY']], 
                                       substance, config['state'], 
                                       config['temperature'], scaling)
        elif config['D'] == 3:
            self.lattice = build_lattice([config['chamX'], config['chamY'], config['chamZ']], 
                                       substance, config['state'], 
                                       config['temperature'], scaling)
        
        # Apply building modifications
        self._apply_building_modifications()
        
        return self.lattice
    
    def _apply_building_modifications(self):
        """Apply building modifications to the lattice."""
        if self.config.get('n_build', 0) == 0:
            return
        
        building_commands = self.config.get('building_commands', [])
        
        for command in building_commands:
            if "lattice" in command and "duallattice" not in command:
                self._apply_lattice_modification(command)
            elif "duallattice" in command:
                self._apply_duallattice_modification(command)
            else:
                self._apply_building_object(command)
    
    def _apply_lattice_modification(self, command):
        """Apply lattice modification command."""
        alfa = int(command[8])
        beta = int(command[11])
        self.lattice[0][alfa][beta] = eval(command.split("=")[1])
        print(self.lattice[0][alfa][beta])
    
    def _apply_duallattice_modification(self, command):
        """Apply dual lattice modification command."""
        alfa = int(command[12])
        beta = int(command[15])
        self.lattice[1][alfa][beta] = eval(command.split("=")[1])
        print(self.lattice[1][alfa][beta])
    
    def _apply_building_object(self, command):
        """Apply building object command."""
        building = eval(command)
        if self.config['D'] == 2:
            self.lattice = insert_object_2D(self.lattice, building, 
                                          self.config['temperature'], 
                                          self.config['substance'], 
                                          self.config['scaling'])
    
    def get_lattice_arrays(self):
        """Get lattice as numpy arrays."""
        if self.lattice is None:
            raise RuntimeError("Lattice not built. Call build_lattice_system() first.")
        
        lattice_positions = np.array(self.lattice[0], dtype=np.float64)
        lattice_info = np.array(self.lattice[1], dtype=np.float64)
        
        return lattice_positions, lattice_info


class SharedMemoryManager:
    """Manages shared memory allocation and operations."""
    
    def __init__(self, config):
        self.config = config
        self.memory = None
        self.memory2 = None
        self.semaphore = None
        self.semaphore2 = None
    
    def allocate_memory(self):
        """Allocate shared memory for lattice data."""
        chamX = self.config['chamX']
        chamY = self.config['chamY']
        chamZ = self.config['chamZ']
        D = self.config['D']
        
        SisDym = chamX * chamY * chamZ
        SizeMem = 8 * SisDym * D * 2
        
        # Allocate first memory segment
        self._allocate_memory_segment(1234567, SizeMem)
        # Allocate second memory segment
        self._allocate_memory_segment(12345678, SizeMem)
    
    def _allocate_memory_segment(self, key, size):
        """Allocate a single memory segment with given key and size."""
        try:
            memory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREX, size=size)
            semaphore = sysv_ipc.Semaphore(key, sysv_ipc.IPC_CREX)
        except:
            memory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT, size=0)
            semaphore = sysv_ipc.Semaphore(key, sysv_ipc.IPC_CREAT)
            sysv_ipc.remove_shared_memory(memory.id)
            sysv_ipc.remove_semaphore(semaphore.id)
            memory = sysv_ipc.SharedMemory(key, sysv_ipc.IPC_CREAT, size=size)
            semaphore = sysv_ipc.Semaphore(key, sysv_ipc.IPC_CREAT)
        
        if key == 1234567:
            self.memory = memory
            self.semaphore = semaphore
        else:
            self.memory2 = memory
            self.semaphore2 = semaphore
    
    def write_lattice_data(self, lattice_positions, lattice_info):
        """Write lattice data to shared memory."""
        chamX = self.config['chamX']
        chamY = self.config['chamY']
        
        if self.config.get('debug', False):
            print("Prepared lattice")
            for i in range(chamX):
                print(lattice_positions[i][:])
        
        # Write positions to first memory segment
        for a in range(chamX):
            self.memory.write(lattice_positions[a].tobytes('C'), a * chamY * 8 * 4)
        
        if self.config.get('debug', False):
            print("Sent lattice")
            print(np.frombuffer(self.memory.read(), dtype=np.float64))
        
        if self.config.get('debug', False):
            print("Prepared info")
            for i in range(chamX):
                print(lattice_info[i][:])
        
        # Write info to second memory segment
        for a in range(chamX):
            self.memory2.write(lattice_info[a].tobytes('C'), a * chamY * 8 * 4)
        
        if self.config.get('debug', False):
            print("Sent info")
            print(np.frombuffer(self.memory2.read(), dtype=np.float64))
    
    def cleanup(self):
        """Clean up shared memory resources."""
        try:
            sysv_ipc.remove_shared_memory(self.memory.id)
            sysv_ipc.remove_semaphore(self.semaphore.id)
        except:
            pass
        
        try:
            sysv_ipc.remove_shared_memory(self.memory2.id)
            sysv_ipc.remove_semaphore(self.semaphore2.id)
        except:
            pass


class CodeExecutor:
    """Handles compilation and execution of C and Python codes."""
    
    def __init__(self, config):
        self.config = config
        self.C_name = "C_Lattice"
        self.Py_name = "Py_Analyses"
        
        # Get the project root directory (parent of orchestrator)
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lattice_engine_dir = os.path.join(self.project_root, "lattice_sound_engine")
        self.orchestrator_dir = os.path.join(self.project_root, "orchestrator")
    
    def compile_c_code(self):
        """Compile the C code."""
        # Change to lattice engine directory and use make
        command_compile = f"cd {self.lattice_engine_dir} && make"
        subprocess.run(command_compile, shell=True)
    
    def execute_c_code(self):
        """Execute the C code with appropriate parameters."""
        config = self.config
        
        # Handle output directory - if relative, make it relative to project root
        output_dir = config['output_dir']
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.project_root, output_dir)
        
        # Execute from lattice engine directory
        command_exe = (f"cd {self.lattice_engine_dir} && ./{self.C_name} "
                      f"{config['chamX']} {config['chamY']} {config['chamZ']} "
                      f"{config['D']} {config['temporal_sensitivity_numerical']} "
                      f"{config['temporal_steps']} {config['thread_num']} "
                      f"{config['forcing_amplitude_str_x']} {config['forcing_omega_str_x']} "
                      f"{config['forcing_amplitude_str_y']} {config['forcing_omega_str_y']} "
                      f"{config['forcing_amplitude_str_z']} {config['forcing_omega_str_z']} "
                      f"{config['output_time']} {config['thermal_coupling']} "
                      f"{config['ChamX_plot'][0]} {config['ChamX_plot'][1]} "
                      f"{config['ChamY_plot'][0]} {config['ChamY_plot'][1]} "
                      f"{config['ChamZ_plot'][0]} {config['ChamZ_plot'][1]} "
                      f"{output_dir}")
        
        subprocess.run(command_exe, shell=True)
        
        if config.get('debug', False):
            print("C Command launched \n", command_exe)
    
    def execute_python_code(self):
        """Execute the Python analysis code."""
        config = self.config
        
        # Handle output directory - if relative, make it relative to project root
        output_dir = config['output_dir']
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.project_root, output_dir)
        
        # Execute from orchestrator directory
        command_pylaunch = (f"cd {self.orchestrator_dir} && python3 {self.Py_name}.py "
                           f"{config['chamX']} {config['chamY']} {config['chamZ']} "
                           f"{config['D']} {config['temporal_steps']} "
                           f"{config['output_time']} {config['plot']} "
                           f"{config['thread_num']} {output_dir}")
        
        subprocess.run(command_pylaunch, shell=True)


class LatticeSoundManager:
    """Main class that orchestrates the entire LatticeSound system."""
    
    def __init__(self, config_file="Starter.flsm"):
        self.config_manager = ConfigurationManager(config_file)
        self.config = self.config_manager.get_config()
        self.lattice_builder = LatticeBuilder(self.config)
        self.memory_manager = SharedMemoryManager(self.config)
        self.code_executor = CodeExecutor(self.config)
        
        # Get project root for output directory handling
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def run(self):
        """Execute the complete LatticeSound workflow."""
        try:
            # Validate configuration
            self.config_manager.validate_plot_dimensions()
            
            # Build lattice
            self.lattice_builder.build_lattice_system()
            lattice_positions, lattice_info = self.lattice_builder.get_lattice_arrays()
            
            # Write system information
            self._write_system_info()
            
            # Allocate and write to shared memory
            self.memory_manager.allocate_memory()
            self.memory_manager.write_lattice_data(lattice_positions, lattice_info)
            
            # Compile and execute codes
            self.code_executor.compile_c_code()
            
            # Execute C code
            c_process = Process(target=self.code_executor.execute_c_code)
            c_process.start()
            c_process.join()
            
            # Execute Python analysis
            py_process = Process(target=self.code_executor.execute_python_code)
            py_process.start()
            py_process.join()
            
        finally:
            # Cleanup shared memory
            self.memory_manager.cleanup()
    
    def _write_system_info(self):
        """Write system information to output file."""
        config = self.config
        substance = config['substance']
        state = config['state']
        temperature = config['temperature']
        scaling = config['scaling']
        
        scaled_len, scaled_mass, scaled_k, scaled_gamm, scaled_omega = scale_back2D(
            substance, state, temperature, scaling)
        
        # Handle output directory - if relative, make it relative to project root
        output_dir = config['output_dir']
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.project_root, output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, "LS_result.txt")
        with open(output_file, "w") as file:
            file.write(f"Effective length          [m]:        {scaled_len}\n")
            file.write(f"Effective mass            [kg]:       {scaled_mass}\n")
            file.write(f"Effective elastic const   [kg/s^2]:   {scaled_k}\n")
            file.write(f"Effective viscosity const [1/s]:      {scaled_gamm}\n")
            file.write(f"Effective omega0          [rad/s]:    {scaled_omega}\n")
            file.write(f"thermal_coupling          [ ]:        {config['thermal_coupling']}\n")


def main():
    """Main entry point for the LatticeSound Manager."""
    try:
        lsm = LatticeSoundManager()
        lsm.run()
    except Exception as e:
        print(f"Error in LatticeSound Manager: {e}")
        raise


if __name__ == '__main__':
    main()
