#!/bin/bash

# Set the environment name as a variable
ENV_NAME="hyde2"

# Step 1: Initialize conda for the shell
echo "Initializing conda for the shell..."
conda init zsh  # Use the appropriate shell if not using bash

# Step 2: Restart the shell or source the configuration
# Uncomment this if you need to source manually
# echo "Sourcing shell configuration..."
# source ~/.bashrc  # For bash, or equivalent for your shell

# Step 3: Create the environment
echo "Creating the conda environment '$ENV_NAME' with Python 3.9..."
conda create --name $ENV_NAME python=3.9 -y

# Step 4: Activate the environment
echo "Activating the '$ENV_NAME' environment..."
conda activate $ENV_NAME

# Step 5: Installing packages
echo "Installing cohere, faiss-cpu, transformers, and PyTorch..."
conda install -y cohere faiss-cpu transformers pytorch cpuonly -c pytorch
conda install -c conda-forge faiss-cpu

echo "Installing OpenAI package (version 0.28)..."
pip install openai==0.28

echo "Installing JDK 21 for pyserini..."
conda install -c conda-forge openjdk=21

echo "Installing pyserini..."
pip install pyserini

# Check if the contriever_msmarco_index directory exists
INDEX_DIR="contriever_msmarco_index"
if [ ! -d "$INDEX_DIR" ]; then
  echo "contriever_msmarco_index directory not found. Downloading and extracting..."
  
  # Download contriever_msmarco_index.tar.gz
  wget https://www.dropbox.com/s/dytqaqngaupp884/contriever_msmarco_index.tar.gz

  # Extract the tar.gz file 
  echo "Extracting contriever_msmarco_index.tar.gz..."
  tar -xvf contriever_msmarco_index.tar.gz
else
  echo "contriever_msmarco_index directory already exists. Skipping download."
fi

# Step 6: Confirm successful installation
echo "All packages installed successfully in the '$ENV_NAME' environment!"

# Step 7: Listing installed packages
echo "Listing installed packages in '$ENV_NAME' environment..."
conda list