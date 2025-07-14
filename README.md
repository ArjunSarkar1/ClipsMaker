# YouTube to Shorts Pipeline 🎬

Automatically convert long-form podcast videos into engaging short-form content by combining them with gameplay footage and adding intelligent subtitles.

## 🚀 Features

- **Automatic Engagement Detection**: Uses AI to find the most interesting moments in podcasts
- **Split-Screen Format**: Combines podcast (top) and gameplay (bottom) in 9:16 aspect ratio
- **Intelligent Subtitles**: Automatically generates and styles subtitles from transcript
- **Audio Analysis**: Detects volume spikes, sentiment changes, and speech patterns
- **Text Analysis**: Identifies questions, exclamations, and emotional content
- **Batch Processing**: Generate multiple clips from a single video
- **YouTube Integration**: Download videos directly from YouTube URLs
- **Interactive Mode**: User-friendly prompts for video URLs

## 📋 Requirements

### For Shorts:
- ✅ Background music (.mp3) - *Coming soon*
- ✅ Captions (.srt) - *Automatic generation*
- ✅ Podcast recording video (.mp4) - *From YouTube or local file*
- ✅ Gameplay video (.mp4) - *From YouTube or local file*
- ✅ Length (15-60 seconds) - *Automatic optimization*

### Optional (Publishing):
- Title suggestions
- Description templates
- Thumbnail generation

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd YoutubeToShorts
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (required for video processing):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu**: `sudo apt install ffmpeg`
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

## 🎯 Usage

### Interactive Mode (Recommended for beginners)

Simply run the pipeline and enter YouTube URLs when prompted:

```bash
python3 clips.py
```

Or use the CLI with interactive mode:

```bash
python3 run_pipeline.py --interactive
```

The program will:
1. Ask for podcast YouTube URL
2. Ask for gameplay YouTube URL  
3. Ask how many clips to generate
4. Download videos automatically
5. Process and generate shorts

### Command Line Interface

#### Using YouTube URLs:

```bash
# Download from YouTube URLs
python3 run_pipeline.py --podcast-url "https://youtube.com/watch?v=..." --gameplay-url "https://youtube.com/watch?v=..." --clips 5

# Alternative syntax
python3 run_pipeline.py --podcast-youtube "https://youtube.com/watch?v=..." --gameplay-youtube "https://youtube.com/watch?v=..." --clips 5
```

#### Using Local Files:

```bash
# Use local video files
python3 run_pipeline.py --podcast savedVideos/main_vid.mp4 --gameplay gamePlayVid/gameplay.mp4 --clips 5
```

#### Mixed Mode:

```bash
# Download podcast from YouTube, use local gameplay
python3 run_pipeline.py --podcast-url "https://youtube.com/watch?v=..." --gameplay gamePlayVid/gameplay.mp4 --clips 5
```

**CLI Options**:
- `--podcast-url, -pu`: YouTube URL for podcast video
- `--gameplay-url, -gu`: YouTube URL for gameplay video
- `--podcast, -p`: Path to local podcast video file
- `--gameplay, -g`: Path to local gameplay video file
- `--clips, -n`: Number of clips to generate (default: 5)
- `--output-dir, -o`: Output directory (default: outputs)
- `--verbose, -v`: Enable verbose output
- `--interactive, -i`: Run in interactive mode

### Programmatic Usage

```python
from clips import YouTubeToShortsPipeline

# Initialize pipeline
pipeline = YouTubeToShortsPipeline()

# Download videos from YouTube
podcast_path = pipeline.download_youtube_video(
    "https://youtube.com/watch?v=...",
    "savedVideos",
    "podcast"
)

gameplay_path = pipeline.download_youtube_video(
    "https://youtube.com/watch?v=...",
    "gamePlayVid", 
    "gameplay"
)

# Run complete pipeline
clips = pipeline.process_pipeline(
    podcast_path=podcast_path,
    gameplay_path=gameplay_path,
    num_clips=3
)

print(f"Generated {len(clips)} clips!")
```

## 🔧 Pipeline Steps

### Step 1: Input Videos
- **Podcast Video**: Long-form content (e.g., interviews, discussions) - from YouTube URL or local file
- **Gameplay Video**: Background footage (e.g., Minecraft, Fortnite, Valorant) - from YouTube URL or local file

### Step 2: Engagement Detection
The system analyzes both audio and text to find high-engagement segments:

**Audio Analysis**:
- Volume spikes and changes
- Spectral centroid (brightness)
- Zero crossing rate (speech activity)

**Text Analysis**:
- Sentiment analysis (positive/negative emotions)
- Question detection
- Exclamation detection
- Laughter patterns
- Optimal word count

### Step 3: Video Combination
- Extracts high-engagement segments (15-60 seconds)
- Creates split-screen format (podcast top, gameplay bottom)
- Optimizes for 9:16 aspect ratio (Shorts format)

### Step 4: Subtitle Generation
- Uses OpenAI Whisper for accurate transcription
- Automatically times subtitles to audio
- Styled with white text and black outline
- Positioned at bottom of screen

## 📁 Project Structure

```
YoutubeToShorts/
├── clips.py                 # Main pipeline implementation
├── run_pipeline.py          # CLI interface
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── youtubeDownloader.py   # Video download utilities
├── test_pipeline.py       # Test script
├── savedVideos/           # Downloaded podcast videos
├── gamePlayVid/           # Downloaded gameplay videos
├── outputs/               # Generated short clips
├── transcripts/           # Generated transcripts
├── temp/                  # Temporary files
└── audio_segments/        # Audio processing files
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Video settings**: Resolution, codec, FPS
- **Engagement analysis**: Weights, duration limits
- **Subtitle styling**: Font, size, colors
- **Whisper settings**: Model size, language

## 🎨 Customization

### Adding Custom Engagement Patterns

```python
def _analyze_text_engagement(self, text: str) -> float:
    # Add your custom patterns here
    custom_patterns = ['your_keyword', 'another_pattern']
    # ... existing code ...
```

### Custom Subtitle Styling

```python
def make_subtitle(txt):
    return TextClip(
        txt, 
        font='Your-Font', 
        fontsize=50,
        color='yellow',
        stroke_color='blue',
        stroke_width=3
    ).set_position(('center', 'top'))
```

## 🚨 Troubleshooting

### Common Issues

1. **FFmpeg not found**:
   ```bash
   # Install FFmpeg first
   brew install ffmpeg  # macOS
   sudo apt install ffmpeg  # Ubuntu
   ```

2. **Whisper model download**:
   - First run will download the model (~1GB)
   - Ensure stable internet connection

3. **YouTube download issues**:
   - Check internet connection
   - Verify YouTube URL is valid
   - Some videos may be restricted

4. **Memory issues**:
   - Use smaller Whisper model: Change `"base"` to `"tiny"` in config
   - Process shorter videos first

5. **Video format issues**:
   - Ensure videos are in common formats (MP4, MOV, AVI)
   - Check video codec compatibility

### Performance Tips

- Use SSD storage for faster processing
- Close other applications during processing
- Use smaller Whisper models for faster transcription
- Process videos in smaller batches

## 📝 Example Usage

### Quick Start with YouTube URLs:

1. **Run interactive mode**:
   ```bash
   python3 clips.py
   ```

2. **Enter URLs when prompted**:
   ```
   📻 Enter the YouTube URL for the podcast video: https://youtube.com/watch?v=...
   🎮 Enter the YouTube URL for the gameplay video: https://youtube.com/watch?v=...
   📊 How many clips to generate? (default: 3): 5
   ```

3. **Wait for processing**:
   - Videos will be downloaded automatically
   - Audio will be transcribed
   - Engagement segments will be analyzed
   - Short clips will be generated

### Using CLI with URLs:

```bash
python3 run_pipeline.py \
  --podcast-url "https://youtube.com/watch?v=podcast_video_id" \
  --gameplay-url "https://youtube.com/watch?v=gameplay_video_id" \
  --clips 3 \
  --verbose
```

## 🔮 Future Enhancements

- [ ] Background music integration
- [ ] Advanced subtitle animations
- [ ] YouTube upload automation
- [ ] Thumbnail generation
- [ ] Multiple gameplay video support
- [ ] Web interface
- [ ] Real-time processing
- [ ] Custom engagement patterns
- [ ] Batch processing from playlists

## 📄 License

This project is licensed under the Apache License- see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---
