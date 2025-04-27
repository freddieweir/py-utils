#!/usr/bin/env python3
import os
import venv
import sys
import subprocess
import inspect
import pathlib

class VirtualEnvironment:
    """A class to create and manage Python virtual environments."""
    
    def __init__(self, custom_name=None):
        """Initialize with optional custom environment name."""
        if custom_name:
            self.venv_name = custom_name
        else:
            # Get the project directory name
            current_dir = os.path.basename(os.getcwd())
            
            # Get the name of the script that called this
            caller_filename = self._get_caller_script_name()
            
            # Create virtual environment name with new pattern
            self.venv_name = f"venv-{current_dir}-{caller_filename}"
    
    def _get_caller_script_name(self):
        """Get the name of the script that called this class."""
        try:
            # Try to get the caller's filename from the stack
            frame = inspect.stack()[2]
            caller_path = frame.filename
            return os.path.basename(caller_path)
        except (IndexError, AttributeError):
            # Fallback to the current running script
            return os.path.basename(sys.argv[0])
    
    def create(self):
        """Create a new virtual environment."""
        print(f"Creating virtual environment '{self.venv_name}'...")
        venv.create(self.venv_name, with_pip=True)
        return self.venv_name
    
    def install_packages(self, packages):
        """Install packages in the virtual environment.
        
        Args:
            packages (list): List of package names to install
        """
        # Determine the pip path based on platform
        if sys.platform == 'win32':
            pip_path = os.path.join(self.venv_name, 'Scripts', 'pip')
        else:
            pip_path = os.path.join(self.venv_name, 'bin', 'pip')
        
        print(f"Installing packages: {', '.join(packages)}")
        subprocess.check_call([pip_path, 'install'] + packages)
    
    def print_activation_instructions(self):
        """Print instructions for activating the virtual environment."""
        print(f"\nVirtual environment '{self.venv_name}' created.")
        print("\nTo activate the environment, run:")
        if sys.platform == 'win32':
            print(f"{self.venv_name}\\Scripts\\activate")
        else:
            print(f"source {self.venv_name}/bin/activate")
    
    def setup(self, packages=None):
        """Set up a virtual environment with optional package installation.
        
        Args:
            packages (list, optional): List of packages to install. Defaults to None.
            
        Returns:
            str: The name of the created virtual environment
        """
        self.create()
        
        if packages:
            self.install_packages(packages)
            
        self.print_activation_instructions()
        return self.venv_name
    
    def get_python_path(self):
        """Get the path to the Python executable in the virtual environment."""
        if sys.platform == 'win32':
            return os.path.join(os.getcwd(), self.venv_name, 'Scripts', 'python')
        else:
            return os.path.join(os.getcwd(), self.venv_name, 'bin', 'python')

class AutoVirtualEnvironment(VirtualEnvironment):
    """A class that automatically sets up and switches to a virtual environment."""
    
    def __init__(self, custom_name=None, auto_packages=None):
        """Initialize with optional custom name and packages to auto-install."""
        super().__init__(custom_name)
        self.auto_packages = auto_packages or []
        
    def auto_switch(self, required_packages=None):
        """
        Check if the environment exists and is activated.
        If not, create it, install packages, and re-execute the current script with it.
        
        Args:
            required_packages (list, optional): List of packages required by the script.
        """
        packages = required_packages or self.auto_packages
        
        # Check if we're already in a virtual environment
        in_venv = sys.prefix != sys.base_prefix
        venv_exists = os.path.exists(self.venv_name) and os.path.isdir(self.venv_name)
        
        # If we're in a virtual environment and it's the right one, we're done
        if in_venv and (self.venv_name in sys.prefix or sys.prefix.endswith(self.venv_name)):
            print(f"Already using virtual environment: {self.venv_name}")
            return True
        
        # If the environment doesn't exist, create it
        if not venv_exists:
            print(f"Virtual environment '{self.venv_name}' doesn't exist. Creating...")
            self.setup(packages=packages)
        
        # Get the Python path in the virtual environment
        venv_python = self.get_python_path()
        
        if not os.path.exists(venv_python):
            print(f"Error: Python executable not found at {venv_python}")
            return False
        
        # Add a flag to prevent infinite recursion
        if "--venv-activated" not in sys.argv:
            print(f"Switching to virtual environment: {self.venv_name}")
            
            # Get the current script path
            current_script = sys.argv[0]
            abs_script_path = os.path.abspath(current_script)
            
            # Prepare args for re-execution
            new_args = [venv_python, abs_script_path] + sys.argv[1:] + ["--venv-activated"]
            
            # Re-execute the current script with the virtual environment Python
            os.execv(venv_python, new_args)
            # If execv succeeds, the code below won't be executed
            
        # If we get here with the flag, we're running in the virtual environment
        return True

# Example usage when script is run directly
if __name__ == "__main__":
    # Example of the regular VirtualEnvironment
    print("Example of regular VirtualEnvironment:")
    venv_manager = VirtualEnvironment()
    print(f"Generated venv name: {venv_manager.venv_name}")
    
    # Example of the AutoVirtualEnvironment
    print("\nExample of AutoVirtualEnvironment:")
    auto_venv = AutoVirtualEnvironment(auto_packages=['requests', 'beautifulsoup4'])
    auto_venv.auto_switch()
    
    # If we reach here in the virtual environment
    if "--venv-activated" in sys.argv:
        print("Success! Running in the virtual environment.")
        print(f"Python path: {sys.executable}")
