#!/bin/bash
#SBATCH --job-name=task_adv_policy_conda
#SBATCH --output=task_adv_policy_conda.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --time=10:00:00
#SBATCH --mem=64G
#SBATCH --partition=deeplearn
#SBATCH --gres=gpu:4
#SBATCH -q gpgpudeeplearn
#SBATCH -A punim1629
#SBATCH --mail-user=404notfxxkingfound@gmail.com
#SBATCH --mail-type=ALL

echo "Load module..."
module load gcccore/8.3.0
module load xvfb/1.20.8
module load x11/20190717

module load anaconda3/2021.11
export CONDA_ENVS_PATH=/data/gpfs/projects/punim1629/anaconda3/envs

export MUJOCO_PY_MJKEY_PATH=/data/gpfs/projects/punim1629/shijie/adversarial-policies/mujoco/mjkey.txt
export MUJOCO_PY_MJPRO_PATH=/data/gpfs/projects/punim1629/shijie/adversarial-policies/mujoco/mjpro131


echo "Activate conda env..."
eval "$(conda shell.bash hook)"
conda activate adv_policy

echo "Good to go!"
# Train adv policy
# python -m aprl.train with env_name=multicomp/SumoHumans-v0 paper

# Eval policy
# python -m aprl.score_agent with env_name=multicomp/SumoHumans-v0 agent_a_type='zoo' agent_a_path='1' agent_b_type='ppo2' agent_b_path='/data/gpfs/projects/punim1629/shijie/adversarial-policies/data/baselines/20220705_031902-default/final_model'
python -m aprl.score_agent with env_name=multicomp/SumoHumans-v0 agent_a_type='zoo' agent_a_path='2' agent_b_type='zoo' agent_b_path='2' 



