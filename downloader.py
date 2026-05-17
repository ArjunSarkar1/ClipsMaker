from pytubefix import YouTube
from pytubefix.cli import on_progress

# expecting long duration videos but just testing short ones for now
input_url = "https://www.youtube.com/watch?v=WfrSlZ_i5Bc"

y = YouTube(input_url, on_progress_callback=on_progress)
print(f"Title: {y.title}")
print(f"Author: {y.author}")

ys = y.streams.get_highest_resolution()
ys.download()
