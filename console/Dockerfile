ARG BASE_VERSION
FROM docker-registry.7onetella.net/7onetella/base:${BASE_VERSION}

RUN apt-get update --fix-missing  &&    \
    apt-get -q -y  install              \
    python3                             \
    python3-pip                         \
    `# vag dependencies          `      \
    openssl                             \
    postgresql                          \
    libpq-dev                           


RUN mkdir -p /console                   && \
    chown -R coder:coder   /console     

COPY --chown=coder:coder requirements.txt  /console

RUN cd /console                     && \
    pip3 install "pip>=20"          && \
    pip3 install -r ./requirements.txt  

COPY --chown=coder:coder .              /console

USER 1000
ENV USER=coder
WORKDIR /home/coder
USER coder

COPY .ssh /home/${USER}/.ssh
COPY --chown=coder:coder entrypoint.sh  /
RUN  chmod +x /entrypoint.sh


EXPOSE 22
EXPOSE 5000


CMD /entrypoint.sh