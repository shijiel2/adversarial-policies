### Please change the paths in the following commands and .slurm files accordingly
Here, we use the CONDA instead of loading modules in Spartan because we can choose the CUDA version in such way to avoid running time errors.

1. Load conda env in spartan<br /> 
`module load anaconda3/2021.11`\
`export CONDA_ENVS_PATH=/data/gpfs/projects/punim1629/anaconda3/envs`\
`eval "$(conda shell.bash hook)"`

2. Create conda env<br />
`conda create -n adv_policy python=3.7`\
`conda activate adv_policy`

3. Install libs<br /> 
Note we use the requirements_spartan.txt to replace the requirements.txt to avoid format issues. The installed packages should be the same.\
`conda install tensorflow-gpu=1.13.1`\
`pip install -r requirements_spartan.txt`\
`pip install -r requirements-dev.txt`\
`pip install -e .`

4. Should be good to go?!<br />
If you want to run the aprl.mutlti.train, remember to adjust cpu and gpu allocations in file "src/aprl/multi/train.py"\
You may want to change the paths/configs in the .slurm as well\
`sbatch task_conda.slurm`\
(Note: For testing the rendering functioin, just run the eval command "python -m aprl.score_agent with env_name=multicomp/SumoHumans-v0 agent_a_type="zoo" agent_a_path="2" agent_b_type="zoo" agent_b_path="2" ". No need to train adv policy.

