#!/bin/bash
#SBATCH --job-name=exp06_riccardo
#SBATCH --account=def-dvera
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=exp06_riccardo_%j.log
# riccardo (about 20,000 rows x 4,296 features): one repeat each. TreeExplainer first (fast),
# then permutation (slow). Smaller tree sweep: 25, 100, 400 trees.

echo "Node: $(hostname)"; echo "CPU: $(lscpu | grep 'Model name')"; echo "Cores: $SLURM_CPUS_PER_TASK"; echo "Started: $(date)"
module load python/3.12
cd ~/explanation-stability-selection
source .venv/bin/activate
export PYTHONPATH=src
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
echo "Code commit: $(git log --oneline -1)"; python -c "import shap, sklearn; print('shap', shap.__version__, 'sklearn', sklearn.__version__)"

COMMON="--config exp06/configs/rf_pool6.yaml --datasets exp06/configs/datasets_exp06.yaml --data-root $HOME/phase2_data --out-root results/exp06 --dataset-name riccardo --repeat 1"
for ex in tree permutation; do
  python exp06/scripts/shap_timing.py $COMMON --explainer $ex
  python exp06/scripts/shap_timing.py $COMMON --explainer $ex --tree-sweep --trees 25,100,400
done
echo "Finished: $(date)"
