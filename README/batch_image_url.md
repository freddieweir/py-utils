# Batch Image Downloader

The `batch_image_url.py` script allows you to download all images from a specified website URL. It handles both static and dynamically loaded content, ensuring you can extract images from modern websites.

## Features

- Downloads all images from a given URL
- Uses Selenium to capture dynamically loaded content
- Extracts highest quality images when multiple sources are available
- Organizes downloads in a folder named after the website
- Handles both absolute and relative image URLs
- Automatic virtual environment creation and management

## Requirements

The script automatically installs the following packages in a virtual environment:
- beautifulsoup4
- requests
- selenium

Additionally, you'll need:
- Chrome browser installed (for Selenium)

## Usage

Simply run the script:

```bash
python batch_image_url.py
```

Upon first run, the script will:
1. Create a virtual environment (if it doesn't exist)
2. Install the required packages
3. Restart itself within the virtual environment

You'll then be prompted to enter a website URL. The script will:
1. Open the website in a headless Chrome browser
2. Wait for images to load
3. Extract all image URLs
4. Download each image to a dedicated folder

## How It Works

1. **Page Loading**: Uses Selenium with a headless Chrome browser to load the page completely, including any JavaScript-rendered content
2. **Image Extraction**: Parses the HTML using BeautifulSoup to find all image tags
3. **Quality Selection**: For images with multiple sources (via srcset), selects the highest quality version
4. **Download Process**: Downloads each image, preserving the original filename

## Download Location

Images are saved to:
```
~/Downloads/py-script-downloads/batch_images/[website-name]/
```

Where `[website-name]` is derived from the URL.

## Examples

### Downloading Images from a Blog

```
Enter the URL: https://example.com/blog-post
Created download directory: /Users/username/Downloads/py-script-downloads
Created script directory: /Users/username/Downloads/py-script-downloads/batch_images
Found 12 images to download.
Attempting to download image 1: https://example.com/images/header.jpg
Downloaded: header.jpg
...
```

### Handling E-commerce Product Pages

```
Enter the URL: https://example.com/product
Created download directory: /Users/username/Downloads/py-script-downloads
Created script directory: /Users/username/Downloads/py-script-downloads/batch_images
Found 24 images to download.
Attempting to download image 1: https://example.com/images/product-1-large.jpg
Downloaded: product-1-large.jpg
...
```

## Notes

- The script utilizes the `module_venv.py` utility to manage virtual environments
- Selenium runs Chrome in headless mode (no visible browser window)
- For websites with many images, the download process may take some time
- Some websites may block automated image downloads or limit access via robots.txt
- The script handles relative image URLs by converting them to absolute URLs 