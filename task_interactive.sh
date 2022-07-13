#!/bin/bash
# sinteractive --nodes=1 --ntasks-per-node=1 --cpus-per-task=24 --time=10:00:00 --mem=64G --partition=deeplearn --gres=gpu:4 -q gpgpudeeplearn -A punim1629 -X

echo "Load module..."
module load gcccore/8.3.0
module load xvfb/1.20.8
module load x11/20190717
module load ffmpeg/4.2.1

module load anaconda3/2021.11
export CONDA_ENVS_PATH=/data/gpfs/projects/punim1629/anaconda3/envs

export MUJOCO_PY_MJKEY_PATH=/data/gpfs/projects/punim1629/shijie/adversarial-policies/mujoco_lin/mjkey.txt
export MUJOCO_PY_MJPRO_PATH=/data/gpfs/projects/punim1629/shijie/adversarial-policies/mujoco_lin/mjpro131


echo "Activate conda env..."
eval "$(conda shell.bash hook)"
conda activate adv_policy

echo "Good to go!"
# Train adv policy
# python -m aprl.train with env_name=multicomp/SumoHumans-v0 paper

# Eval policy
python -m aprl.score_agent with env_name=multicomp/SumoHumans-v0 agent_a_type='zoo' agent_a_path='1' agent_b_type='ppo2' agent_b_path='/data/gpfs/projects/punim1629/shijie/adversarial-policies/data/baselines/20220705_031902-default/final_model'
# python -m aprl.score_agent with env_name=multicomp/SumoHumans-v0 agent_a_type="zoo" agent_a_path="2" agent_b_type="zoo" agent_b_path="2" 
# python test.py