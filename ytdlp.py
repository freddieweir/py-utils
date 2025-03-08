import os
import subprocess
import platform
from pathlib import Path
import sys

# Define the venv directory
VENV_DIR = Path(__file__).parent / "venv"
YT_DLP_VERSION = "2025.2.19"  # You can update this to the latest version

# Check if yt-dlp is installed in the venv
def is_yt_dlp_installed():
    try:
        subprocess.run(
            [str(VENV_DIR / "bin" / "python"), "-c", "import yt_dlp"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False

# Set up the venv and install yt-dlp
def setup_venv():
    print("Setting up virtual environment...")
    
    # Create the venv if it doesn't exist
    if not VENV_DIR.exists():
        python_executable = sys.executable
        subprocess.run([python_executable, "-m", "venv", str(VENV_DIR)], check=True)
    
    # Install yt-dlp using the venv's pip directly
    pip_executable = str(VENV_DIR / "bin" / "pip") if platform.system() != "Windows" else str(VENV_DIR / "Scripts" / "pip")
    subprocess.run(
        [pip_executable, "install", f"yt-dlp=={YT_DLP_VERSION}"],
        check=True
    )

# Check if the venv is set up and activate it
def activate_venv():
    if not VENV_DIR.exists():
        setup_venv()
    
    # No need to explicitly activate the venv - we'll use its Python directly
    return str(VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin") / "python")

# Main script
def main():
    # Activate the venv
    activate_venv()
    
    # Check if yt-dlp is installed
    if not is_yt_dlp_installed():
        print("Installing yt-dlp...")
        subprocess.run([str(VENV_DIR / "bin" / "pip"), "install", f"yt-dlp=={YT_DLP_VERSION}"], check=True)
    
    # Proceed with the rest of the script
    print("\nYouTube Downloader")
    print("----------------")
    
    # Get user input
    url = input("Enter the YouTube URL: ")
    
    # Get output format
    while True:
        print("\nSelect output format:")
        print("1. Audio only (MP3)")
        print("2. Video + Audio (MP4)")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == "1":
            format = "bestaudio[ext=mp4]/bestaudio[ext=m4a]/bestaudio"
            postprocessor_args = ["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
            break
        elif choice == "2":
            format = "bestvideo+bestaudio[ext=mp4]/best[ext=mp4]/best"
            postprocessor_args = []
            break
        else:
            print("Invalid choice. Please try again.")
    
    # Set output directory to Downloads
    output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Run yt-dlp with the specified format
    try:
        subprocess.run(
            [
                str(VENV_DIR / "bin" / "yt-dlp"),
                "-o",
                f"{output_dir}/%(title)s.%(ext)s",
                "--merge-output-format",
                "mp4",
                "--embed-subs",
                "--no-overwrites",
                "--download-archive",
                f"{output_dir}/downloaded.txt",
                *postprocessor_args,
                url,
            ],
            check=True,
        )
        print(f"\nDownload completed successfully! Files saved to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\nError downloading video: {e}")
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")

if __name__ == "__main__":
    main()
