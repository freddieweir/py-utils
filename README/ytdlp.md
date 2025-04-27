# YouTube Downloader Utility

The `ytdlp.py` script is a convenient wrapper around the powerful [yt-dlp](https://github.com/yt-dlp/yt-dlp) tool for downloading videos from YouTube and other platforms. It features automatic virtual environment setup and provides a user-friendly interface for downloading videos or extracting audio.

## Features

- Automatic virtual environment creation and management
- Download videos in MP4 format with best available quality
- Extract audio from videos as MP3 files
- Process multiple URLs in a single session
- Consistent download location across all scripts
- Detailed progress information

## Requirements

The script automatically installs the following packages in a virtual environment:
- yt-dlp (version specified in the script)

## Usage

Simply run the script:

```bash
python ytdlp.py
```

Upon first run, the script will:
1. Create a virtual environment (if it doesn't exist)
2. Install yt-dlp and its dependencies
3. Restart itself within the virtual environment

You'll then be prompted to:
1. Choose between video or audio-only download
2. Enter one or more YouTube URLs (separated by commas)

## Download Options

### Video Download

When video mode is selected:
- Videos are downloaded in MP4 format with the best available quality
- Thumbnails are embedded into the video file
- Metadata is preserved
- Subtitles are embedded when available

### Audio-Only Download

When audio-only mode is selected:
- Audio is extracted from videos and saved as MP3 files
- Audio quality is set to 192 kbps
- Metadata is preserved

## Examples

### Downloading a Single Video

```
Enter (v)ideo or (a)udio only for all URLs in this session? (v/a, default: v): v
Video mode selected. All downloads will be saved as MP4.

Enter YouTube URL(s) (separate multiple URLs with commas, or 'q' to quit): https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Downloading Multiple Videos

```
Enter (v)ideo or (a)udio only for all URLs in this session? (v/a, default: v): v
Video mode selected. All downloads will be saved as MP4.

Enter YouTube URL(s) (separate multiple URLs with commas, or 'q' to quit): https://www.youtube.com/watch?v=dQw4w9WgXcQ, https://www.youtube.com/watch?v=9bZkp7q19f0
```

### Extracting Audio from a Video

```
Enter (v)ideo or (a)udio only for all URLs in this session? (v/a, default: v): a
Audio-only mode selected. All downloads will be saved as MP3.

Enter YouTube URL(s) (separate multiple URLs with commas, or 'q' to quit): https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Download Location

Files are automatically saved to:
```
~/Downloads/py-script-downloads/yt-dlp downloads/
```

## Notes

- The script utilizes the `module_venv.py` utility to manage virtual environments
- Downloaded files are tracked in a download archive to prevent re-downloading the same content
- The script handles errors gracefully, including for private or members-only videos
- You can quit the script at any time by entering 'q' at the URL prompt 