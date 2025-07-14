"""
Configuration file for YouTube to Shorts pipeline
"""

# Video settings
VIDEO_CONFIG = {
    "target_width": 1080,
    "target_height": 1920,  # 9:16 aspect ratio for shorts
    "zoom_factor": 1.3,  # Zoom factor for both podcast and gameplay videos
    "fps": 30,
    "codec": "libx264",
    "audio_codec": "aac"
}

# Engagement analysis settings
ENGAGEMENT_CONFIG = {
    "min_clip_duration": 15,  # seconds
    "max_clip_duration": 60,  # seconds
    "text_weight": 0.4,  # Weight for text-based analysis
    "audio_weight": 0.6,  # Weight for audio-based analysis
    "max_segments": 10  # Maximum number of segments to analyze
}

# Subtitle settings
SUBTITLE_CONFIG = {
    "font_size": 45,
    "font_color": "white",
    "stroke_color": "black",
    "stroke_width": 3,
    "max_width": 1000,  # Maximum width in pixels
    "position": "center",  # 'center', 'bottom', 'top'
    "margin_bottom": 100,  # Margin from bottom in pixels
    "fade_duration": 0.3,  # Fade in/out duration in seconds
    "highlight_effect": True,  # Enable fade in/out highlighting
}

# Whisper settings
WHISPER_CONFIG = {
    "model": "base",  # Options: tiny, base, small, medium, large
    "language": None,  # Auto-detect
    "task": "transcribe"
}

# File paths
PATHS = {
    "inputs": "inputs",
    "outputs": "outputs",
    "transcripts": "transcripts",
    "temp": "temp",
    "audio_segments": "audio_segments"
}

# Processing settings
PROCESSING_CONFIG = {
    "num_clips": 5,  # Default number of clips to generate
    "cleanup_temp": True,  # Clean up temporary files
    "verbose": False  # Verbose output
} 