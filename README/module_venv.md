# Python Virtual Environment Utility

The `module_venv.py` script provides classes for creating and managing Python virtual environments. It's designed to be imported by other scripts to automate virtual environment creation, package installation, and environment switching.

## Features

- Automatic virtual environment naming based on project directory and caller script
- Creation of virtual environments with pip support
- Package installation within the virtual environment
- Automatic detection and switching to the correct virtual environment
- Cross-platform support (Windows, macOS, Linux)

## Classes

### VirtualEnvironment

A base class to create and manage Python virtual environments.

```python
from module_venv import VirtualEnvironment

# Create a virtual environment with automatic naming
venv = VirtualEnvironment()

# Create a virtual environment with custom name
venv = VirtualEnvironment(custom_name="my_custom_venv")

# Create the environment and install packages
venv.setup(packages=["requests", "pandas"])
```

#### Methods

- `create()` - Creates a new virtual environment
- `install_packages(packages)` - Installs packages in the virtual environment
- `print_activation_instructions()` - Prints instructions for activating the environment
- `setup(packages=None)` - Sets up a virtual environment with optional package installation
- `get_python_path()` - Gets the path to the Python executable in the virtual environment

### AutoVirtualEnvironment

A subclass that automatically sets up and switches to a virtual environment.

```python
from module_venv import AutoVirtualEnvironment

# Create an auto virtual environment with packages
auto_venv = AutoVirtualEnvironment(auto_packages=["requests", "beautifulsoup4"])

# Switch to the environment (creates it if it doesn't exist)
auto_venv.auto_switch()

# If the script continues after this point, it's running in the virtual environment
```

#### Methods

All methods from `VirtualEnvironment` plus:

- `auto_switch(required_packages=None)` - Checks if the environment exists and is activated; if not, creates it, installs packages, and re-executes the current script with it

## Integration in Other Scripts

To use this in your own scripts:

```python
import os
import sys
from pathlib import Path

# Import the VirtualEnvironment classes
try:
    from module_venv import VirtualEnvironment, AutoVirtualEnvironment
except ImportError:
    # Import with fallback (example code)
    ...

# Define required packages
REQUIRED_PACKAGES = ["package1", "package2"]

def main():
    # Get the home directory for venv path
    home_dir = str(Path.home())
    
    # Create venv name for this specific script
    venv_name = os.path.join(home_dir, "venv", "my_script_venv")
    
    # Setup auto virtual environment with required packages
    auto_venv = AutoVirtualEnvironment(custom_name=venv_name, auto_packages=REQUIRED_PACKAGES)
    
    # Switch to the virtual environment
    auto_venv.auto_switch()
    
    # If we reach here, we should be in the virtual environment
    print(f"Using Python interpreter: {sys.executable}")
    
    # Rest of your script logic goes here...

if __name__ == "__main__":
    main()
```

## Examples

### Basic Usage

```python
# Example of the regular VirtualEnvironment
venv_manager = VirtualEnvironment()
print(f"Generated venv name: {venv_manager.venv_name}")

# Create and set up the environment
venv_manager.setup(packages=["requests", "numpy"])
```

### Auto-switching to a Virtual Environment

```python
# Example of the AutoVirtualEnvironment
auto_venv = AutoVirtualEnvironment(auto_packages=["requests", "beautifulsoup4"])
auto_venv.auto_switch()

# If we reach here in the virtual environment
if "--venv-activated" in sys.argv:
    print("Success! Running in the virtual environment.")
    print(f"Python path: {sys.executable}")
``` 