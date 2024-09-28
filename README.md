# Vinny's Terminal ASCII Player (VTAP)

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Examples](#examples)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project allows you to download a YouTube video and play it in your terminal as ASCII art with synchronized audio. It leverages multithreading and the experimental free-threaded build of CPython 3.13 to process video frames efficiently, ensuring smooth playback at the proper frames per second (FPS).

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.13** (Free-threaded build without the Global Interpreter Lock)
- **ffmpeg** or **ffplay** (for audio playback)
- **pip** (Python package installer)

### Required Python Packages

- `pytube` (for downloading YouTube videos)
- `opencv-python` (for video processing)
- `numpy` (for numerical operations)

You can install the Python packages using:

```bash
pip install -r requirements.txt
```

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/VinnyVanGogh/vtap.git
```

### Install Dependencies

Navigate to the project directory and install the required packages:

```bash
cd vtap
pip install -r requirements.txt
```

Ensure that `ffmpeg` or `ffplay` is installed and accessible from your command line:

- **On macOS with Homebrew:**

  ```bash
  brew install ffmpeg
  ```

- **On Ubuntu/Debian:**

  ```bash
  sudo apt-get install ffmpeg
  ```

- **On Windows:**

  Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH.

## Usage

### Command-Line Arguments

The script accepts several command-line arguments to customize the playback:

- `--url`: **(Required)** The YouTube video URL.
- `--chars`: Characters to use for ASCII art (default: `' .:-=+*#%@'`).
- `--scale`: Scale factor for ASCII art (e.g., `0.5` for half size; default: `1.0`).
- `--colors`: Enable colored ASCII art.
- `--fullscreen`: Fit ASCII art to terminal size.
- `--demo`: Play a demo video.

### Examples

**Demo Mode:**

```bash
python vtap.py --demo
```

**Basic Usage:**

```bash
python vtap.py --url 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

**Custom Characters and Scaling:**

```bash
python vtap.py --url 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --chars ' .:-=+*#%@' --scale 0.5
```

**Enable Colored ASCII Art:**

```bash
python vtap.py --url 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --colors
```

**Fullscreen Mode:**

```bash
python vtap.py --url 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' --fullscreen
```

## How It Works

1. **Download Video:**

   The script uses `pytube` to download the specified YouTube video in MP4 format with both audio and video streams.

2. **Multithreaded Processing:**

   - **Frame Reading Thread:** Reads video frames and queues them for processing.
   - **Frame Processing Threads:** Multiple threads convert frames to ASCII art in parallel.
   - **Frame Display Thread:** Displays the ASCII frames in the terminal at the correct FPS.
   - **Audio Playback Thread:** Plays the video's audio simultaneously using `ffplay`.

3. **ASCII Art Generation:**

   - Each video frame is resized according to the specified scale or terminal size.
   - Frames are converted to grayscale and mapped to ASCII characters based on pixel intensity.
   - Optionally, color information is added using ANSI escape codes.

4. **Synchronized Playback:**

   - The display thread ensures that frames are shown at intervals matching the video's FPS.
   - Audio playback is synchronized with the video frames for a cohesive experience.

## Project Structure

```
vtap/
├── vtap.py
├── downloader.py
├── ascii_art.py
├── ascii_video.py
├── audio_player.py
├── my_args.py
├── requirements.txt
```

### File Descriptions

- **vtap.py:** The entry point of the program; parses arguments and initiates threads.
- **downloader.py:** Handles downloading the YouTube video.
- **ascii_art.py:** Contains the `AsciiArt` class for converting frames to ASCII art.
- **ascii_video.py:** Manages video playback, including multithreading for frame processing.
- **audio_player.py:** Handles audio playback using `ffplay`.
- **my_args.py:** Contains the argument parser configuration.
- **requirements.txt:** Lists the required Python packages.

## Contributing

We welcome contributions to improve this project. To contribute, follow these steps:

1. **Fork the Repository:**

   Click the "Fork" button at the top right of the repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/<your-username>/vtap.git
   cd vtap
   ```

3. **Create a Branch:**

   ```bash
   git checkout -b 'feature/your-feature-name'
   ```

4. **Make Your Changes:**

   - Improve code efficiency.
   - Fix bugs.
   - Add new features.

5. **Commit Your Changes:**

   ```bash
   git commit -am 'Add your commit message here'
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request:**

   - Go to the original repository.
   - Click on "Pull Requests" and then "New Pull Request".
   - Select your branch and submit the pull request.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software in accordance with the license.

---

**Disclaimer:** This project is intended for educational and personal use. Ensure you comply with YouTube's Terms of Service and respect copyright laws when downloading and using YouTube content.

---

## Acknowledgments

- **CPython Development Team:** For introducing the experimental free-threaded build in Python 3.13.
- **Contributors:** Thanks to everyone who has contributed to this project.
- **OpenCV and NumPy:** For providing powerful tools for image and video processing.

---

## Troubleshooting

### Common Issues

- **SSL Certificate Error when Downloading Videos:**

  If you encounter an SSL error, you may need to install the necessary certificates. On macOS, run the `Install Certificates.command` script located in `/Applications/Python 3.13/`.

- **Slow Performance:**

  - Reduce the `--scale` factor to lower the resolution.
  - Use fewer characters in `--chars`.
  - Disable colors by omitting the `--colors` flag.

- **Audio Not Playing:**

  Ensure that `ffmpeg` or `ffplay` is correctly installed and accessible from your command line.

### Support

If you experience any issues or have questions, feel free to open an issue on the [GitHub repository](https://github.com/VinnyVanGogh/vtap/issues).

---

## Additional Information

### Free-Threaded Python Build

This project utilizes the experimental free-threaded build of CPython 3.13, which removes the Global Interpreter Lock (GIL), allowing true parallelism with threads.

**Note:** Python 3.13 is under development, and the free-threaded build is experimental. Ensure you are comfortable with using development versions of Python.

### Installing Python 3.13 Free-Threaded Build

1. **Download the Source Code:**

   ```bash
   git clone https://github.com/python/cpython.git
   cd cpython
   git checkout 3.13
   ```

2. **Build Python with Free-Threading Enabled:**

   ```bash
   ./configure --disable-gil
   make
   ```

3. **Install Python:**

   ```bash
   sudo make altinstall
   ```

   **Note:** Use `make altinstall` to avoid overwriting your system's default Python.

---
