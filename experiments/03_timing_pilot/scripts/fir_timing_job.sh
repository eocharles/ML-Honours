#!/bin/bash
#SBATCH --job-name=timing_bc
#SBATCH --account=def-dvera
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=timing_bc_%j.log

# Record exactly where and on what this ran
echo "Node: $(hostname)"
echo "CPU: $(lscpu | grep 'Model name')"
echo "Cores allocated: $SLURM_CPUS_PER_TASK"
echo "Started: $(date)"

module load python/3.12
cd ~/explanation-stability-selection
source .venv/bin/activate
export PYTHONPATH=src
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "Code commit: $(git log --oneline -1)"

# 3 repeats of the 2-candidate smoke timing
for i in 1 2 3; do
    python elijah_timing.py
done

# 12 candidates, grouped and alternating order
python elijah_timing_12.py
python elijah_timing_12_alternating.py

echo "Finished: $(date)"
