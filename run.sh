#!/bin/bash

# Default values
SERVER=""

# Directories and common variables
RUNS_DIR="./runs"
OLD_DIR="$RUNS_DIR/old"
START_SCRIPT="./start_script.sh"
LOG_PATTERN="slurm*"

# Parse options
while getopts ":s:" opt; do
  case $opt in
    s)
      SERVER=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Check if the 'old' directory exists, create it if necessary
if [ ! -d "$OLD_DIR" ]; then
  echo "Creating directory $OLD_DIR"
  mkdir -p "$OLD_DIR"
fi

# Find the youngest log file's modification date (excluding files in ./old)
youngest_file=$(find "$RUNS_DIR" -maxdepth 1 -type f -not -path "$OLD_DIR/*" -name "$LOG_PATTERN" -printf "%T@ %p\n" | sort -n | tail -1 | awk '{print $2}')

# Get the modification date in the format YYYY-MM-DD_HH-MM
if [ -n "$youngest_file" ]; then
  log_date=$(date -r "$youngest_file" +"%Y-%m-%d_%H-%M")
else
  echo "No slurm logfiles found."
  exit 1
fi

# Create a directory inside the 'old' folder with the date of the youngest log file
target_dir="$OLD_DIR/$log_date"
if [ ! -d "$target_dir" ]; then
  echo "Creating directory $target_dir"
  mkdir -p "$target_dir"
fi

# Move all log files except those in the 'old' directory and its contents
echo "Moving logfiles from $RUNS_DIR to $target_dir"
find "$RUNS_DIR" -maxdepth 1 -type f -not -name "old" -exec mv {} "$target_dir/" \; 2>/dev/null

# Also move any directories (except 'old') and their contents
find "$RUNS_DIR" -maxdepth 1 -type d -not -path "$OLD_DIR" -exec mv {} "$target_dir/" \; 2>/dev/null

# Check if files were moved successfully
if [ $? -eq 0 ]; then
  echo "Logfiles moved successfully."
else
  echo "No slurm logfiles to move."
fi

# Submit job with or without nodelist
if [ -n "$SERVER" ]; then
  echo "Submitting job to server $SERVER"
  sbatch --nodelist="$SERVER" "$START_SCRIPT"
else
  echo "Submitting job"
  sbatch "$START_SCRIPT"
fi

# Wait before opening logs
echo "Waiting before opening logs"
sleep 10

# Open logs
echo "Opening logs"
tail -f "$RUNS_DIR"/*