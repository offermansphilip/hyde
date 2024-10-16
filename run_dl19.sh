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
if [ ! -d "./runs_dl19/old" ]; then
  echo "Creating directory ./runs_dl19/old"
  mkdir -p "./runs_dl19/old"
fi

# Move all logfiles matching ./runs_dl19/slurm* to ./runs_dl19/old
echo "Moving logfiles from ./runs_dl19/slurm* to ./runs_dl19/old"
mv ./runs_dl19/slurm* ./runs_dl19/old/ 2>/dev/null

# Check if files were copied successfully
if [ $? -eq 0 ]; then
  echo "Logfiles moved successfully."
else
  echo "No slurm logfiles to move."
fi

# Submit job with or without nodelist
if [ -n "$SERVER" ]; then
  echo "Submitting job to server $SERVER"
  sbatch --nodelist="$SERVER" ./start_script_dl19.sh
else
  echo "Submitting job"
  sbatch ./start_script_dl19.sh
fi
echo "Waiting before opening logs"
sleep 5

echo "Opening logs"
tail -f ./runs_dl19/slurm*
