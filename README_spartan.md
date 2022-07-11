### Please change the paths in the following commands and .slurm files accordingly
Here, we use the CONDA instead of loading modules in Spartan because we can choose the CUDA version in such way to avoid running time errors.

1. Load conda env in spartan<br /> 
`module load anaconda3/2021.11`\
`export CONDA_ENVS_PATH=/data/gpfs/projects/punim1629/anaconda3/envs`\
`eval "$(conda shell.bash hook)"`

2. Create conda env<br />
Note the Python version is changed to 3.6.8 instead of 3.7.* as required in setup.py because that will cause error in the training process. Of course, the setup.py is already modified accordingly.\
`conda create -n adv_policy python=3.6.8`\
`conda activate adv_policy`

3. Install libs<br /> 
`conda install cudatoolkit=10.0.130`\
`pip install -r requirements-build.txt`\
`pip install -r requirements_spartan.txt`\
`pip install -r requirements-dev.txt`\
`pip install -e .`

4. Should be good to go?<br />
You may want to change the paths in the .slurm as well\
`sbatch task_conda.slurm`



