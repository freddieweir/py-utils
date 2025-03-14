import os
import math
import subprocess
import platform
import sys
import shutil
from pathlib import Path

# Import the VirtualEnvironment classes from module_venv
try:
    # Try to import assuming script is run from the py-utils directory
    from module_venv import VirtualEnvironment, AutoVirtualEnvironment
except ImportError:
    # Try to import using relative path if script is run from a different directory
    try:
        import importlib.util
        
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to module_venv.py
        module_path = os.path.join(current_dir, "module_venv.py")
        
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Cannot find module_venv.py at {module_path}")
        
        # Load the module
        spec = importlib.util.spec_from_file_location("module_venv", module_path)
        module_venv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_venv)
        
        # Get the VirtualEnvironment classes
        VirtualEnvironment = module_venv.VirtualEnvironment
        AutoVirtualEnvironment = module_venv.AutoVirtualEnvironment
    except Exception as e:
        print(f"Error importing VirtualEnvironment classes: {e}")
        print("Please make sure module_venv.py is in the same directory as this script.")
        sys.exit(1)

# Define the required packages
REQUIRED_PACKAGES = ["moviepy==1.0.3"]

def extract_audio(file_path):
    """Extract audio from video files."""
    # This function will be called after the venv is activated
    import moviepy.editor as mp
    
    # Check if the file is a video
    if file_path.endswith(('.mov', '.mp4', '.avi', '.mkv', '.wmv')):
        # Extract audio from video
        print(f"Extracting audio from {file_path}...")
        video = mp.VideoFileClip(file_path)
        audio_file_path = f"{os.path.splitext(file_path)[0]}.mp3"
        video.audio.write_audiofile(audio_file_path)
        print(f"Audio extracted and saved to {audio_file_path}")
        return audio_file_path
    else:
        # File is already an audio file, so just return the path
        return file_path

def split_file(file_path, max_size_mb):
    """Split a file into chunks of specified maximum size."""
    global output_dir
    
    # Convert max size from MB to bytes
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    # Get the total size of the file
    total_size = os.path.getsize(file_path)
    
    # Calculate the number of chunks needed
    num_chunks = math.ceil(total_size / max_size_bytes)
    
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Read the file in chunks
        chunk_size = max_size_bytes
        for i in range(num_chunks):
            chunk = f.read(chunk_size)
            # Write the chunk to a new file
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            chunk_file_path = os.path.join(output_dir, f'{name} - Part {i+1}{ext}')
            with open(chunk_file_path, 'wb') as cf:
                cf.write(chunk)
            print(f'Wrote chunk {i+1} to {chunk_file_path}')
    
    # Copy the original file to the output directory with "- ORIGINAL" appended
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    
    # Check if the file already ends with "- ORIGINAL"
    if name.endswith("- ORIGINAL"):
        original_dest_name = base_name
    else:
        original_dest_name = f'{name} - ORIGINAL{ext}'
    
    dest_path = os.path.join(output_dir, original_dest_name)
    shutil.move(file_path, dest_path)
    print(f'Moved original file to {dest_path}')

def main():
    """Main function to handle file selection and splitting."""
    global output_dir
    
    # Get the home directory for venv path
    home_dir = str(Path.home())
    
    # Create venv name for this specific script
    venv_name = os.path.join(home_dir, "venv", "split_file_venv")
    
    # Setup auto virtual environment with required packages
    auto_venv = AutoVirtualEnvironment(custom_name=venv_name, auto_packages=REQUIRED_PACKAGES)
    
    # Try to switch to the virtual environment with required packages
    # This will create it if it doesn't exist and re-execute the script
    auto_venv.auto_switch()
    
    # If we reach here, we should be in the virtual environment
    print(f"Using Python interpreter: {sys.executable}")
    
    # Get the list of files in the current directory, ignoring .DS_Store
    files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.DS_Store') and not f.startswith('.')]
    
    # Print the list of files with numbers
    print("Select a file:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file}")
    
    # Get the user's selection
    while True:
        try:
            selection = int(input("Enter the number of your chosen file: "))
            if 1 <= selection <= len(files):
                break
            else:
                print("Invalid selection. Please enter a number between 1 and", len(files))
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get the selected file path
    file_path = files[selection - 1]
    
    # Get the file name without extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Remove "- ORIGINAL" suffix from the directory name if it exists
    dir_name = file_name
    if dir_name.endswith("- ORIGINAL"):
        dir_name = dir_name[:-10].strip()  # Remove "- ORIGINAL" and any trailing spaces
    
    # Create a directory based on the file name (without "- ORIGINAL" suffix)
    output_dir = dir_name
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f'Created directory: {output_dir}')
    else:
        print(f'Directory already exists: {output_dir}')
    
    # Extract audio if necessary
    file_path = extract_audio(file_path)
    
    max_size_mb = float(input("Enter the maximum chunk size in MB (default: 9): ") or 9)
    
    split_file(file_path, max_size_mb)

if __name__ == "__main__":
    main()
