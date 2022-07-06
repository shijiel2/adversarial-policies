1. load conda env in spartan 
module load anaconda3/2021.11
export CONDA_ENVS_PATH=/data/gpfs/projects/punim1629/anaconda3/envs
eval "$(conda shell.bash hook)"

2. create conda env
# Note the Python version is changed to 3.6.8 instead of the required 3.7.* in setup.py in order to avoid bug in training. The setup.py is modified accordingly. 
conda create -n adv_policy python=3.6.8 
conda activate adv_policy

3. install lib 
conda install cudatoolkit=10.0.130
pip install -r requirements-build.txt
pip install -r requirements_spartan.txt
pip install -r requirements-dev.txt
pip install -e .

4. should be good to go?
sbatch task_conda.slurm



