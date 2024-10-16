#!/bin/bash
#SBATCH -p GPU                # partition (queue)
#SBATCH -N 1                  # number of nodes
#SBATCH -t 0-36:00            # time (D-HH:MM)
#SBATCH -o ./runs_dl19/slurm.%N.%j.out   # STDOUT
#SBATCH -e ./runs_dl19/slurm.%N.%j.err   # STDERR
#SBATCH --gres=gpu:1          # Request 1 GPU

# Load the appropriate environment
if [ -f "/usr/local/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/usr/local/anaconda3/etc/profile.d/conda.sh"
else
    export PATH="/usr/local/anaconda3/bin:$PATH"
fi

# Activate the conda environment
source activate hyde_dl19

# Start the Ollama server in the background
echo "Starting Ollama server..."
ollama serve &

# Wait a bit to ensure the server starts
sleep 10  # Adjust the time as necessary for the server to start

# Run the Python script
echo "Running the Python script..."
python ./src/hyde_dl19.py

# Print a message after completion
echo "Job completed."
