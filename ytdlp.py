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

        # Prompt for trimming options (applies to all URLs in this batch)
        print("\n✨ Optional: Trim your download! ✂️✨")
        print("   You can specify start and end times to trim the video/audio.")
        print("   Format: seconds (e.g. 30) or HH:MM:SS (e.g. 00:01:30)")
        print("   Leave blank to download the full video/audio.")
        start_time = input("   ⏩ Start at (leave blank for beginning): ").strip()
        end_time = input("   ⏹️ End at (leave blank for end): ").strip()
        
        # Validate and build download_sections string if needed
        download_sections = None
        downloader = None
        downloader_args = None
        if start_time or end_time:
            # yt-dlp expects download-sections as "*start-end" (e.g. "*30-60" or "*00:01:00-00:02:00")
            section = f"*{start_time if start_time else ''}-{end_time if end_time else ''}"
            download_sections = section
            print(f"\nTrimming enabled: {section}")
            # Use ffmpeg downloader with -ss and -to for more reliable trimming
            downloader = 'ffmpeg'
            ffmpeg_args = []
            if start_time:
                ffmpeg_args.append(f"-ss {start_time}")
            if end_time:
                ffmpeg_args.append(f"-to {end_time}")
            if ffmpeg_args:
                # ffmpeg_i: is the correct prefix for yt-dlp's --downloader-args
                downloader_args = { 'ffmpeg_i': ' '.join(ffmpeg_args) }
        else:
            print("\nNo trimming. Downloading full video/audio.")
        
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
                archive_path = os.path.join(output_dir, 'downloaded_audio.txt')
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
                    'verbose': True,
                    'download_archive': archive_path  # Separate audio archive
                }
            else:
                # Video options
                print("Video mode selected. Will download as MP4.")
                archive_path = os.path.join(output_dir, 'downloaded_video.txt')
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
                    'verbose': True,  # Add verbose logging to see what's happening
                    'download_archive': archive_path  # Separate video archive
                }
            # Add trimming if specified
            if download_sections:
                ydl_opts['download_sections'] = download_sections
            if downloader:
                ydl_opts['downloader'] = downloader
            if downloader_args:
                ydl_opts['downloader_args'] = downloader_args

            # Check if the URL is already in the archive
            already_downloaded = False
            if os.path.exists(archive_path):
                with open(archive_path, 'r') as archive_file:
                    for line in archive_file:
                        if url in line:
                            already_downloaded = True
                            break
            if already_downloaded:
                print(f"\n⚠️ This URL appears to have already been downloaded according to the archive.")
                force_redownload = input("   Proceed anyway? (y/N): ").strip().lower()
                if force_redownload == 'y':
                    # Remove the entry from the archive so yt-dlp will re-download
                    with open(archive_path, 'r') as archive_file:
                        lines = archive_file.readlines()
                    with open(archive_path, 'w') as archive_file:
                        for line in lines:
                            if url not in line:
                                archive_file.write(line)
                    print("   Proceeding with re-download...")
                else:
                    print("   Skipping download for this URL.")
                    continue
            
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
                    
                if is_audio_only:
                    print(f"\nAudio downloaded successfully! MP3 file saved to {output_dir}")
                else:
                    print(f"\nVideo downloaded successfully! MP4 file saved to {output_dir}")
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
