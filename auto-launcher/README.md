# Using docker
## Pre-requisites
### Docker volume to save build files
You need to create a docker volumne for containing build outputs. To do so, the most straightfoward commant is:
`sudo docker volume create build-vol`.
You can see where the volume is stored by using:
`sudo docker volume inspect build-vol`
### Adding the nvidia-container-runtime
You can download the runtime by:
`sudo apt install nvidia-container-runtime`

You then need to modify your docker startup override configuration file. This can be either a json file, but on systemd machines, this will be another file (`/etc/systemd/system/docker.service.d/override.conf`). You need to add this value to ExecStart:
--add-runtime=nvidia=/usr/bin/nvidia-container-runtime

### How the override.conf file should look like
Here is an example of a valid .conf file:
```[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H unix:// -H tcp://127.0.0.1:2375 --containerd=/run/containerd/containerd.sock --bridge="bridge0" -s overlay --data-root="/media/emilio/86d1fadd-4a40-4ce5-96b4-a56f81b8df62" --add-runtime=nvidia=/usr/bin/nvidia-container-runtime
```
**Note that if you change this file, you will need to tell docker service that the file has changed AND to restart the service (it seems only restarting the service doesn't take into account the changes). You can thus run:
`sudo systemctl daemon-reload && sudo systemctl restart docker`
**
### Extra options
#### External device as docker storage
`--data-root` points to a mounted external storage device since the docker working directory is usually in the same file-system. Since building docker images can result in a large disk usage, we point to another directory. If using this, we also need to use `-s overlay` to say we want to use the storage driver named _overlay_. 
#### User defined network bridge for docker containers
`--bridge=bridge0` is telling docker to use a bridge device named `bridge0` on which docker containers will use. This is most of the time not needed (although they say for production use it should be used and carefully considered), if you run a VPN or a non standard network configuration, you will need to set an alternative bridge network that doesn't conflict with your existing network. Here is the series of command I use to setup a network:
```
function setup_bridge_for_docker {
  local is_bridge_present=$(check_bridge_present)
  if [ "$is_bridge_present" = "Present" ]; then
    echo "Bridge already present, exiting";
    return
  fi
  sudo systemctl stop docker
  sudo ip link add bridge0 type bridge
  sudo ip addr add 192.168.5.1/24 dev bridge0 
  sudo ip link set bridge0 up
}

function check_bridge_present {
  local bridge_output=$(netstat -i|cut -d' ' -f1|grep 'bridge0')
  if [ -z "$bridge_output" ]; then
    echo "Not Present";
  else
    echo "Present";
  fi
}
```
You can put this into your shell init file to allow quicker access. Ex: if using bash, you can put this file into your `~/.bash_aliases` or `~/.bashrc`.

## Building base docker container
Let's take the example of PyTorch. We will create a docker image with the proper dependencies with the following command:
`sudo docker build --tag pytorch90builder --file configs/PyTorch/Dockerfile_cuda90_builder build_contexts/pytorch/`
The `--tag` is whatever tag you'd like (but make sure that when you run the container it is the proper name)
The second argument is the build context.

## Launching a container for building
We want our container to have access to nvidia-devices so we run with the following options:
1. `--runtime=nvidia` to have access to gpu
1. `-e NVIDIA_DEVICES=all` sets an environment variable in the container that upon loading, nvidia picks up and tells the container nvidia-runtime to allow access on all devices
1. `-e NVIDIA_REQUIRE_CUDA="cuda>=9.0"` also sets an environment variable telling nvidia to use a version greater than what is requested. While one can specify a specific version (=), that one needs to be available on the host by some mechanism.
1. `-e NVIDIA_DRIVER_CAPABILITIES="compute,utility"` are the features to be enabled within the container. For our use, we only want access to CUDA compute capabilties
1. `--mount source=build-vol,target=/builds` tells our container to mount on /builds (in its filesystem) volume created by docker with name `build-vol`. This is used to store completed builds (*.whl) in order to store them on the host machine (since the volume is actually a path existing on the host).
1. `-it` launches an interactive session (`-i`) and a pseudo-tty (`t`)
1. Finally, the last argument we provided here is the base image.

Continuing with the PyTorch example:
`sudo docker run --name pytorch90 --rm --mount source=build-vol,target=/builds --runtime=nvidia -e NVIDIA_DEVICES=all -e NVIDIA_REQUIRE_CUDA="cuda>=9.0" -e NVIDIA_DRIVER_CAPABILITIES="compute,utility" --name pytorch_builder -it pytorch90builder:latest`

## Building
We use anaconda to manage dependencies. Notably, we have created an environment called `build`. So before building, run `conda activate build` so building depedencies are correctly loaded. Afterwards you can the the script found in `/opt/some/path/installer.sh` to build correctly the python wheels (`.whl`)
