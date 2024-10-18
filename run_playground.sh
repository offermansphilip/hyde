#!/bin/bash

# Default values
SERVER=""

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
if [ ! -d "./runs_playground/old" ]; then
  echo "Creating directory ./runs_playground/old"
  mkdir -p "./runs_playground/old"
fi

# Find the youngest log file's modification date (excluding files in ./old)
youngest_file=$(find ./runs_playground -maxdepth 1 -type f -not -path "./runs_playground/old/*" -name "slurm*" -printf "%T@ %p\n" | sort -n | tail -1 | awk '{print $2}')

# Get the modification date in the format YYYY-MM-DD_HH-MM
if [ -n "$youngest_file" ]; then
  log_date=$(date -r "$youngest_file" +"%Y-%m-%d_%H-%M")
else
  echo "No slurm logfiles found."
  exit 1
fi

# Create a directory inside the 'old' folder with the date of the youngest log file
target_dir="./runs_playground/old/$log_date"
if [ ! -d "$target_dir" ]; then
  echo "Creating directory $target_dir"
  mkdir -p "$target_dir"
fi

# Move all log files except those in the 'old' directory and its contents
echo "Moving logfiles from ./runs_playground to $target_dir"
find ./runs_playground -maxdepth 1 -type f -not -name "old" -exec mv {} "$target_dir/" \; 2>/dev/null

# Also move any directories (except 'old') and their contents
find ./runs_playground -maxdepth 1 -type d -not -path "./runs_playground/old" -exec mv {} "$target_dir/" \; 2>/dev/null

# Check if files were moved successfully
if [ $? -eq 0 ]; then
  echo "Logfiles moved successfully."
else
  echo "No slurm logfiles to move."
fi

# Submit job with or without nodelist
if [ -n "$SERVER" ]; then
  echo "Submitting job to server $SERVER"
  sbatch --nodelist="$SERVER" ./start_script_playground.sh
else
  echo "Submitting job"
  sbatch ./start_script_playground.sh
fi

echo "Waiting before opening logs"
sleep 5

echo "Opening logs"
tail -f ./runs_playground/slurm*
