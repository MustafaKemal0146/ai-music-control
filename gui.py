import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                            QSlider, QFrame, QSplitter)
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtWidgets import QFileDialog

class VideoWidget(QLabel):
    """Widget for displaying video feed."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)  # 16:9 aspect ratio
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #000000;")
        
    def update_frame(self, frame):
        """Update the displayed frame."""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to QImage and then to QPixmap
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to fit the widget while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_img)
        self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

class LogConsole(QTextEdit):
    """Widget for displaying log messages."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            border: 1px solid #3c3c3c;
            padding: 5px;
        """)
        
    def append_log(self, message):
        """Append a log message to the console."""
        self.append(f"> {message}")
        # Scroll to the bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def update_logs(self, log_messages):
        """Update the console with a list of log messages."""
        self.clear()
        for message in log_messages:
            self.append_log(message)

class MusicControlPanel(QWidget):
    """Panel for displaying music controls and information."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Track info
        self.track_info_label = QLabel("No track playing")
        self.track_info_label.setAlignment(Qt.AlignCenter)
        self.track_info_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #f0f0f0;
            padding: 5px;
        """)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("⏮")
        self.play_pause_button = QPushButton("⏯")
        self.next_button = QPushButton("⏭")
        self.shuffle_button = QPushButton("🔀")
        
        for button in [self.prev_button, self.play_pause_button, self.next_button, self.shuffle_button]:
            button.setFixedSize(40, 40)
            button.setFont(QFont('Arial', 16))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                    border-radius: 20px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #4d4d4d;
                }
            """)
            button_layout.addWidget(button)
            
        # Volume slider
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        volume_label.setStyleSheet("color: #f0f0f0;")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #2d2d2d;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4d4d4d;
                border: 1px solid #5d5d5d;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #5d5d5d;
            }
        """)
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        # Add all components to the layout
        layout.addWidget(self.track_info_label)
        layout.addLayout(button_layout)
        layout.addLayout(volume_layout)
        
        self.setLayout(layout)
        
    def update_track_info(self, track_info):
        """Update the displayed track information."""
        if track_info:
            status = "▶️" if track_info["status"] == "playing" else "⏸️"
            self.track_info_label.setText(f"{status} {track_info['name']} ({track_info['index']}/{track_info['total']})")

class HeadControlApp(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Set up timer for video updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
        # Initialize camera, face detector, and music controller
        self.cap = None
        self.face_detector = None
        self.music_controller = None
        
    def setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Head Movement Music Control")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        # You can replace this with an actual logo image
        logo_label.setText("🎵")
        logo_label.setFont(QFont('Arial', 24))
        logo_label.setStyleSheet("color: #f0f0f0;")
        
        title_label = QLabel("Head Movement Music Control")
        title_label.setFont(QFont('Arial', 18, QFont.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        # Add folder button
        self.add_folder_button = QPushButton("Add Music Folder")
        self.add_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #f0f0f0;
                border-radius: 4px;
                padding: 6px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        header_layout.addWidget(self.add_folder_button)
        
        # Video widget
        self.video_widget = VideoWidget()
        
        # Music control panel
        self.music_panel = MusicControlPanel()
        
        # Log console
        self.log_console = LogConsole()
        
        # Add widgets to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.video_widget, 3)  # Video takes more space
        main_layout.addWidget(self.music_panel, 1)
        main_layout.addWidget(self.log_console, 1)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
            }
            QLabel {
                color: #f0f0f0;
            }
        """)
        
    def set_controllers(self, face_detector, music_controller):
        """Set the face detector and music controller instances."""
        self.face_detector = face_detector
        self.music_controller = music_controller
        
        # Connect music control signals
        self.music_panel.prev_button.clicked.connect(self.music_controller.previous_track)
        self.music_panel.play_pause_button.clicked.connect(self.music_controller.toggle_play_pause)
        self.music_panel.next_button.clicked.connect(self.music_controller.next_track)
        self.music_panel.shuffle_button.clicked.connect(self.music_controller.shuffle)
        self.music_panel.volume_slider.valueChanged.connect(
            lambda value: self.music_controller.set_volume(value / 100.0))
        
        # Connect add folder button
        self.add_folder_button.clicked.connect(self.select_music_folder)
        
    def select_music_folder(self):
        """Open a dialog to select a music folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder:
            self.music_controller.music_dir = folder
            self.music_controller.reload_tracks()
            self.log_console.append_log(f"Music folder set to: {folder}")
        
    def start_camera(self, camera_index=0):
        """Start the camera capture."""
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.log_console.append_log("Error: Could not open camera.")
            return False
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        
        # Start the timer for frame updates
        self.timer.start(33)  # ~30 FPS
        self.log_console.append_log("Camera started successfully.")
        return True
        
    def update_frame(self):
        """Update the video frame and process head movements."""
        if self.cap is None or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.log_console.append_log("Error: Failed to capture frame.")
            return
            
        # Flip the frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)
        
        # Process the frame with face detector
        if self.face_detector:
            processed_frame, detection_result = self.face_detector.detect_face(frame)
            
            # Handle detected movement
            if detection_result['movement'] and self.music_controller:
                self.music_controller.handle_movement(detection_result['movement'])
                self.log_console.append_log(f"Detected movement: {detection_result['movement']}")
                
            # Update the video widget with the processed frame
            self.video_widget.update_frame(processed_frame)
        else:
            # If no face detector, just show the raw frame
            self.video_widget.update_frame(frame)
            
        # Update music info and logs
        if self.music_controller:
            self.music_panel.update_track_info(self.music_controller.get_current_track_info())
            self.log_console.update_logs(self.music_controller.get_logs())
            
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the timer
        self.timer.stop()
        
        # Release the camera
        if self.cap and self.cap.isOpened():
            self.cap.release()
            
        # Clean up music controller
        if self.music_controller:
            self.music_controller.cleanup()
            
        # Accept the close event
        event.accept() 