# Report #1

Our current implementation contains high coupling and low cohesion such as `clips.py`. This makes it hard to test, swap components or scale any individual part without breaking the others.

I want to scale and improve our current implementation so the following approach will be used.

## New Implementation

The basic flow of would be in the following key steps:

**1.** User uploads a long form content

**2.** The input video gets put into a queue (Videos will be stored in Amazon Simple Storage Service S3 bucket)

**3.** Backend Process

**3.1** Downloads the long form video

**3.2** Creates the clips from long form video and saved in the same S3 bucket

**4** Frontend process

**4.1** Finds clips and presents them to user

Note: we will use a S3 key to uniquely identify and retrieve videos inside S3.

To further explain the backend structure:

We will authenticate the request with a bearer token, download the input video from S3 and each folder will contain all associated files/videos/clips identified by a unique id.

Next, we will transcribe the video by extracting the audio from video with FFMPEG, then use WhisperX which is built on top of OpenAI's Whisper (great for long videos) and we will get a list of words with their associated timestamps.

Now, we need to focus on finding viral moments in the video, I am still open to options like Llama 3.0, Google Gemini 2.5 with emphasis on scoring (hook, emotional intensity, value/insight, clarity, shareability). Then, we parse llm output as JSON with reasoning behind why it was scored that way.

Then, once our viral moments have been found, we can start creating clips by looping through identified moments.
We do this by extracting the timestamps (start, end from llm) then we will use an active speaker detection tool to identify people who are speaking for each frame of the video (more to discuss). We will mostly focus on vertical videos. Additionally, manipulating the aspect ratio of a normal Youtube video from horizontal to vertical. Hence, cropping the coordinates to ensure this. We will most likely use an open source tool for this (to save time). Then, after the video creation is done, we will add subtitles (optimally showing x words at a time on the screen) and freestyle them (customizations).

Video Transcribe

- https://github.com/a2nath/Video-Transcribe

Automatic Speech Recognition

- https://github.com/openai/whisper
- https://github.com/m-bain/whisperx
- https://github.com/SYSTRAN/faster-whisper
