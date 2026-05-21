from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import head
import modal
from fastapi import Depends
from pydantic import BaseModel

# setting up Modal

APT_PACKAGES = ["ffmpeg", "libgli-mesa-glx", "wget", "libcudnn8", "libcudnn8-dev"]
SETUP_CMD = [
    "mkdir -p /usr/share/fonts/truetype/custom",
    "wget -q -O /usr/share/fonts/truetype/custom/DM_Sans_Regular.ttf https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans-Regular.ttf",
    "wget -q -O /usr/share/fonts/truetype/custom/DM_Sans_Bold.ttf https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans-Bold.ttf",
    "fc-cache -f -v",
]

# this is the docker image for our modal function
# basic docker image that will be used to create the environement
# that our endpoint will run from within
image = (
    modal.Image.from_registry("nvidia/cuda:12.04-devel-ubuntu22.04", add_python="3.12")
    .apt_install(APT_PACKAGES)
    .pip_install_from_requirements("requirements.txt")
    .run_commands(SETUP_CMD)
    .add_local_dir("LR-ASD", "/LR-ASD", copy=True)
)

app = modal.App("AI ClipMaker", image=image)

volume = modal.Volume.from_name("ai-clipmaker-data", create_if_missing=True)

mount_path = "/root/.cache/torch"

auth_scheme = HTTPBearer()# 


class VideoRequest(BaseModel):
    s3_key : str
    


# this is the function that will be called when the endpoint is hit
@app.function(
    secrets=[modal.Secret.from_name("ai-clipmaker")],
    gpu="L40S",
    timeout=1000,
    retries=0,
    scaledown_window=20,
    volumes={mount_path: volume},
)
class ClipMaker:
    @modal.enter()
    def loadModels(self):
        # os.env("AUTH_TOKEN") we can store the secret keys in the modal instead of storing secrets locally
        print("Loading models...")
        pass
    
    @modal.fastapi_endpoint(method="POST")
    def video_processor(self, request: VideoRequest, token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
        print("Processing video..." + request.s3_key)
        pass
    
    
# lets test it out
@app.local_entrypoint()
def mainFunc():
    print("Testing the endpoint...")
    # we can use the requests library to test the endpoint
    import requests
    
    ai_clipmaker = ClipMaker()
    
    url = ai_clipmaker.video_processor.url
    payload = {
        "s3_key": "testing#1/test1.mp4"
    }

    headers = {
        "content-type": "application/json",
        "authorization": "Bearer " + "111111" ## REMEMBER to replace with AUTH_TOKEN from modal secrets
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    print(result)