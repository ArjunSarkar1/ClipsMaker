## Session #1 (1hr)
- test downloading youtube videos through pytubefix
- Testing FFMPEG
    - ffmpeg -ss 00:05:00 -to 00:08:00 -i testVid.mp4 -c copy testVidCropped.mp4 (this creates a segment of a video into a 3min clip)
- Will be using the LR-ASD repo for active speaker detection
- looked into speech detection libs
    - https://arxiv.org/pdf/2303.00747 (WhisperX - https://github.com/m-bain/whisperx)
- Will be setting up modal in the next session

## Session #2 (30min)
- Alright, so far, I updated the main.py to create teh infra for the and building the post api endpoint. I used a Cuda enabled docker image (which mean GPU support), installed necessary libs from requirements.txt, fonts, commands and mounted my local lr-asd model. I included a Bearer token authorization to prevent random people from hitting my GPU endpoint. The goal is to makes a video reference (s3_key), authenticate the request with a Bearer token, run it on a GPU machine and will eventually process videos (clip, captions, etc.)
- Infra almost done but we need work on the AI logic next