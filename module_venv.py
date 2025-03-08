#!/usr/bin/env python3
import os
import venv
import subprocess

# Get the project directory name
project_name = os.path.basename(os.getcwd())

# Create virtual environment name
venv_name = f"{project_name}-env"

# Create a new virtual environment
venv.create(venv_name, with_pip=True)

# Activate the environment (note: this can't be done directly in Python)
# Instead, we'll print instructions for the user
print(f"Virtual environment '{venv_name}' created.")
print("\nTo activate the environment, run:")
print(f"source {venv_name}/bin/activate  # On Unix/macOS")
print(f"{venv_name}\\Scripts\\activate  # On Windows")
