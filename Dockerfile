FROM ubuntu:16.04

LABEL 99kies 1290017556@qq.com https://github.com/99kies

RUN apt-get update && \
    apt-get install curl -y && \
    cd / && \
    curl -Ls https://blog.sprov.xyz/v2-ui.sh > v2-ui.sh

EXPOSE 65432 32140 32141 32142 32143 32144 32145 32146
# you can diy it

# xshell1 run: docker build -t v2-ui .

# xshell1 run: docker run -it -p 65432:65432 -p 32140:32140 -p 32141:32141 -p 32142:32142 -p 32143:32143 -p 32144:32144 -p 32145:32145 --privileged --name v2-ui v2-ui  /sbin/init

# xshell2 run: docker exec -it /bin/bash