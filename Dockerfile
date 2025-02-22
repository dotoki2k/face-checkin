# Use Ubuntu 20.04 as base image
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    sudo \
    python3 \
    python3-pip \
    libgl1-mesa-glx\
    libglib2.0-0\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY . /app

# Install dependencies
RUN pip3 install -r requirements.txt

EXPOSE 5000

# Default command
CMD ["python3", "app.py"]
