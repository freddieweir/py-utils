# File Splitter Utility

The `9mb_split_file.py` script helps you split large files into smaller chunks of a specified size (default 9MB). It's particularly useful for sharing large files through platforms with file size limits or extracting audio from video files before splitting.

## Features

- Split files into smaller chunks of configurable size
- Extract audio from video files before splitting (uses moviepy)
- Automatic virtual environment creation and management
- Preserves the original file with a "- ORIGINAL" suffix
- Organizes chunks in a dedicated directory named after the original file

## Requirements

The script automatically installs the following packages in a virtual environment:
- moviepy==1.0.3 (for audio extraction)

## Usage

Simply run the script:

```bash
python 9mb_split_file.py
```

Upon first run, the script will:
1. Create a virtual environment (if it doesn't exist)
2. Install moviepy and its dependencies
3. Restart itself within the virtual environment

You'll then be guided through the following steps:

1. A list of files in the current directory will be displayed
2. You'll be prompted to select a file by entering its number
3. If the selected file is a video, audio will be extracted as an MP3 file
4. You'll be asked to specify the maximum chunk size in MB (default: 9MB)
5. The file will be split into chunks of the specified size

## Audio Extraction

For video files (`.mov`, `.mp4`, `.avi`, `.mkv`, `.wmv`), the script will:
1. Extract the audio track using moviepy
2. Save it as an MP3 file with the same base name
3. Split the MP3 file instead of the original video

## Output Organization

For a file named `example.mp3`:
1. A directory named `example` will be created
2. The original file will be moved to `example/example - ORIGINAL.mp3`
3. Chunks will be created as:
   - `example/example - Part 1.mp3`
   - `example/example - Part 2.mp3`
   - etc.

## Examples

### Splitting a Large Audio File

```
Select a file:
1. lecture.mp3
2. presentation.pdf
3. document.txt
Enter the number of your chosen file: 1

Created directory: lecture
Enter the maximum chunk size in MB (default: 9): 9
Wrote chunk 1 to lecture/lecture - Part 1.mp3
Wrote chunk 2 to lecture/lecture - Part 2.mp3
Moved original file to lecture/lecture - ORIGINAL.mp3
```

### Extracting Audio from Video and Splitting

```
Select a file:
1. video.mp4
2. document.pdf
Enter the number of your chosen file: 1

Extracting audio from video.mp4...
Audio extracted and saved to video.mp3
Created directory: video
Enter the maximum chunk size in MB (default: 9): 5
Wrote chunk 1 to video/video - Part 1.mp3
Wrote chunk 2 to video/video - Part 2.mp3
Wrote chunk 3 to video/video - Part 3.mp3
Moved original file to video/video - ORIGINAL.mp3
```

## Notes

- The script utilizes the `module_venv.py` utility to manage virtual environments
- For video files, only the audio is extracted and split, not the video itself
- The script runs in the directory it's executed from and operates on files in that directory
- Original files are preserved with a "- ORIGINAL" suffix 