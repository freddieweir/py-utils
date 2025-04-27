#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Import the VirtualEnvironment classes from module_venv (in the same directory)
try:
    # Try to import assuming script is run from the py-utils directory
    from module_venv import VirtualEnvironment, AutoVirtualEnvironment
    print("Successfully imported VirtualEnvironment classes")
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
        print(f"Successfully imported VirtualEnvironment classes from {module_path}")
    except Exception as e:
        print(f"Error importing VirtualEnvironment classes: {e}")
        print("Please make sure module_venv.py is in the same directory as this script.")
        sys.exit(1)

# Check if wget is installed
def check_dependencies():
    """Check if wget is installed on the system."""
    try:
        result = subprocess.run(
            ["which", "wget"] if sys.platform != "win32" else ["where", "wget"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return ["wget"]
        return []
    except Exception as e:
        print(f"Error checking for wget: {e}")
        return ["wget"]

# Function to create a safe directory name from a URL
def get_safe_dirname_from_url(url):
    """Convert a URL to a safe directory name.
    
    Args:
        url (str): The URL to convert
        
    Returns:
        str: A filesystem-safe directory name
    """
    # Remove protocol (http://, https://)
    if '://' in url:
        url = url.split('://', 1)[1]
    
    # Replace special characters with underscores
    import re
    safe_name = re.sub(r'[^\w\-\.]', '_', url)
    
    # Remove trailing underscores
    safe_name = safe_name.rstrip('_')
    
    # Limit length to avoid path length issues
    if len(safe_name) > 64:
        safe_name = safe_name[:64]
    
    return safe_name

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
    script_dir = download_dir / "doc_link downloads"
    if not script_dir.exists():
        os.makedirs(script_dir, exist_ok=True)
        print(f"Created script directory: {script_dir}")
    
    return script_dir

# Function to download documents using wget
def download_documents(base_url):
    """
    Download all documents from the given base URL using wget.
    
    Args:
        base_url (str): The base URL to download documents from
    
    Returns:
        int: Success status (0 for success, 1 for failure)
    """
    # Get the common download directory
    base_path = get_download_dir()
    
    # Create a specific directory for this URL
    url_dirname = get_safe_dirname_from_url(base_url)
    url_specific_path = os.path.join(base_path, url_dirname)
    if not Path(url_specific_path).exists():
        os.makedirs(url_specific_path)
        print(f"Created URL-specific directory: {url_specific_path}")

    print(f"Starting download from {base_url}")
    print(f"Documents will be saved to: {url_specific_path}")
    
    # Change to the download directory
    original_dir = os.getcwd()
    os.chdir(url_specific_path)
    
    try:
        # Construct the wget command
        wget_cmd = [
            "wget",
            "--recursive",  # Download recursively
            "--level=inf",  # No limit on recursion depth
            "--mirror",     # Mirror the website
            "--convert-links",  # Convert links to local
            "--adjust-extension",  # Add appropriate extensions
            "--page-requisites",  # Get all page assets
            "--no-clobber",  # Don't re-download existing files
            "--random-wait",  # Add random delays between requests
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # Generic Chrome browser user agent
            "--no-check-certificate",  # Skip SSL certificate checks
            "-e",  # Execute command
            "--timeout=10",  # Set timeout to avoid hanging
            "--tries=3",    # Number of retries
            "--wait=1",     # Wait 1 second between retrievals
            base_url
        ]
        
        print(f"Running command: {' '.join(wget_cmd)}")
        
        # Execute wget command
        process = subprocess.run(
            wget_cmd,
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        if process.returncode == 0:
            print(f"wget completed successfully!")
            print(f"All documents saved to: {url_specific_path}")
            return 0  # Success
        else:
            print(f"wget error (code {process.returncode}):")
            print(process.stderr)
            return 1  # Failure
    
    except Exception as e:
        print(f"Error running wget: {e}")
        return 1  # Failure
    
    finally:
        # Change back to the original directory
        os.chdir(original_dir)

# Function to validate URL format
def is_valid_url(url):
    """Check if the provided URL is valid.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    try:
        # More permissive URL validation pattern
        pattern = re.compile(
            r'^(https?://)?'  # http:// or https:// (optional)
            r'(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'  # subdomains
            r'([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])'  # domain name
            r'(\.[a-zA-Z]{2,})'  # TLD (.com, .org, etc.)
            r'(:[0-9]+)?'  # port (optional)
            r'(/[-a-zA-Z0-9()@:%_\+.~#?&//=]*)?'  # path, query params (optional)
            r'$'
        )
        
        return bool(pattern.match(url))
    except re.error:
        # Fallback to a basic check in case the regex has issues
        if '.' not in url:
            return False
        return url.startswith('http://') or url.startswith('https://') or url.startswith('www.')

# Function to get URL from user or command line
def get_url_from_user():
    """Get and validate a URL from the user.
    
    Returns:
        str: Valid URL
    """
    url = None
    
    # Check if URL was provided via command line
    for i, arg in enumerate(sys.argv):
        if arg == '--url' and i + 1 < len(sys.argv):
            url = sys.argv[i + 1]
            if is_valid_url(url):
                print(f"Using URL from command line: {url}")
                return url
            else:
                print(f"Invalid URL format: {url}")
                # Continue to prompt the user
    
    # Prompt the user for URL
    while not url or not is_valid_url(url):
        url = input("Please enter the URL to download documents from: ").strip()
        if not url:
            print("URL cannot be empty.")
        elif not is_valid_url(url):
            print("Invalid URL format. Please enter a valid URL (e.g., https://example.com/docs)")
    
    # Ensure URL has http/https prefix
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    
    return url

# Handle the installation of wget if it's not installed
def ensure_wget_installed():
    """
    Ensure wget is installed on the system.
    Returns True if wget is available, False otherwise.
    """
    try:
        # Check if wget is installed
        result = subprocess.run(
            ["which", "wget"] if sys.platform != "win32" else ["where", "wget"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # wget is installed
            return True
        
        # Try to install wget
        print("wget is not installed. Attempting to install...")
        
        if sys.platform == "darwin":  # macOS
            try:
                # Try using Homebrew
                subprocess.run(["brew", "install", "wget"], check=True)
                print("wget installed successfully using Homebrew")
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Failed to install wget using Homebrew. Homebrew may not be installed.")
        
        elif sys.platform == "linux":
            try:
                # Try apt-get (Debian/Ubuntu)
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "wget"], check=True)
                print("wget installed successfully using apt-get")
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                try:
                    # Try yum (RedHat/CentOS)
                    subprocess.run(["sudo", "yum", "install", "-y", "wget"], check=True)
                    print("wget installed successfully using yum")
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    print("Failed to install wget using package managers.")
        
        elif sys.platform == "win32":  # Windows
            print("Please install wget manually on Windows:")
            print("1. Download from https://eternallybored.org/misc/wget/")
            print("2. Add the wget executable to your PATH")
        
        print("\nPlease install wget manually and try again.")
        return False
        
    except Exception as e:
        print(f"Error checking/installing wget: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Get the home directory for venv path
    home_dir = str(Path.home())
    
    # Create venv name for this specific script
    venv_name = os.path.join(home_dir, "venv", "doc_links_venv")
    
    # Try to switch to the virtual environment
    auto_venv = AutoVirtualEnvironment(custom_name=venv_name)
    auto_venv.auto_switch()
    
    # If we reach here, we should be in the virtual environment
    print(f"Using Python interpreter: {sys.executable}")
    
    # Check if wget is available
    if not ensure_wget_installed():
        sys.exit(1)
    
    # Check for command line arguments
    if len(sys.argv) > 1 and "--venv-activated" not in sys.argv:
        if sys.argv[1] == '--download':
            # Get URL from user for document downloads
            base_url = get_url_from_user()
            
            # Just download documents if explicitly requested
            print("\nStarting document download...")
            result = download_documents(base_url)
            if result == 0:
                print("\nDownload complete! Check the ~/Downloads/py-script-downloads/doc_link downloads directory.")
            else:
                print("\nDownload failed. Please check the error messages above.")
        elif sys.argv[1] == '--help':
            print("Usage: python doc_links.py [OPTION]")
            print("Download documents from a specified URL using wget.")
            print("\nOptions:")
            print("  --download              Download documents from a URL")
            print("  --url [URL]             Specify URL directly (used with --download)")
            print("  --help                  Display this help and exit")
            print("\nExamples:")
            print("  python doc_links.py --download")
            print("  python doc_links.py --download --url https://docs.openwebui.com")
            print("\nDefault wget options:")
            print("  --mirror --convert-links --adjust-extension --page-requisites --no-parent")
    else:
        # If no command is provided, ask the user what to do
        print("\nReady to download documents.")
        choice = input("Would you like to download documents now? (y/n): ").strip().lower()
        if choice == 'y' or choice == 'yes':
            # Get URL from user for document downloads
            base_url = get_url_from_user()
            
            print("\nStarting document download...")
            result = download_documents(base_url)
            if result == 0:
                print("\nDownload complete! Check the ~/Downloads/py-script-downloads/doc_link downloads directory.")
            else:
                print("\nDownload failed. Please check the error messages above.")
        else:
            print("\nTo download documents later, run: python doc_links.py --download")

# 🛠️✨ This script automatically sets up a virtual environment and uses wget to download website content with the specified options.
