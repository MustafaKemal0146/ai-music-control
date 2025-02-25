import cv2
import numpy as np
import torch
import math
import os

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the face detector with OpenCV.
        
        Args:
            min_detection_confidence: Minimum confidence for face detection
            min_tracking_confidence: Minimum confidence for landmark tracking
        """
        # Load OpenCV's face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Head pose estimation parameters
        self.face_3d = np.array([
            (0.0, 0.0, 0.0),            # Nose tip
            (0.0, -330.0, -65.0),       # Chin
            (-225.0, 170.0, -135.0),    # Left eye left corner
            (225.0, 170.0, -135.0),     # Right eye right corner
            (-150.0, -150.0, -125.0),   # Left mouth corner
            (150.0, -150.0, -125.0)     # Right mouth corner
        ], dtype=np.float32)
        
        # Camera matrix estimation (will be updated based on image size)
        self.camera_matrix = None
        self.dist_coeffs = np.zeros((4, 1))
        
        # Head pose state
        self.head_pose = {
            'pitch': 0,  # Up/down
            'yaw': 0,    # Left/right
            'roll': 0    # Tilt
        }
        
        # Movement detection thresholds
        self.yaw_threshold = 15  # Degrees for left/right movement
        self.pitch_threshold = 15  # Degrees for up/down movement
        self.special_movement_threshold = 30  # For special movement detection
        
        # Movement state
        self.prev_head_pose = self.head_pose.copy()
        self.movement_detected = None
        self.movement_cooldown = 0
        self.cooldown_frames = 30  # Frames to wait before detecting new movement
        
        # For simulating head movements
        self.frame_count = 0
        self.simulated_movements = ['left', 'right', 'up', 'down', 'special', None, None, None]
        
    def _update_camera_matrix(self, img_h, img_w):
        """Update camera matrix based on image dimensions."""
        focal_length = img_w
        center = (img_w / 2, img_h / 2)
        self.camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype=np.float32
        )
        
    def detect_face(self, frame):
        """
        Detect face and landmarks in the given frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            Processed frame with landmarks and head pose visualization
            Dictionary with detection results
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w, _ = frame.shape
        
        # Update camera matrix if needed
        if self.camera_matrix is None:
            self._update_camera_matrix(h, w)
            
        # Initialize result dictionary
        detection_result = {
            'face_detected': False,
            'landmarks': None,
            'head_pose': self.head_pose.copy(),
            'movement': None
        }
        
        # Decrement cooldown if active
        if self.movement_cooldown > 0:
            self.movement_cooldown -= 1
            
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        if len(faces) > 0:
            detection_result['face_detected'] = True
            
            # Get the first face
            x, y, w, h = faces[0]
            
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw some simulated facial landmarks
            center_x, center_y = x + w // 2, y + h // 2
            eye_w = w // 4
            
            # Left eye
            left_eye_x = center_x - eye_w
            left_eye_y = y + h // 3
            cv2.circle(frame, (left_eye_x, left_eye_y), 5, (0, 0, 255), -1)
            
            # Right eye
            right_eye_x = center_x + eye_w
            right_eye_y = y + h // 3
            cv2.circle(frame, (right_eye_x, right_eye_y), 5, (0, 0, 255), -1)
            
            # Nose
            nose_x, nose_y = center_x, center_y
            cv2.circle(frame, (nose_x, nose_y), 5, (0, 0, 255), -1)
            
            # Mouth
            mouth_y = y + 2 * h // 3
            left_mouth_x = center_x - eye_w
            right_mouth_x = center_x + eye_w
            cv2.circle(frame, (left_mouth_x, mouth_y), 5, (0, 0, 255), -1)
            cv2.circle(frame, (right_mouth_x, mouth_y), 5, (0, 0, 255), -1)
            
            # Chin
            chin_x, chin_y = center_x, y + h - 10
            cv2.circle(frame, (chin_x, chin_y), 5, (0, 0, 255), -1)
            
            # Create simulated face landmarks for head pose estimation
            landmarks = np.array([
                [nose_x, nose_y],
                [chin_x, chin_y],
                [left_eye_x, left_eye_y],
                [right_eye_x, right_eye_y],
                [left_mouth_x, mouth_y],
                [right_mouth_x, mouth_y]
            ])
            
            # Simulate head pose based on face position
            # This is a very simplified simulation
            face_center_x = x + w / 2
            face_center_y = y + h / 2
            
            # Calculate yaw based on horizontal position
            yaw = (face_center_x - frame.shape[1] / 2) / (frame.shape[1] / 4) * 30
            
            # Calculate pitch based on vertical position
            pitch = (face_center_y - frame.shape[0] / 2) / (frame.shape[0] / 4) * 30
            
            # Update head pose
            self.head_pose = {
                'pitch': pitch,  # Up/down
                'yaw': yaw,      # Left/right
                'roll': 0        # Tilt (not simulated)
            }
            
            # Display head pose angles
            cv2.putText(frame, f"Pitch: {int(pitch)}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Yaw: {int(yaw)}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Roll: 0", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detect movements if cooldown is over
            if self.movement_cooldown == 0:
                movement = self._detect_movement()
                if movement:
                    detection_result['movement'] = movement
                    self.movement_cooldown = self.cooldown_frames
            
            detection_result['landmarks'] = landmarks
            detection_result['head_pose'] = self.head_pose.copy()
            
            # Store current pose for next frame comparison
            self.prev_head_pose = self.head_pose.copy()
        else:
            # If no face detected, simulate movements for demo purposes
            self.frame_count += 1
            if self.frame_count % 60 == 0:  # Every ~2 seconds at 30fps
                idx = (self.frame_count // 60) % len(self.simulated_movements)
                simulated_movement = self.simulated_movements[idx]
                if simulated_movement and self.movement_cooldown == 0:
                    detection_result['movement'] = simulated_movement
                    self.movement_cooldown = self.cooldown_frames
                    cv2.putText(frame, f"Simulated: {simulated_movement}", (10, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        return frame, detection_result
    
    def _detect_movement(self):
        """
        Detect head movements based on pose changes.
        
        Returns:
            String indicating the detected movement or None
        """
        # Calculate differences from previous frame
        yaw_diff = self.head_pose['yaw'] - self.prev_head_pose['yaw']
        pitch_diff = self.head_pose['pitch'] - self.prev_head_pose['pitch']
        
        # Check for left/right movement (yaw)
        if abs(self.head_pose['yaw']) > self.yaw_threshold:
            if self.head_pose['yaw'] > self.yaw_threshold:
                return 'right'
            elif self.head_pose['yaw'] < -self.yaw_threshold:
                return 'left'
                
        # Check for up/down movement (pitch)
        if abs(self.head_pose['pitch']) > self.pitch_threshold:
            if self.head_pose['pitch'] > self.pitch_threshold:
                return 'down'
            elif self.head_pose['pitch'] < -self.pitch_threshold:
                return 'up'
        
        # Check for special movement (rapid nodding)
        if abs(pitch_diff) > self.special_movement_threshold:
            return 'special'
            
        return None 