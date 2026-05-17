import modal

# setting up Modal

# this is the docker image for our modal function
image = (modal.Image.from_registry("nvidia/cuda:12.04-devel-ubuntu22.04", add_python="3.12").apt_install(["ffmpeg","libgli-mesa-glx", "wget", "libcudnn8", "libcudnn8-dev"]).pip_install_from_requirements("requirements.txt").run_commands([""]))

         