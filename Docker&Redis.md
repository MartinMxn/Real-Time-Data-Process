# Docker
## Why?
1. Used to solve the diff of env bug, the develop env of dev machine, QA machine and production env may be different. Docker could eliminate env inconsistency   
2. Another point is to increase resource utilization and isolation.

## What?
A tool to package and deploy app inside containers(isolated env). Written in Go.
// extend docker compose / swarm  

### Architecture
#### Client-Server Arch  
terminal is docker client, (docker build/pull/run), docker client will translate your command line to specific task and send it to docker daemon. (eval...connect with docker machine)
#### 
Server - Docker daemon  
tasks requests from docker client and dispatch/route to corresponding handler  
engine takes request and do task (like create container)
#### 
Docker registry  
a warehouse for container images  
public <a href="https://hub.docker.com/">DockerHub</a> or private
#### 
Docker image  
The basis of containers  
Layer by layer
Instructions are stored in a file called **Dockerfile**

## How?
A linux kernel functionality to  
1.  perform resource limiting  
2.  resource prioritization  
3.  resource accounting  
Docker use cgroup to achieve resource limiting  
### <a href="https://github.com/wsargent/docker-cheat-sheet">Docker command</a>


# Redis
in memory data structure store to cache or act as message queue  
## Used as LRU cache
## Used as non-critical message queue
