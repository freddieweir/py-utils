import os
import subprocess
import platform
from pathlib import Path
import sys

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

# Define yt-dlp version
YT_DLP_VERSION = "2025.2.19"  # You can update this to the latest version
REQUIRED_PACKAGES = [f"yt-dlp=={YT_DLP_VERSION}"]

# Define the common download directory path to be used across all scripts
def get_download_dir():
    """
    Get the common download directory path (~/Downloads/py-script-downloads).
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path object to the download directory
    """
    # Get the user's home directory in a cross-platform way
    home_dir = Path.home()
    
    # Create the path to Downloads/py-script-downloads
    download_dir = home_dir / "Downloads" / "py-script-downloads"
    
    # Create the directory if it doesn't exist
    if not download_dir.exists():
        os.makedirs(download_dir, exist_ok=True)
        print(f"Created download directory: {download_dir}")
    
    # Create script-specific subdirectory
    script_dir = download_dir / "yt-dlp downloads"
    if not script_dir.exists():
        os.makedirs(script_dir, exist_ok=True)
        print(f"Created script directory: {script_dir}")
    
    return script_dir

# Main script
def main():
    # Get the home directory for venv path
    home_dir = str(Path.home())
    
    # Create venv name for this specific script
    venv_name = os.path.join(home_dir, "venv", "ytdlp_venv")
    
    # Setup auto virtual environment with required packages
    auto_venv = AutoVirtualEnvironment(custom_name=venv_name, auto_packages=REQUIRED_PACKAGES)
    
    # Try to switch to the virtual environment with required packages
    # This will create it if it doesn't exist and re-execute the script
    auto_venv.auto_switch()
    
    # If we reach here, we should be in the virtual environment
    print(f"Using Python interpreter: {sys.executable}")
    
    # Import yt-dlp after ensuring it's installed
    import yt_dlp
    
    # Proceed with the rest of the script
    print("\nYouTube Downloader")
    print("----------------")
    
    # Get the output directory
    output_dir = get_download_dir()
    print(f"Downloads will be saved to: {output_dir}")
    
    # Ask user for download preference at the beginning
    default_download_type = 'v'  # Default to video
    
    # Ask if user wants video or just audio for all downloads in this session
    download_type = input("Download (v)ideo or (a)udio only for all URLs in this session? (v/a, default: v): ").lower().strip()
    
    # If no input, use the default
    if not download_type:
        is_audio_only = default_download_type.startswith('a')
        print(f"Using default: {'Audio-only' if is_audio_only else 'Video'}")
    else:
        is_audio_only = download_type.startswith('a')
        
    if is_audio_only:
        print("Audio-only mode selected. All downloads will be saved as MP3.")
    else:
        print("Video mode selected. All downloads will be saved as MP4.")
    
    # Loop until user quits
    while True:
        # Get user input
        url_input = input("\nEnter YouTube URL(s) (separate multiple URLs with commas, or 'q' to quit): ")
        
        # Check if user wants to quit
        if url_input.lower() == 'q':
            print("Exiting. Goodbye!")
            break
        
        # Split the input by commas and strip whitespace
        urls = [url.strip() for url in url_input.split(',') if url.strip()]
        
        if not urls:
            print("No valid URLs entered. Please try again.")
            continue
            
        print(f"Found {len(urls)} URL(s) to process")
        
        # Process each URL
        for index, url in enumerate(urls):
            # Remove any @ symbol if present (sometimes added when copying from certain platforms)
            url = url.lstrip('@')
            
            if not url.startswith(('http://', 'https://', 'www.', 'youtu.be', 'youtube.com')):
                print(f"\nSkipping invalid URL: {url}")
                continue
                
            print(f"\n[{index + 1}/{len(urls)}] Processing: {url}")
            
            # Set up yt-dlp options based on download type
            if is_audio_only:
                # Audio-only options
                print("Audio-only mode selected. Will download as MP3.")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }, {
                        'key': 'FFmpegMetadata'  # Add metadata to the audio file
                    }],
                    'no_overwrites': True,
                    'ignoreerrors': True,
                    'verbose': True
                }
            else:
                # Video options
                print("Video mode selected. Will download as MP4.")
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prefer MP4 format
                    'merge_output_format': 'mp4',
                    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),  # Set output template to save in Downloads folder
                    'embed_subs': True,
                    'writethumbnail': True,
                    'postprocessors': [
                        {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},  # Force MP4 conversion
                        {'key': 'EmbedThumbnail'},  # Embed thumbnail in the video file
                        {'key': 'FFmpegMetadata'},  # Add metadata to the video file
                    ],
                    'no_overwrites': True,
                    'ignoreerrors': True,
                    'verbose': True
                }
            
            # Run yt-dlp with the specified options
            try:
                print("\nAttempting to download...")
                print(f"Download will be saved to: {output_dir}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # First try to get info to verify if video is accessible
                    print("\nVerifying video access...")
                    info = ydl.extract_info(url, download=False)
                    print(f"Video title: {info.get('title', 'Unknown')}")
                    print(f"Video duration: {info.get('duration', 'Unknown')} seconds")
                    print(f"Available formats: {len(info.get('formats', []))} formats found")
                    
                    # Now download the video
                    print("\nStarting download...")
                    ydl.download([url])
                
                # Try to get the actual output file path
                output_file = None
                ext = 'mp3' if is_audio_only else 'mp4'
                # Try yt-dlp info dict for output file path
                if 'requested_downloads' in info and info['requested_downloads']:
                    output_file = info['requested_downloads'][0].get('filepath')
                elif 'filepath' in info:
                    output_file = info['filepath']
                # Fallback: search for the most recent file in output_dir with the right extension
                if not output_file or not os.path.exists(output_file):
                    import glob
                    files = glob.glob(os.path.join(output_dir, f"*.{ext}"))
                    if files:
                        output_file = max(files, key=os.path.getmtime)
                trimmed_file = None
                if output_file:
                    base, extn = os.path.splitext(output_file)
                    trimmed_file = f"{base}_trimmed{extn}"
                duration = info.get('duration', None)
                
                # Prompt for trim times (after download)
                if duration:
                    if duration >= 3600:
                        time_format = 'HH:MM:SS'
                    else:
                        time_format = 'MM:SS'
                else:
                    time_format = 'MM:SS'
                print("\n✨ Optional: Trim your download! ✨")
                print(f"Enter start and end times in {time_format} format (leave blank for full length). Example: 00:30 for 30 seconds, 01:15:00 for 1 hour 15 min.")
                trim_start = input("⏩ Start at (leave blank for start): ").strip()
                trim_end = input("⏹️ End at (leave blank for end): ").strip()
                
                def parse_time(t):
                    if not t:
                        return None
                    parts = t.split(":")
                    try:
                        if len(parts) == 3:
                            h, m, s = map(int, parts)
                            return h*3600 + m*60 + s
                        elif len(parts) == 2:
                            m, s = map(int, parts)
                            return m*60 + s
                        elif len(parts) == 1:
                            return int(parts[0])
                    except Exception:
                        return None
                    return None
                
                start_sec = parse_time(trim_start)
                end_sec = parse_time(trim_end)
                
                if (start_sec is not None or end_sec is not None):
                    if not output_file or not os.path.exists(output_file):
                        print(f"❌ Could not find the downloaded file to trim! Please check your downloads folder. (File: {output_file})")
                    else:
                        print(f"\n✂️ Trimming {output_file}...")
                        ffmpeg_cmd = [
                            "ffmpeg", "-y", "-i", output_file
                        ]
                        if start_sec is not None:
                            ffmpeg_cmd += ["-ss", str(start_sec)]
                        if end_sec is not None:
                            if start_sec is not None:
                                duration_sec = end_sec - start_sec
                            else:
                                duration_sec = end_sec
                            ffmpeg_cmd += ["-t", str(duration_sec)]
                        ffmpeg_cmd += ["-c", "copy", trimmed_file]
                        print(f"Running: {' '.join([f'\"{arg}\"' if ' ' in str(arg) else str(arg) for arg in ffmpeg_cmd])}")
                        try:
                            subprocess.run(ffmpeg_cmd, check=True)
                            print(f"\n🎉 Trimmed file saved as: {trimmed_file}")
                        except Exception as e:
                            print(f"❌ Error trimming file: {e}")
                else:
                    print("No trimming selected. Keeping full download.")
            except yt_dlp.utils.DownloadError as e:
                print(f"\nError downloading video: {e}")
                if "members-only content" in str(e).lower() or "private video" in str(e).lower() or "This video is only available to members" in str(e):
                    print("\nThis appears to be a members-only video which requires special access.")
                    print("Unfortunately this content cannot be downloaded with this tool.")
                elif "sign in to view" in str(e).lower():
                    print("\nThis video requires you to be signed in to view.")
                    print("Unfortunately this content cannot be downloaded with this tool.")
            except Exception as e:
                print(f"\nUnexpected error during download: {e}")
                print(f"Error type: {type(e).__name__}")
            except KeyboardInterrupt:
                print("\nDownload cancelled by user.")
                print("Continuing to next URL...")
                continue
                
        print("\nProcessed all URLs.")

if __name__ == "__main__":
    main()
