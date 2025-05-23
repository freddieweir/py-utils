import os
import re
import sys
from urllib.parse import urljoin
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
REQUIRED_PACKAGES = [
    'beautifulsoup4',
    'requests',
    'selenium'
]

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
    script_dir = download_dir / "batch_images"
    if not script_dir.exists():
        os.makedirs(script_dir, exist_ok=True)
        print(f"Created script directory: {script_dir}")
    
    return script_dir

def create_folder(url):
    """Create a folder named after the URL's title."""
    folder_name = os.path.basename(url.strip('/'))
    folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)
    
    # Create the folder within the downloads directory
    download_path = os.path.join(get_download_dir(), folder_name)
    os.makedirs(download_path, exist_ok=True)
    return download_path

def get_page_source(url):
    """Use Selenium to get the page source, including dynamically loaded content."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )
        return driver.page_source
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None
    finally:
        driver.quit()

def extract_image_urls(page_source):
    """Extract image URLs from the page source, prioritizing higher-quality images."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(page_source, 'html.parser')
    image_urls = []
    
    for img_tag in soup.find_all('img'):
        # Check if srcset is available (contains multiple image sources)
        if img_tag.get('srcset'):
            # Extract the highest quality image from srcset
            srcset = img_tag['srcset']
            image_url = None
            # Split srcset into different sources and choose the largest one
            sources = srcset.split(', ')
            for src in sources:
                src_url = src.split()[0]
                if not image_url or len(src_url) > len(image_url):
                    image_url = src_url
            if image_url:
                image_urls.append(image_url)
        else:
            # Fallback to the original src attribute
            image_url = img_tag.get('src')
            if image_url:
                image_urls.append(image_url)
                
    return image_urls

def download_image(img_url, folder_name):
    """Download an image and save it to the specified folder."""
    import requests
    
    try:
        response = requests.get(img_url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Extract the image file name
        img_name = os.path.basename(urljoin(img_url, img_url))
        img_path = os.path.join(folder_name, img_name)
        
        # Save the image
        with open(img_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {img_name}")
        return True
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")
        return False

def download_images_from_url(url):
    """Main function to download images from a given URL."""
    folder_name = create_folder(url)
    
    # Get the full page source with Selenium
    page_source = get_page_source(url)
    if not page_source:
        print("Failed to fetch page source. Exiting.")
        return
    
    # Extract image URLs
    image_urls = extract_image_urls(page_source)
    print(f"Found {len(image_urls)} images to download.")
    
    # Download each image
    for i, img_url in enumerate(image_urls, start=1):
        # Handle relative URLs
        img_url = urljoin(url, img_url)
        print(f"Attempting to download image {i}: {img_url}")
        if download_image(img_url, folder_name):
            print(f"Successfully downloaded image {i}.")

def main():
    # Get the home directory for venv path
    home_dir = str(Path.home())
    
    # Create venv name for this specific script
    venv_name = os.path.join(home_dir, "venv", "batch_image_venv")
    
    # Setup auto virtual environment with required packages
    auto_venv = AutoVirtualEnvironment(custom_name=venv_name, auto_packages=REQUIRED_PACKAGES)
    
    # Try to switch to the virtual environment with required packages
    # This will create it if it doesn't exist and re-execute the script
    auto_venv.auto_switch()
    
    # If we reach here, we should be in the virtual environment
    print(f"Using Python interpreter: {sys.executable}")
    
    url = input("Enter the URL: ")
    if not url:
        print("Please provide a valid URL.")
        return
    download_images_from_url(url)

if __name__ == "__main__":
    main()
