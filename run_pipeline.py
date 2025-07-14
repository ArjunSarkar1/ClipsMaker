#!/usr/bin/env python3
"""
Command-line interface for YouTube to Shorts pipeline
"""

import argparse
import os
import sys
from clips import YouTubeToShortsPipeline
from config import PROCESSING_CONFIG

def main():
    parser = argparse.ArgumentParser(
        description="YouTube to Shorts Pipeline - Convert long videos to engaging short clips"
    )
    
    # Input options - either URLs or file paths
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--podcast-url", "-pu",
        type=str,
        help="YouTube URL for podcast video"
    )
    input_group.add_argument(
        "--podcast", "-p",
        type=str,
        help="Path to podcast video file"
    )
    
    input_group.add_argument(
        "--gameplay-url", "-gu",
        type=str,
        help="YouTube URL for gameplay video"
    )
    input_group.add_argument(
        "--gameplay", "-g", 
        type=str,
        help="Path to gameplay video file"
    )
    
    # Combined URL option
    parser.add_argument(
        "--podcast-youtube", "-py",
        type=str,
        help="YouTube URL for podcast video (alternative to --podcast-url)"
    )
    parser.add_argument(
        "--gameplay-youtube", "-gy",
        type=str,
        help="YouTube URL for gameplay video (alternative to --gameplay-url)"
    )
    
    # Other options
    parser.add_argument(
        "--clips", "-n",
        type=int,
        default=PROCESSING_CONFIG["num_clips"],
        help=f"Number of clips to generate (default: {PROCESSING_CONFIG['num_clips']})"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="outputs",
        help="Output directory for generated clips (default: outputs)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (prompt for URLs)"
    )
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        from clips import get_user_input
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
        
        return
    
    # Determine podcast and gameplay sources
    podcast_source = args.podcast_url or args.podcast_youtube or args.podcast
    gameplay_source = args.gameplay_url or args.gameplay_youtube or args.gameplay
    
    if not podcast_source or not gameplay_source:
        print("❌ Error: You must provide both podcast and gameplay sources")
        print("Use --help for usage information")
        sys.exit(1)
    
    # Initialize pipeline
    pipeline = YouTubeToShortsPipeline()
    
    # Set output directory
    if args.output_dir != "outputs":
        pipeline.project_root = args.output_dir
        pipeline.setup_directories()
    
    print("🎬 YouTube to Shorts Pipeline")
    print("=" * 40)
    
    # Handle podcast source
    if args.podcast_url or args.podcast_youtube:
        podcast_url = args.podcast_url or args.podcast_youtube
        print(f"Podcast URL: {podcast_url}")
        try:
            podcast_path = pipeline.download_youtube_video(
                podcast_url,
                os.path.join(pipeline.project_root, "savedVideos"),
                "podcast"
            )
        except Exception as e:
            print(f"❌ Error downloading podcast: {e}")
            sys.exit(1)
    else:
        podcast_path = args.podcast
        if not os.path.exists(podcast_path):
            print(f"❌ Error: Podcast video not found: {podcast_path}")
            sys.exit(1)
        print(f"Podcast file: {podcast_path}")
    
    # Handle gameplay source
    if args.gameplay_url or args.gameplay_youtube:
        gameplay_url = args.gameplay_url or args.gameplay_youtube
        print(f"Gameplay URL: {gameplay_url}")
        try:
            gameplay_path = pipeline.download_youtube_video(
                gameplay_url,
                os.path.join(pipeline.project_root, "gamePlayVid"),
                "gameplay"
            )
        except Exception as e:
            print(f"❌ Error downloading gameplay: {e}")
            sys.exit(1)
    else:
        gameplay_path = args.gameplay
        if not os.path.exists(gameplay_path):
            print(f"❌ Error: Gameplay video not found: {gameplay_path}")
            sys.exit(1)
        print(f"Gameplay file: {gameplay_path}")
    
    print(f"Clips to generate: {args.clips}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 40)
    
    try:
        # Run pipeline
        generated_clips = pipeline.process_pipeline(
            podcast_path,
            gameplay_path,
            num_clips=args.clips
        )
        
        if generated_clips:
            print(f"\n✅ Successfully generated {len(generated_clips)} short videos!")
            print("\nGenerated clips:")
            for i, clip_path in enumerate(generated_clips, 1):
                print(f"  {i}. {clip_path}")
                
            print(f"\n📁 All clips saved to: {args.output_dir}")
        else:
            print("\n⚠️  No clips were generated. Try with different videos or check the logs.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 