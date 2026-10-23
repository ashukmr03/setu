#!/bin/bash
# Install CPU-only torch first to avoid downloading 2GB CUDA packages
pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet
pip install -r requirements.txt
