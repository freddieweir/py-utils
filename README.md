# HoloEyes

HoloEyes is a macOS utility that creates a transparent, always-on-top, click-through video window for your main screen. It is designed to help users (especially those with ADHD) stay focused by playing vibrant, colorful local videos in the background, without interfering with normal computer use.

## Directory Structure
- `HoloEyes/` — Main HoloEyes app code and logic

## Features
- Transparent, borderless, always-on-top window
- Video playback (local files only)
- Live opacity control (hotkeys or API)
- Click-through and interactive toggle
- Multi-monitor support
- Colorful, cyberpunk-inspired UI
- ADHD-friendly, highly interactive controls
- No media files are ever committed to the repo

## Usage
1. Place your sample videos in the `HoloEyes/samples/` folder.
2. (Optional) Run `convert_to_1080p.py` to ensure all videos are 1080p for maximum compatibility.
3. Run the main script in `HoloEyes/` to launch HoloEyes:
   ```
   python3 HoloEyes/overlay_main.py
   ```
4. Select your video and monitor when prompted.
5. Use hotkeys or the API to control opacity and interactivity.

---

**Note:** No media files are included in this repo, and `.gitignore` ensures your videos are never uploaded.

---

## Roadmap

### Planned Features
- **Screen Capture Overlay:**
  - Integrate the ability to capture a region or window from another screen (e.g., a YouTube video playing in a browser) and display it as an overlay.
  - This will serve as an alternative to browser Picture-in-Picture (PiP), allowing you to overlay any content from any app or browser window.
  - User will be able to select which screen/window/region to capture, and the overlay will update in real time.
- **Window/Region Selection UI:**
  - Interactive UI to select which window or screen region to capture for overlay.
- **Performance Optimizations:**
  - Ensure smooth, low-latency capture and overlay, even on high-resolution displays.
- **Audio Routing (optional):**
  - Optionally route audio from the captured source to the overlay or mute as needed.
- **More Integrations:**
  - Support for additional input sources (e.g., webcam, external devices).
- **Customizable Overlays:**
  - Add more themes, color schemes, and ADHD-friendly visual effects.
