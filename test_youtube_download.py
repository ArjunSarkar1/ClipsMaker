#!/usr/bin/env python3
"""
Test YouTube downloading functionality
"""

import os
from clips import YouTubeToShortsPipeline, clean_youtube_url

def test_youtube_download():
    """Test YouTube video downloading"""
    
    # Test URL cleaning
    test_url = "https://www.youtube.com/watch?v=ru44DngJYoA&list=PL-Woi1-PlvaLMXaictKoiRv6PYUOIy4Xm&index=17"
    cleaned_url = clean_youtube_url(test_url)
    print(f"Original URL: {test_url}")
    print(f"Cleaned URL: {cleaned_url}")
    
    # Test with a known working short video (Big Buck Bunny - public domain)
    test_video_url = "https://www.youtube.com/watch?v=YE7VzlLtp-4"  # Big Buck Bunny trailer
    
    try:
        print(f"\n🧪 Testing YouTube download with: {test_video_url}")
        
        # Initialize pipeline
        pipeline = YouTubeToShortsPipeline()
        
        # Test download
        downloaded_path = pipeline.download_youtube_video(
            test_video_url,
            os.path.join(pipeline.project_root, "temp"),
            "test"
        )
        
        if os.path.exists(downloaded_path):
            print(f"✅ Download successful! File: {downloaded_path}")
            print(f"📁 File size: {os.path.getsize(downloaded_path)} bytes")
            
            # Clean up test file
            os.remove(downloaded_path)
            print("🧹 Test file cleaned up")
            
            return True
        else:
            print("❌ Download failed - file not found")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing YouTube Download Functionality")
    print("=" * 50)
    
    success = test_youtube_download()
    
    if success:
        print("\n✅ YouTube download functionality is working!")
        print("🚀 You can now use the pipeline with YouTube URLs")
    else:
        print("\n❌ YouTube download functionality has issues")
        print("💡 Check your internet connection and try again") 