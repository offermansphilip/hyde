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

# Move all logfiles matching ./runs_playground/slurm* to ./runs_playground/old
echo "Moving logfiles from ./runs_playground/slurm* to ./runs_playground/old"
mv ./runs_playground/slurm* ./runs_playground/old/ 2>/dev/null

# Check if files were copied successfully
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
