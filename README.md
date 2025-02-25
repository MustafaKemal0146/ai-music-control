# AI Music Control

A Python application that uses head movements to control music playback through computer vision and deep learning.

## Features

- Real-time face detection and facial landmark tracking
- Control music with head movements:
  - Turn head right: Next song
  - Turn head left: Previous song
  - Move head up/down: Pause/Play music
  - Special movement detection for additional controls
- User-friendly GUI with video feed and logging console

## Requirements

- Python 3.7+
- Webcam
- Dependencies listed in requirements.txt

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```
python main.py
```

## Project Structure

- `main.py`: Entry point for the application
- `face_detector.py`: Face detection and landmark tracking module
- `music_controller.py`: Music playback control module
- `gui.py`: PyQt5-based graphical user interface
- `utils.py`: Utility functions and helpers

## License

See the LICENSE file for details. 

