#!/usr/bin/env python3
"""
Test script for YouTube to Shorts pipeline
"""

import os
import sys
from clips import YouTubeToShortsPipeline

def test_pipeline():
    """Test the pipeline with existing videos"""
    
    # Check if videos exist
    podcast_path = "savedVideos/main_vid.mp4"
    gameplay_path = "gamePlayVid/20 Minutes Minecraft Shader Parkour Gameplay [Free to Use] [Map Download].mp4"
    
    print("🧪 Testing YouTube to Shorts Pipeline")
    print("=" * 50)
    
    # Check files
    if not os.path.exists(podcast_path):
        print(f"❌ Podcast video not found: {podcast_path}")
        return False
    
    if not os.path.exists(gameplay_path):
        print(f"❌ Gameplay video not found: {gameplay_path}")
        return False
    
    print(f"✅ Podcast video found: {podcast_path}")
    print(f"✅ Gameplay video found: {gameplay_path}")
    
    # Initialize pipeline
    try:
        print("\n🔧 Initializing pipeline...")
        pipeline = YouTubeToShortsPipeline()
        print("✅ Pipeline initialized successfully!")
        
        # Test audio extraction
        print("\n🎵 Testing audio extraction...")
        audio_path = pipeline.extract_audio_from_video(podcast_path)
        print(f"✅ Audio extracted to: {audio_path}")
        
        # Test transcription (this will take some time)
        print("\n📝 Testing transcription...")
        print("⚠️  This may take a few minutes for the first run (downloading Whisper model)...")
        transcript_data = pipeline.transcribe_audio(audio_path)
        print("✅ Transcription completed!")
        
        # Test engagement analysis
        print("\n🎯 Testing engagement analysis...")
        segments = pipeline.analyze_engagement(transcript_data, audio_path)
        print(f"✅ Found {len(segments)} engagement segments")
        
        if segments:
            print("\n📊 Top engagement segments:")
            for i, segment in enumerate(segments[:3], 1):
                print(f"  {i}. {segment['start_time']:.1f}s - {segment['end_time']:.1f}s "
                      f"(Score: {segment['engagement_score']:.3f})")
                print(f"     Text: {segment['text'][:100]}...")
        
        # Test video combination (just one clip)
        if segments:
            print("\n🎬 Testing video combination...")
            segment = segments[0]
            combined_path = pipeline.combine_videos(
                podcast_path,
                gameplay_path,
                segment['start_time'],
                segment['end_time']
            )
            print(f"✅ Combined video created: {combined_path}")
            
            # Test subtitle addition
            print("\n💬 Testing subtitle addition...")
            final_path = pipeline.add_subtitles(
                combined_path,
                transcript_data,
                segment['start_time'],
                segment['end_time']
            )
            print(f"✅ Final video with subtitles: {final_path}")
            
            # Clean up test files
            if os.path.exists(combined_path):
                os.remove(combined_path)
                print("🧹 Cleaned up intermediate files")
        
        print("\n🎉 All tests passed! Pipeline is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_pipeline()
    
    if success:
        print("\n🚀 Ready to generate shorts! Run:")
        print("   python3 clips.py")
        print("   or")
        print("   python3 run_pipeline.py --podcast savedVideos/main_vid.mp4 --gameplay 'gamePlayVid/20 Minutes Minecraft Shader Parkour Gameplay [Free to Use] [Map Download].mp4'")
    else:
        print("\n🔧 Please fix the issues above before running the pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    main() 