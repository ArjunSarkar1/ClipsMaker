import os
import time
# from pytube import YouTube
import sys
import moviepy
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

def downloadVideo(vid_url, save_path):
    try:
        start_time = time.time()
        yt = YouTube(vid_url)

        print("[ Video Details ]")
        print("Title:", yt.title)
        print("Author:", yt.author)
        print("Views:", yt.views)
        print("Video Length:", getTimeFormat(yt.length))

        you = yt.streams.get_highest_resolution()
        you.download(save_path)

        end_time = time.time()
        elapsed_time = round((end_time - start_time), 2)
        print("\n[ Video downloaded in {:.2f} seconds ]\n".format(elapsed_time))

    except Exception as e:
        print("An error occurred:", str(e))

def downloadAudio(vid_url, save_path):
    start_time = time.time()
    yt = YouTube(vid_url)
    audio = yt.streams.filter(only_audio=True).first()
    audio.download(save_path)
    end_time = time.time()
    elapsed_time = int(end_time - start_time)
    print("\n[ Audio downloaded in {:.2f} seconds ]\n".format(elapsed_time))

def getTimeFormat(seconds):
    remMin, remSec = divmod(int(seconds), 60)
    hours, minutes = divmod(remMin, 60)
    return "{:02}:{:02}:{:02}".format(hours, minutes, remSec) #good to know!

    # hrStr = ""
    # minStr = ""
    # secStr = ""
    # if len(str(hours)) == 1:
    #     hrStr += "0"+str(hours)
    # else:
    #     hrStr += str(hours)
    # if len(str(minutes)) == 1:
    #     minStr += "0"+str(minutes)
    # else:
    #     minStr += str(minutes)
    # if len(str(remSec)) == 1:
    #     secStr += "0"+str(remSec)
    # else:
    #     secStr += str(remSec)
    
    # return f"{hrStr}:{minStr}:{secStr}"

def main():
    # https://www.youtube.com/watch?v=vEQ8CXFWLZU
    # https://www.youtube.com/watch?v=6jQx2ge4NQg
    url = input("Enter the YouTube URL: ")
    main_vid_path = os.path.join(os.getcwd(), "savedVideos")
    game_vid_path = os.path.join(os.getcwd(), "gamePlayVid")

    # downloadVideo(url, main_vid_path)
    # downloadVideo(url, game_vid_path)
    # audio
    
    # u = "https://www.youtube.com/watch?v=HV1CMDhemt0"
    # downloadAudio(u, os.path.join(os.getcwd(), "savedAudios"))


def split_main_video(input_video, output_path, start_time, end_time):
    video = VideoFileClip(input_video).subclip(start_time, end_time)
    video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    video.close()

if not os.path.exists("outputFolder"):
    os.makedirs("outputFolder")

# Replace these with your actual start and end times from the heatmap data
start_time_1, end_time_1 = 0, 60  # seconds
start_time_2, end_time_2 = 60, 120  # seconds

# Specify the input video file
input_video_path = "savedVideos/main_vid.mp4"

# Split the video into chunks
output_file_1 = os.path.join("outputFolder", 'chunk_1.mp4')
output_file_2 = os.path.join("outputFolder", 'chunk_2.mp4')

split_main_video(input_video_path, output_file_1, start_time_1, end_time_1)
split_main_video(input_video_path, output_file_2, start_time_2, end_time_2)