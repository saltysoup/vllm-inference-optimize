#!/bin/bash

# install dependencies
# vllm
# flashinfer (flash attention support for FP4 not stable yet)
# guidellm
# lm-evaluation-harness

sudo apt install -y python3.11-venv
python3 -m venv env 
source env/bin/activate

pip install uv

uv pip install vllm

git clone https://github.com/flashinfer-ai/flashinfer.git --recursive
cd flashinfer
uv pip install -v .

uv pip install guidellm

git clone --depth 1 https://github.com/EleutherAI/lm-evaluation-harness
cd lm-evaluation-harness
uv pip install -e .
uv pip install lm-eval[api]
