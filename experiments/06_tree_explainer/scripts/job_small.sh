#!/bin/bash
#SBATCH --job-name=exp06_small
#SBATCH --account=def-dvera
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=exp06_small_%j.log
# breast_cancer and spambase: RF pool (3 repeats) and tree sweep (3 repeats), both explainers

echo "Node: $(hostname)"; echo "CPU: $(lscpu | grep 'Model name')"; echo "Cores: $SLURM_CPUS_PER_TASK"; echo "Started: $(date)"
module load python/3.12
cd ~/explanation-stability-selection
source .venv/bin/activate
export PYTHONPATH=src
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "Code commit: $(git log --oneline -1)"; python -c "import shap, sklearn; print('shap', shap.__version__, 'sklearn', sklearn.__version__)"

COMMON="--config exp06/configs/rf_pool6.yaml --datasets exp06/configs/datasets_exp06.yaml --data-root $HOME/phase2_data --out-root results/exp06"
for ds in breast_cancer spambase; do
  for ex in permutation tree; do
    for r in 1 2 3; do python exp06/scripts/shap_timing.py $COMMON --dataset-name $ds --repeat $r --explainer $ex; done
    for r in 1 2 3; do python exp06/scripts/shap_timing.py $COMMON --dataset-name $ds --repeat $r --explainer $ex --tree-sweep; done
  done
done
echo "Finished: $(date)"
