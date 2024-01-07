FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

# Update packages
RUN apt update
RUN apt full-upgrade --yes

# Install packages that are useful
RUN apt install --yes vim iputils-ping dnsutils

# Copy needed files
COPY .bashrc.daryl /home/vscode/.bashrc.daryl
COPY .promptname /home/vscode/.promptname
COPY .vimrc /home/vscode/.vimrc
COPY setup-dev.sh /home/vscode/setup-dev.sh

# Set profile
RUN echo 'source ~/.bashrc.daryl' >> /home/vscode/.bashrc

# Set permissions to files
RUN chown vscode:vscode /home/vscode/.*
RUN chown vscode:vscode /home/vscode/*
RUN chmod +x /home/vscode/setup-dev.sh

# Set environment variables
ENV FOLDERNAME 'my_rest_api'
ENV TITLE 'My REST API'