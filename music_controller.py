import os
import pygame
import random
from pathlib import Path

class MusicController:
    def __init__(self, music_dir="music"):
        """
        Initialize the music controller.
        
        Args:
            music_dir: Directory containing music files (mp3, wav)
        """
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Music state
        self.is_playing = False
        self.current_track_index = 0
        self.volume = 0.5  # 0.0 to 1.0
        
        # Set up music directory and track list
        self.music_dir = music_dir
        self.ensure_music_dir()
        self.tracks = self.load_tracks()
        
        # Log messages
        self.log_messages = []
        
    def ensure_music_dir(self):
        """Create music directory if it doesn't exist."""
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)
            self.add_log("Created music directory")
            
            # Create a README file in the music directory
            with open(os.path.join(self.music_dir, "README.txt"), "w") as f:
                f.write("Place your music files (MP3, WAV) in this directory.\n")
                f.write("The application will automatically detect and play them.\n")
    
    def load_tracks(self):
        """
        Load music tracks from the music directory.
        
        Returns:
            List of track paths
        """
        valid_extensions = ['.mp3', '.wav', '.ogg']
        tracks = []
        
        try:
            for file in os.listdir(self.music_dir):
                file_path = os.path.join(self.music_dir, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in valid_extensions):
                    tracks.append(file_path)
        except Exception as e:
            self.add_log(f"Error loading tracks: {str(e)}")
            
        if not tracks:
            self.add_log("No music tracks found. Please add MP3 or WAV files to the music directory.")
            # Add a sample track path that doesn't exist to prevent errors
            tracks = [os.path.join(self.music_dir, "sample.mp3")]
            
        return tracks
    
    def reload_tracks(self):
        """Reload the track list from the music directory."""
        self.tracks = self.load_tracks()
        self.add_log(f"Reloaded tracks: found {len(self.tracks)} music files")
        
        # Reset current track index if it's out of bounds
        if self.current_track_index >= len(self.tracks):
            self.current_track_index = 0
    
    def play(self):
        """Play the current track."""
        if not self.tracks:
            self.add_log("No tracks available to play")
            return
            
        try:
            if not self.is_playing:
                if not pygame.mixer.music.get_busy():
                    # Load and play the current track
                    pygame.mixer.music.load(self.tracks[self.current_track_index])
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play()
                else:
                    # Unpause if paused
                    pygame.mixer.music.unpause()
                    
                self.is_playing = True
                track_name = os.path.basename(self.tracks[self.current_track_index])
                self.add_log(f"Playing: {track_name}")
        except Exception as e:
            self.add_log(f"Error playing music: {str(e)}")
    
    def pause(self):
        """Pause the current track."""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.add_log("Paused playback")
    
    def next_track(self):
        """Play the next track."""
        if not self.tracks:
            return
            
        self.current_track_index = (self.current_track_index + 1) % len(self.tracks)
        track_name = os.path.basename(self.tracks[self.current_track_index])
        self.add_log(f"Next track: {track_name}")
        
        # Stop current playback and start the new track
        pygame.mixer.music.stop()
        self.play()
    
    def previous_track(self):
        """Play the previous track."""
        if not self.tracks:
            return
            
        self.current_track_index = (self.current_track_index - 1) % len(self.tracks)
        track_name = os.path.basename(self.tracks[self.current_track_index])
        self.add_log(f"Previous track: {track_name}")
        
        # Stop current playback and start the new track
        pygame.mixer.music.stop()
        self.play()
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def set_volume(self, volume):
        """
        Set the playback volume.
        
        Args:
            volume: Float between 0.0 and 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        self.add_log(f"Volume set to {int(self.volume * 100)}%")
    
    def shuffle(self):
        """Shuffle the playlist and play a random track."""
        if not self.tracks:
            return
            
        self.current_track_index = random.randint(0, len(self.tracks) - 1)
        track_name = os.path.basename(self.tracks[self.current_track_index])
        self.add_log(f"Shuffled to: {track_name}")
        
        # Stop current playback and start the new track
        pygame.mixer.music.stop()
        self.play()
    
    def handle_movement(self, movement):
        """
        Handle head movement commands.
        
        Args:
            movement: String indicating the detected movement
                     ('left', 'right', 'up', 'down', 'special')
        """
        if movement == 'left':
            self.previous_track()
        elif movement == 'right':
            self.next_track()
        elif movement in ['up', 'down']:
            self.toggle_play_pause()
        elif movement == 'special':
            self.shuffle()
    
    def get_current_track_info(self):
        """
        Get information about the current track.
        
        Returns:
            Dictionary with track information
        """
        if not self.tracks:
            return {"name": "No tracks available", "status": "stopped", "index": 0, "total": 0}
            
        track_path = self.tracks[self.current_track_index]
        track_name = os.path.basename(track_path)
        
        return {
            "name": track_name,
            "status": "playing" if self.is_playing else "paused",
            "index": self.current_track_index + 1,
            "total": len(self.tracks)
        }
    
    def add_log(self, message):
        """
        Add a log message.
        
        Args:
            message: Log message string
        """
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
            
        self.log_messages.append(message)
        # Keep only the last 100 messages
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)
    
    def get_logs(self):
        """
        Get all log messages.
        
        Returns:
            List of log message strings
        """
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
            
        return self.log_messages
    
    def cleanup(self):
        """Clean up resources."""
        pygame.mixer.music.stop()
        pygame.mixer.quit() 