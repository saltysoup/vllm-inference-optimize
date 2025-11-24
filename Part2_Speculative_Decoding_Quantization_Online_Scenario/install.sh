#!/bin/bash

# install dependencies
# vllm
# flashinfer 
# guidellm

sudo apt install -y python3.11-venv
python3 -m venv env 
source env/bin/activate

pip install uv

uv pip install vllm

git clone https://github.com/flashinfer-ai/flashinfer.git --recursive
cd flashinfer
uv pip install -v .

uv pip install guidellm