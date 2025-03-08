import os
import math
import subprocess
import platform
import sys
import shutil
from pathlib import Path

# Define the venv directory
VENV_DIR = Path(__file__).parent / "venv_split_file"
REQUIRED_PACKAGES = ["moviepy==1.0.3"]

def is_package_installed(package_name):
    """Check if a package is installed in the venv."""
    try:
        python_executable = str(VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python")
        subprocess.run(
            [python_executable, "-c", f"import {package_name.split('==')[0]}"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_venv():
    """Set up the virtual environment and install required packages."""
    print("Setting up virtual environment...")
    
    # Create the venv if it doesn't exist
    if not VENV_DIR.exists():
        python_executable = sys.executable
        subprocess.run([python_executable, "-m", "venv", str(VENV_DIR)], check=True)
    
    # Install required packages
    pip_executable = str(VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "pip")
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...")
        subprocess.run(
            [pip_executable, "install", package],
            check=True
        )

def activate_venv():
    """Ensure the venv is set up and return the path to its Python executable."""
    if not VENV_DIR.exists() or not all(is_package_installed(pkg) for pkg in REQUIRED_PACKAGES):
        setup_venv()
    
    return str(VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python")

def run_in_venv():
    """Re-run the current script in the virtual environment."""
    python_executable = activate_venv()
    os.execv(python_executable, [python_executable, __file__] + sys.argv[1:])

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
    
    # Check if running in the venv
    if not any("venv_split_file" in arg for arg in sys.path):
        run_in_venv()
        return
    
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
