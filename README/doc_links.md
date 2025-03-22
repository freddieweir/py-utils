# Documentation Downloader

The `doc_links.py` script is a powerful utility for downloading documentation or other linked documents from websites. It uses wget to recursively mirror sites, ensuring all documentation pages and their assets are downloaded for offline access.

## Features

- Recursively downloads entire documentation sites
- Preserves the site's structure and assets
- Converts links for offline browsing
- Organizes downloads in URL-specific folders
- Handles SSL certificate issues gracefully
- Provides simulated user agent and random delays to avoid blocking

## Requirements

This script requires:
- wget (command-line utility)
- Python 3.6+

The script will check if wget is installed and inform you if it's missing.

## Usage

Simply run the script:

```bash
python doc_links.py
```

or

```bash
python doc_links.py --url https://docs.example.com
```

You'll be prompted to enter a URL if not provided via command line. The script will:
1. Validate the URL format
2. Create a dedicated directory for the downloaded content
3. Execute wget with appropriate parameters to mirror the site
4. Display progress during the download

## Technical Details

The script uses the following wget parameters:
- `--recursive`: Download recursively
- `--level=inf`: No limit on recursion depth
- `--mirror`: Mirror the website
- `--convert-links`: Convert links to local
- `--adjust-extension`: Add appropriate extensions
- `--page-requisites`: Get all page assets
- `--no-clobber`: Don't re-download existing files
- `--random-wait`: Add random delays between requests
- Custom user agent to simulate a regular browser

## Download Location

Documents are saved to:
```
~/Downloads/py-script-downloads/doc_link downloads/[domain-specific-folder]/
```

Where `[domain-specific-folder]` is a sanitized version of the URL.

## Examples

### Downloading Python Documentation

```
Please enter the URL to download documents from: https://docs.python.org/3/
Created URL-specific directory: /Users/username/Downloads/py-script-downloads/doc_link downloads/docs_python_org_3
Starting download from https://docs.python.org/3/
...
wget completed successfully!
All documents saved to: /Users/username/Downloads/py-script-downloads/doc_link downloads/docs_python_org_3
```

### Downloading Technical Documentation

```
Please enter the URL to download documents from: https://learn.microsoft.com/en-us/azure/
Created URL-specific directory: /Users/username/Downloads/py-script-downloads/doc_link downloads/learn_microsoft_com_en-us_azure
Starting download from https://learn.microsoft.com/en-us/azure/
...
wget completed successfully!
All documents saved to: /Users/username/Downloads/py-script-downloads/doc_link downloads/learn_microsoft_com_en-us_azure
```

## Notes

- The script creates a sanitized directory name from the URL to avoid filesystem issues
- The download can take considerable time for large documentation sites
- Some sites may block wget or limit what can be downloaded
- The script sets a reasonable timeout and retry limit
- For best results, specify a specific documentation section rather than a very large site
- All assets (CSS, JavaScript, images) needed for offline viewing are downloaded 