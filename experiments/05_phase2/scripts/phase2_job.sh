#!/bin/bash
#SBATCH --job-name=phase2
#SBATCH --account=def-dvera
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=phase2_%j.log

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

DATA=~/phase2_data
OUT=results/phase2
COMMON="--config phase2/configs/phase2_pool12.yaml --datasets phase2/configs/phase2_datasets.yaml --data-root $DATA --out-root $OUT"

for ds in breast_cancer spambase; do
    for r in 1 2 3 4 5; do
        python phase2/scripts/phase2_timing.py $COMMON --dataset-name $ds --repeat $r
    done
    for r in 1 2 3; do
        python phase2/scripts/phase2_timing.py $COMMON --dataset-name $ds --repeat $r --tree-sweep
    done
done
echo "Finished: $(date)"
