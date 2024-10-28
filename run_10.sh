#!/bin/bash
#SBATCH -p GPU                # partition (queue)
#SBATCH -N 1                  # number of nodes
#SBATCH -t 0-36:00            # time (D-HH:MM)
#SBATCH -o slurm.%N.%j.out # STDOUT
#SBATCH -e slurm.%N.%j.err # STDERR
#SBATCH --gres=gpu:1          # Request 1 GPU

# Default values
NUM_RUNS=20
RUNS_DIR="./runs_3"
CONDA_PATH="/usr/local/anaconda3"
ENV_NAME="hyde"
PYTHON_SCRIPT="./src/experiment.py"
OLLAMA_LOG="${RUNS_DIR}/ollama2.log"

# Load Conda environment
if [ -f "${CONDA_PATH}/etc/profile.d/conda.sh" ]; then
    . "${CONDA_PATH}/etc/profile.d/conda.sh"
else
    export PATH="${CONDA_PATH}/bin:$PATH"
fi

# Activate the conda environment
source activate ${ENV_NAME}

# Create the main output directory if it doesn't exist
if [ ! -d "$RUNS_DIR" ]; then
    echo "Creating directory $RUNS_DIR"
    mkdir -p "$RUNS_DIR"
fi

# Set tmp dir
TMPDIR=/home/u440541/tmp
TEMP=/home/u440541/tmp 
OLLAMA_TMPDIR=/home/u440541/tmp 
# OLLAMA_MODELS=/scratch/ollama
# Start the Ollama server in the background and log the output
echo "Starting Ollama server and pulling model..."
ollama serve >> ${OLLAMA_LOG} 2>&1 &
sleep 10  # Ensure server starts

# Pull the required model
ollama pull llama3.1 >> ${OLLAMA_LOG} 2>&1 &
sleep 10  # Wait to ensure the model is available

# Function to start an experiment run
start_experiment_run() {
  local run_number=$1
  local run_dir="$RUNS_DIR/run_$run_number"
  
  # Create a directory for the current run
  mkdir -p "$run_dir"
  
  # Set output and error file paths
  local output_file="$run_dir/slurm.out"
  local error_file="$run_dir/slurm.err"
  
  # Start the Python script with specific job number and run directory
  echo "Running experiment for run number $run_number with output directory $run_dir..."
  python ${PYTHON_SCRIPT} --job_number ${run_number} --run_directory ${run_dir} > "$output_file" 2> "$error_file" &
}

# Run 10 experiments in parallel with different output directories
for ((i=11; i<=NUM_RUNS; i++)); do
  start_experiment_run $i
  echo "Started experiment run $i"
  sleep 10  # Optional delay to stagger the start times slightly
done

# Wait for all background jobs to complete
wait

echo "All experiments completed."