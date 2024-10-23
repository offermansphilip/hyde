#!/bin/bash
#SBATCH -p GPU                # partition (queue)
#SBATCH -N 1                  # number of nodes
#SBATCH -t 0-36:00            # time (D-HH:MM)
#SBATCH --gres=gpu:1          # Request 1 GPU

# Default values for arguments
OUTPUT_DIR=""
JOB_NUMBER=""

# Parse options
while getopts ":o:j:" opt; do
  case $opt in
    o)
      OUTPUT_DIR=$OPTARG
      ;;
    j)
      JOB_NUMBER=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Check if the output directory and job number are provided
if [ -z "$OUTPUT_DIR" ] || [ -z "$JOB_NUMBER" ]; then
  echo "Both output directory (-o) and job number (-j) must be provided."
  exit 1
fi

CONDA_PATH="/usr/local/anaconda3"
ENV_NAME="hyde"
OLLAMA_LOG="${OUTPUT_DIR}/ollama.log"
PYTHON_SCRIPT="./src/experiment.py"

# Create the output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating directory $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Load the appropriate environment
if [ -f "${CONDA_PATH}/etc/profile.d/conda.sh" ]; then
    . "${CONDA_PATH}/etc/profile.d/conda.sh"
else
    export PATH="${CONDA_PATH}/bin:$PATH"
fi

# Activate the conda environment
source activate ${ENV_NAME}

# Start the Ollama server in the background and log the output
echo "Starting Ollama server..."
ollama serve > ${OLLAMA_LOG} 2>&1 &

# Wait a bit to ensure the server starts
sleep 10  # Adjust the time as necessary for the server to start

# Run the Python script with the job number and output directory as arguments
echo "Running the Python script with job number ${JOB_NUMBER} and output directory ${OUTPUT_DIR}..."
python ${PYTHON_SCRIPT} --job_number ${JOB_NUMBER} --run_directory ${OUTPUT_DIR}

# Print a message after completion
echo "Job completed."