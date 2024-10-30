#!/bin/bash

# Default values
NUM_RUNS=10
RUNS_DIR="./runs/runs_1"
START_SCRIPT="./start_script.sh"

# Create the run directory if it doesn't exist
if [ ! -d "$RUNS_DIR" ]; then
    echo "Creating directory $RUNS_DIR"
    mkdir -p "$RUNS_DIR"
fi

# Function to submit a job
submit_job() {
  local run_number=$1
  local run_dir="$RUNS_DIR/run_$run_number"
  
  # Create a directory for the current run
  mkdir -p "$run_dir"
  
  # Set output and error file paths
  local output_file="$run_dir/slurm.out"
  local error_file="$run_dir/slurm.err"
  
  # If no server was provided, try to find an idle server
  # SERVER=$(sinfo -t idle -h -o "%N" | awk -F, '{print $1}')
  # SERVER="lenurple"
  SERVER=$(sinfo -o "%N %T" | awk '$2 == "idle" {print $1}' | tr ',' '\n')
  while [ -z "$SERVER" ]; do
    echo "No idle server found. Checking again in 10 seconds."
    sleep 10
    SERVER=$(sinfo -o "%N %T" | awk '$2 == "idle" {print $1}' | tr ',' '\n')
    # SERVER=$(sinfo -t idle -h -o "%N" | awk -F, '{print $1}')
  done
  echo "Found idle server: $SERVER"
  
  # Submit the job with the appropriate output, error files, job number, and output directory
  echo "Submitting run $run_number to server $SERVER"
  sbatch --nodelist="$SERVER" -o "$output_file" -e "$error_file" "$START_SCRIPT" -j "$run_number" -o "$run_dir"
}

# Run the script 10 times
for ((i=1; i<=NUM_RUNS; i++)); do
  submit_job $i
  echo "Run $i submitted, waiting 10 seconds before checking for the next run."
  sleep 10
done
