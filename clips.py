import os
import time
import json
import numpy as np
from typing import List, Tuple, Dict, Optional
import whisper
import librosa
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import speech_recognition as sr
from textblob import TextBlob
import re
from collections import Counter
import logging
from urllib.parse import urlparse, parse_qs
import subprocess
from config import (
    VIDEO_CONFIG, SUBTITLE_CONFIG, 
    ENGAGEMENT_CONFIG, WHISPER_CONFIG, PATHS, PROCESSING_CONFIG
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_youtube_url(url: str) -> str:
    """
    Clean YouTube URL by removing playlist and other parameters
    
    Args:
        url: Raw YouTube URL
        
    Returns:
        Cleaned YouTube URL with only video ID
    """
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Handle youtu.be URLs
        if parsed.netloc == 'youtu.be':
            video_id = parsed.path[1:]  # Remove leading slash
            return f"https://www.youtube.com/watch?v={video_id}"
        
        # Handle youtube.com URLs
        if 'youtube.com' in parsed.netloc:
            query_params = parse_qs(parsed.query)
            
            # Extract video ID
            if 'v' in query_params:
                video_id = query_params['v'][0]
                return f"https://www.youtube.com/watch?v={video_id}"
        
        # If we can't parse it, return the original URL
        return url
        
    except Exception as e:
        logger.warning(f"Could not clean URL {url}: {e}")
        return url

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename on all OSes.
    Replaces or removes problematic characters (quotes, slashes, colons, etc.).
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove or replace unsafe characters
    filename = re.sub(r'[\\/:*?"<>|\n\r\t]', '', filename)
    # Replace curly quotes and em/en dashes with safe equivalents
    filename = filename.replace('“', '"').replace('”', '"')
    filename = filename.replace('‘', "'").replace('’', "'")
    filename = filename.replace('—', '-').replace('–', '-')
    # Remove any remaining non-printable or non-ASCII characters
    filename = re.sub(r'[^\x20-\x7E]', '', filename)
    # Optionally, limit length
    return filename[:80]

class YouTubeToShortsPipeline:
    def __init__(self, project_root: str = "."):
        """
        Initialize the YouTube to Shorts pipeline
        
        Args:
            project_root: Root directory for the project
        """
        self.project_root = project_root
        self.setup_directories()
        self.model = whisper.load_model("base")  # Load Whisper model
        
    def setup_directories(self):
        """Create necessary directories for the project"""
        directories = [
            "inputs",
            "outputs", 
            "transcripts",
            "temp",
            "audio_segments",
            "savedVideos",
            "gamePlayVid"
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.project_root, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"Created directory: {dir_path}")
    
    def download_youtube_video(self, url: str, save_path: str, video_type: str = "video") -> str:
        """
        Download video from YouTube URL using yt-dlp
        """
        try:
            cleaned_url = clean_youtube_url(url)
            print(f"\n📥 Downloading {video_type} from YouTube...")
            print(f"Original URL: {url}")
            print(f"Cleaned URL: {cleaned_url}")
            start_time = time.time()

            # Ensure save_path exists
            os.makedirs(save_path, exist_ok=True)

            # Use yt-dlp to get video title (for filename)
            try:
                result = subprocess.run([
                    "yt-dlp", "--get-title", cleaned_url
                ], capture_output=True, text=True, check=True)
                title = result.stdout.strip()
                title = sanitize_filename(title)
                if not title:
                    title = f"{video_type}_video"
            except Exception as e:
                print(f"⚠️  Could not fetch video title: {e}")
                title = f"{video_type}_video"

            filename = f"{video_type}_{title}.mp4"
            filepath = os.path.join(save_path, filename)

            # Download the best quality video+audio as MP4
            try:
                print(f"Downloading to: {filepath}")
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "-o", filepath,
                    cleaned_url
                ]
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"❌ Error during download: {e}")
                raise

            end_time = time.time()
            elapsed_time = round((end_time - start_time), 2)
            print(f"✅ Downloaded in {elapsed_time} seconds")
            print(f"📁 Saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            print("💡 Troubleshooting tips:")
            print("   - Check if the video is available in your region")
            print("   - Try a different video")
            print("   - Make sure the URL is correct")
            print("   - Some videos may be restricted")
            raise
    
    def get_time_format(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format"""
        if seconds is None:
            return "Unknown"
        remMin, remSec = divmod(int(seconds), 60)
        hours, minutes = divmod(remMin, 60)
        return "{:02}:{:02}:{:02}".format(hours, minutes, remSec)
    
    def extract_audio_from_video(self, video_path: str, output_path: str = None) -> str:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to the video file
            output_path: Path to save the audio file (optional)
            
        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            output_path = os.path.join(
                self.project_root, 
                "temp", 
                f"audio_{os.path.basename(video_path)}.wav"
            )
        
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_path, verbose=False, logger=None)
            video.close()
            audio.close()
            logger.info(f"Audio extracted to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription data
        """
        try:
            logger.info("Starting transcription...")
            result = self.model.transcribe(audio_path)
            
            # Save transcript
            transcript_path = os.path.join(
                self.project_root,
                "transcripts", 
                f"transcript_{os.path.basename(audio_path)}.json"
            )
            
            with open(transcript_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Transcription saved to: {transcript_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def analyze_engagement(self, transcript_data: Dict, audio_path: str) -> List[Dict]:
        """
        Analyze transcript and audio for high-engagement segments
        
        Args:
            transcript_data: Whisper transcription result
            audio_path: Path to the audio file
            
        Returns:
            List of high-engagement segments with timestamps
        """
        segments = []
        
        # Load audio for analysis
        y, sr = librosa.load(audio_path)
        
        # Get all segments from transcript
        whisper_segments = transcript_data.get('segments', [])
        logger.info(f"Found {len(whisper_segments)} Whisper segments")
        
        if not whisper_segments:
            logger.warning("No segments found in transcript")
            return []
        
        # Calculate average segment duration
        avg_duration = sum(seg['end'] - seg['start'] for seg in whisper_segments) / len(whisper_segments)
        logger.info(f"Average segment duration: {avg_duration:.2f} seconds")
        
        # Strategy 1: Combine consecutive segments to create longer clips
        combined_segments = self._combine_segments(whisper_segments, target_duration=30)
        logger.info(f"Created {len(combined_segments)} combined segments")
        
        # Strategy 2: Use individual segments if they're long enough
        long_segments = [seg for seg in whisper_segments if (seg['end'] - seg['start']) >= 10]
        logger.info(f"Found {len(long_segments)} segments >= 10 seconds")
        
        # Combine both strategies
        all_candidates = combined_segments + long_segments
        
        # Analyze each candidate segment
        for i, segment in enumerate(all_candidates):
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text'].strip()
            duration = end_time - start_time
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                text, y, sr, start_time, end_time
            )
            
            segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'text': text,
                'engagement_score': engagement_score,
                'duration': duration,
                'source': segment.get('source', 'unknown')
            })
        
        # Sort by engagement score
        segments.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Filter segments that are suitable for shorts (10-60 seconds)
        suitable_segments = [
            seg for seg in segments 
            if 10 <= seg['duration'] <= 60
        ]
        
        logger.info(f"Found {len(suitable_segments)} suitable segments for shorts")
        
        # Log top segments for debugging
        if suitable_segments:
            logger.info("Top 5 engagement segments:")
            for i, seg in enumerate(suitable_segments[:5]):
                logger.info(f"  {i+1}. {seg['start_time']:.1f}s - {seg['end_time']:.1f}s "
                          f"(Score: {seg['engagement_score']:.3f}, Duration: {seg['duration']:.1f}s)")
                logger.info(f"     Text: {seg['text'][:100]}...")
        
        return suitable_segments[:10]  # Return top 10 segments
    
    def _combine_segments(self, segments: List[Dict], target_duration: float = 30) -> List[Dict]:
        """
        Combine consecutive segments to create longer clips
        
        Args:
            segments: List of Whisper segments
            target_duration: Target duration for combined segments
            
        Returns:
            List of combined segments
        """
        combined = []
        current_segments = []
        current_start = None
        current_text = ""
        
        for segment in segments:
            if current_start is None:
                current_start = segment['start']
            
            current_segments.append(segment)
            current_text += " " + segment['text'].strip()
            
            current_duration = segment['end'] - current_start
            
            # If we've reached target duration or this is the last segment
            if current_duration >= target_duration or segment == segments[-1]:
                if current_duration >= 10:  # Minimum 10 seconds
                    combined.append({
                        'start': current_start,
                        'end': segment['end'],
                        'text': current_text.strip(),
                        'source': 'combined'
                    })
                
                # Reset for next combination
                current_segments = []
                current_start = None
                current_text = ""
        
        return combined
    
    def _calculate_engagement_score(self, text: str, audio: np.ndarray, 
                                  sample_rate: int, start_time: float, 
                                  end_time: float) -> float:
        """
        Calculate engagement score for a segment
        
        Args:
            text: Text content of the segment
            audio: Audio data
            sample_rate: Audio sample rate
            start_time: Start time of segment
            end_time: End time of segment
            
        Returns:
            Engagement score (0-1)
        """
        score = 0.0
        
        # Text-based analysis
        text_score = self._analyze_text_engagement(text)
        score += text_score * 0.4  # 40% weight for text
        
        # Audio-based analysis
        audio_score = self._analyze_audio_engagement(
            audio, sample_rate, start_time, end_time
        )
        score += audio_score * 0.6  # 60% weight for audio
        
        return min(score, 1.0)
    
    def _analyze_text_engagement(self, text: str) -> float:
        """
        Analyze text for engagement indicators
        
        Args:
            text: Text to analyze
            
        Returns:
            Text engagement score (0-1)
        """
        if not text:
            return 0.0
        
        score = 0.0
        
        # Sentiment analysis
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        score += abs(sentiment) * 0.3  # Higher sentiment (positive or negative) = more engaging
        
        # Question detection
        questions = len(re.findall(r'\?', text))
        score += min(questions * 0.2, 0.3)  # Questions are engaging
        
        # Exclamation detection
        exclamations = len(re.findall(r'!', text))
        score += min(exclamations * 0.15, 0.2)  # Exclamations show excitement
        
        # Laughter detection
        laughter_patterns = ['haha', 'lol', 'lmao', '😂', '😄', '😆']
        laughter_count = sum(text.lower().count(pattern) for pattern in laughter_patterns)
        score += min(laughter_count * 0.1, 0.2)
        
        # Length bonus (not too short, not too long)
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            score += 0.1
        
        return min(score, 1.0)
    
    def _analyze_audio_engagement(self, audio: np.ndarray, sample_rate: int,
                                start_time: float, end_time: float) -> float:
        """
        Analyze audio for engagement indicators
        
        Args:
            audio: Audio data
            sample_rate: Audio sample rate
            start_time: Start time of segment
            end_time: End time of segment
            
        Returns:
            Audio engagement score (0-1)
        """
        # Extract segment audio
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        segment_audio = audio[start_sample:end_sample]
        
        if len(segment_audio) == 0:
            return 0.0
        
        score = 0.0
        
        # Volume analysis
        rms = np.sqrt(np.mean(segment_audio**2))
        score += min(rms * 10, 0.4)  # Higher volume = more engaging
        
        # Spectral centroid (brightness)
        spectral_centroids = librosa.feature.spectral_centroid(
            y=segment_audio, sr=sample_rate
        )[0]
        avg_centroid = np.mean(spectral_centroids)
        score += min(avg_centroid / 5000, 0.3)  # Brighter sounds = more engaging
        
        # Zero crossing rate (speech activity)
        zcr = librosa.feature.zero_crossing_rate(segment_audio)[0]
        avg_zcr = np.mean(zcr)
        score += min(avg_zcr * 2, 0.3)  # Higher ZCR = more speech activity
        
        return min(score, 1.0)
    
    def combine_videos(self, podcast_path: str, gameplay_path: str, 
                      start_time: float, end_time: float, 
                      output_path: str = None) -> str:
        """
        Combine podcast and gameplay videos into a split-screen format with zoomed content
        
        Args:
            podcast_path: Path to podcast video
            gameplay_path: Path to gameplay video
            start_time: Start time for the clip
            end_time: End time for the clip
            output_path: Output path for combined video
            
        Returns:
            Path to the combined video
        """
        if output_path is None:
            output_path = os.path.join(
                self.project_root,
                "outputs",
                f"combined_clip_{start_time}_{end_time}.mp4"
            )
        
        try:
            podcast_clip = VideoFileClip(podcast_path).subclip(start_time, end_time)
            gameplay_clip = VideoFileClip(gameplay_path).subclip(start_time, end_time)
            target_width = VIDEO_CONFIG['target_width']
            target_height = VIDEO_CONFIG['target_height']
            zoom_factor = VIDEO_CONFIG['zoom_factor']
            # Resize and zoom podcast clip (top half)
            podcast_resized = podcast_clip.resize(height=target_height//2).resize(width=target_width)
            podcast_zoomed = podcast_resized.resize(zoom_factor)
            podcast_final = podcast_zoomed.set_position(('center', 0))
            # Resize and zoom gameplay clip (bottom half), mute audio
            gameplay_resized = gameplay_clip.resize(height=target_height//2).resize(width=target_width)
            gameplay_zoomed = gameplay_resized.resize(zoom_factor)
            gameplay_final = gameplay_zoomed.set_position(('center', target_height//2)).without_audio()
            # Use podcast audio only
            final_clip = CompositeVideoClip([
                podcast_final,
                gameplay_final
            ], size=(target_width, target_height)).set_audio(podcast_clip.audio)
            final_clip.write_videofile(
                output_path,
                codec=VIDEO_CONFIG['codec'],
                audio_codec=VIDEO_CONFIG['audio_codec'],
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            podcast_clip.close()
            gameplay_clip.close()
            final_clip.close()
            logger.info(f"Combined video saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error combining videos: {e}")
            raise
    
    def add_subtitles(self, video_path: str, transcript_data: Dict,
                     start_time: float, end_time: float,
                     output_path: str = None) -> str:
        """
        Add styled subtitles to video with highlighting effects
        
        Args:
            video_path: Path to input video
            transcript_data: Whisper transcription data
            start_time: Start time of the clip
            end_time: End time of the clip
            output_path: Output path for video with subtitles
            
        Returns:
            Path to video with subtitles
        """
        if output_path is None:
            output_path = os.path.join(
                self.project_root,
                "outputs",
                f"final_clip_{start_time}_{end_time}.mp4"
            )
        
        try:
            # Extract relevant subtitles for the time range
            subtitles = []
            for segment in transcript_data.get('segments', []):
                if (segment['start'] >= start_time and segment['end'] <= end_time):
                    adjusted_start = segment['start'] - start_time
                    adjusted_end = segment['end'] - start_time
                    subtitles.append((
                        (adjusted_start, adjusted_end),
                        segment['text'].strip()
                    ))
            # --- Progressive word-by-word chunking ---
            def chunk_text(text, n=3):
                words = text.split()
                return [' '.join(words[i:i+n]) for i in range(0, len(words), n)]
            chunked_subtitles = []
            for (seg_start, seg_end), text in subtitles:
                chunks = chunk_text(text, n=3)
                seg_duration = seg_end - seg_start
                chunk_duration = seg_duration / max(len(chunks), 1)
                for idx, chunk in enumerate(chunks):
                    chunk_start = seg_start + idx * chunk_duration
                    chunk_end = chunk_start + chunk_duration
                    chunked_subtitles.append(((chunk_start, chunk_end), chunk))
            # --- Subtitle rendering ---
            def make_subtitle(txt):
                try:
                    return TextClip(
                        txt,
                        font='Arial-Bold',
                        fontsize=SUBTITLE_CONFIG['font_size'],
                        color='white',
                        stroke_color='white',
                        stroke_width=SUBTITLE_CONFIG['stroke_width'],
                        method='caption',
                        size=(SUBTITLE_CONFIG['max_width'], None),
                        align='center'
                    ).set_position(('center', 'center')).margin(bottom=SUBTITLE_CONFIG['margin_bottom'])
                except Exception as e:
                    logger.warning(f"ImageMagick text rendering failed: {e}")
                    try:
                        return TextClip(
                            txt,
                            fontsize=SUBTITLE_CONFIG['font_size'],
                            color='white',
                            method='caption',
                            size=(SUBTITLE_CONFIG['max_width'], None),
                            align='center'
                        ).set_position(('center', 'center')).margin(bottom=SUBTITLE_CONFIG['margin_bottom'])
                    except Exception as e2:
                        logger.error(f"Text rendering completely failed: {e2}")
                        from moviepy.video.VideoClip import ColorClip
                        return ColorClip(size=(1, 1), color=(0, 0, 0)).set_duration(0.1)
            subtitle_clips = []
            fade_duration = SUBTITLE_CONFIG['fade_duration']
            highlight_enabled = SUBTITLE_CONFIG['highlight_effect']
            for (start, end), text in chunked_subtitles:
                subtitle_clip = make_subtitle(text)
                subtitle_with_fade = subtitle_clip.set_start(start).set_end(end)
                if highlight_enabled and end - start > 2 * fade_duration:
                    subtitle_with_fade = subtitle_with_fade.fadein(fade_duration).fadeout(fade_duration)
                subtitle_clips.append(subtitle_with_fade)
            video = VideoFileClip(video_path)
            final_video = CompositeVideoClip([video] + subtitle_clips)
            final_video.write_videofile(
                output_path,
                codec=VIDEO_CONFIG['codec'],
                audio_codec=VIDEO_CONFIG['audio_codec'],
                verbose=False,
                logger=None
            )
            video.close()
            final_video.close()
            logger.info(f"Video with subtitles saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            logger.info("Returning video without subtitles due to error")
            return video_path
    
    def process_pipeline(self, podcast_path: str, gameplay_path: str,
                        num_clips: int = 5) -> List[str]:
        """
        Run the complete pipeline
        
        Args:
            podcast_path: Path to podcast video
            gameplay_path: Path to gameplay video
            num_clips: Number of clips to generate
            
        Returns:
            List of paths to generated short videos
        """
        logger.info("Starting YouTube to Shorts pipeline...")
        
        # Step 1: Extract audio from podcast
        logger.info("Step 1: Extracting audio from podcast...")
        audio_path = self.extract_audio_from_video(podcast_path)
        
        # Step 2: Transcribe audio
        logger.info("Step 2: Transcribing audio...")
        transcript_data = self.transcribe_audio(audio_path)
        
        # Step 3: Analyze engagement
        logger.info("Step 3: Analyzing engagement...")
        engagement_segments = self.analyze_engagement(transcript_data, audio_path)
        
        if not engagement_segments:
            print("⚠️  No suitable engagement segments found. Try with a longer video or different content.")
            return []
        
        # Step 4: Generate clips
        logger.info("Step 4: Generating clips...")
        generated_clips = []
        
        for i, segment in enumerate(engagement_segments[:num_clips]):
            logger.info(f"Processing clip {i+1}/{min(num_clips, len(engagement_segments))}")
            
            # Combine videos
            combined_path = self.combine_videos(
                podcast_path,
                gameplay_path,
                segment['start_time'],
                segment['end_time']
            )
            
            # Add subtitles
            final_path = self.add_subtitles(
                combined_path,
                transcript_data,
                segment['start_time'],
                segment['end_time']
            )
            
            generated_clips.append(final_path)
            
            # Clean up intermediate file
            if os.path.exists(combined_path):
                os.remove(combined_path)
        
        logger.info(f"Pipeline completed! Generated {len(generated_clips)} clips.")
        return generated_clips

def get_user_input():
    """Get video URLs from user input"""
    print("🎬 YouTube to Shorts Pipeline")
    print("=" * 50)
    
    # Get podcast URL
    while True:
        podcast_url = input("\n📻 Enter the YouTube URL for the podcast video: ").strip()
        if podcast_url:
            if "youtube.com" in podcast_url or "youtu.be" in podcast_url:
                break
            else:
                print("❌ Please enter a valid YouTube URL")
        else:
            print("❌ URL cannot be empty")
    
    # Get gameplay URL
    while True:
        gameplay_url = input("🎮 Enter the YouTube URL for the gameplay video: ").strip()
        if gameplay_url:
            if "youtube.com" in gameplay_url or "youtu.be" in gameplay_url:
                break
            else:
                print("❌ Please enter a valid YouTube URL")
        else:
            print("❌ URL cannot be empty")
    
    # Get number of clips
    while True:
        try:
            num_clips = input("📊 How many clips to generate? (default: 3): ").strip()
            if not num_clips:
                num_clips = 3
            else:
                num_clips = int(num_clips)
                if 1 <= num_clips <= 10:
                    break
                else:
                    print("❌ Please enter a number between 1 and 10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return podcast_url, gameplay_url, num_clips

def main():
    """Main function to run the pipeline with user input"""
    try:
        # Get user input
        podcast_url, gameplay_url, num_clips = get_user_input()
        
        # Initialize pipeline
        pipeline = YouTubeToShortsPipeline()
        
        # Download videos
        print(f"\n📥 Downloading videos...")
        podcast_path = pipeline.download_youtube_video(
            podcast_url, 
            os.path.join(pipeline.project_root, "savedVideos"),
            "podcast"
        )
        
        gameplay_path = pipeline.download_youtube_video(
            gameplay_url,
            os.path.join(pipeline.project_root, "gamePlayVid"),
            "gameplay"
        )
        
        # Run pipeline
        print(f"\n🚀 Starting pipeline...")
        generated_clips = pipeline.process_pipeline(
            podcast_path, 
            gameplay_path, 
            num_clips=num_clips
        )
        
        if generated_clips:
            print(f"\n✅ Successfully generated {len(generated_clips)} short videos!")
            print("\nGenerated clips:")
            for i, clip_path in enumerate(generated_clips, 1):
                print(f"  {i}. {clip_path}")
        else:
            print("\n⚠️  No clips were generated. Try with different videos or check the logs.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
