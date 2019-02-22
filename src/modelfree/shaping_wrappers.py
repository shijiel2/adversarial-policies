from collections import defaultdict
import json

import numpy as np
from stable_baselines import logger
from stable_baselines.common.base_class import BaseRLModel
from stable_baselines.common.vec_env import VecEnvWrapper

from modelfree import envs  # noqa - needed to register sumo_auto_contact
from modelfree.scheduling import LinearAnnealer


class RewardShapingEnv(VecEnvWrapper):
    """A more direct interface for shaping the reward of the attacking agent."""

    default_shaping_params = {
        'reward_center': 1,
        'reward_ctrl': -1,
        'reward_contact': -1,
        'reward_survive': 1,

        # sparse reward field as per gym_compete/new_envs/multi_agent_env:151
        'reward_remaining': 1,
        # dense reward field as per gym_compete/new_envs/agents/humanoid_fighter:45
        # 'reward_move': 10,
    }

    def __init__(self, env, shaping_params=default_shaping_params,
                 reward_annealer=None):
        super().__init__(env)
        self.shaping_params = shaping_params
        self.reward_annealer = reward_annealer
        self.counter = 0

        self.ep_rew_dict = defaultdict(list)
        self.step_rew_dict = defaultdict(lambda: [[] for _ in range(self.num_envs)])

    def _log_sparse_dense_rewards(self):
        if self.counter == 2048 * self.num_envs:
            num_episodes = len(self.ep_rew_dict['reward_remaining'])
            dense_terms = ['reward_center', 'reward_ctrl', 'reward_contact', 'reward_survive']
            for term in dense_terms:
                assert len(self.ep_rew_dict[term]) == num_episodes

            ep_dense_mean = sum([sum(self.ep_rew_dict[t]) for t in dense_terms]) / num_episodes
            logger.logkv('epdensemean', ep_dense_mean)

            ep_sparse_mean = sum(self.ep_rew_dict['reward_remaining']) / num_episodes
            logger.logkv('epsparsemean', ep_sparse_mean)

            c = self.reward_annealer()
            ep_rew_mean = c * ep_dense_mean + (1 - c) * ep_sparse_mean
            logger.logkv('eprewmean_true', ep_rew_mean)

            logger.logkv('rew_anneal', c)

            for rew_type in self.ep_rew_dict:
                self.ep_rew_dict[rew_type] = []
            self.counter = 0

    def reset(self):
        return self.venv.reset()

    def step_wait(self):
        obs, rew, done, infos = self.venv.step_wait()

        # replace rew with differently shaped rew
        # victim is agent 0, attacker is agent 1
        for env_num in range(self.num_envs):
            shaped_reward = 0
            for rew_type, rew_value in infos[env_num][1].items():
                if rew_type not in self.shaping_params:
                    continue

                weighted_reward = self.shaping_params[rew_type] * rew_value
                self.step_rew_dict[rew_type][env_num].append(weighted_reward)
                if self.reward_annealer is not None:
                    c = self.get_annealed_exploration_reward()
                    if rew_type == 'reward_remaining':
                        weighted_reward *= (1 - c)
                    else:
                        weighted_reward *= c
                shaped_reward += weighted_reward

            if done[env_num]:
                for rew_type in self.step_rew_dict:
                    self.ep_rew_dict[rew_type].append(sum(self.step_rew_dict[rew_type][env_num]))
                    self.step_rew_dict[rew_type][env_num] = []
            self.counter += 1
            self._log_sparse_dense_rewards()
            rew[env_num] = shaped_reward

        return obs, rew, done, infos

    def get_annealed_exploration_reward(self):
        """
        Returns c (which will be annealed to zero) s.t. the total reward equals
        c * reward_move + (1 - c) * reward_remaining
        """
        c = self.reward_annealer()
        assert 0 <= c <= 1
        return c


class NoisyAgentWrapper(BaseRLModel):
    def __init__(self, agent, noise_annealer, noise_type='gaussian'):
        """
        Wrap an agent and add noise to its actions
        :param agent: PolicyToModel(BaseRLModel) the agent to wrap
        :param noise_annealer: Annealer.get_value - presumably the noise should be decreased
        over time in order to get the adversarial policy to perform well on a normal victim.
        :param noise_type: str - the type of noise parametrized by noise_annealer's value.
        Current options are [gaussian]
        """
        self.agent = agent
        self.sess = agent.sess
        self.noise_annealer = noise_annealer
        self.noise_generator = self._get_noise_generator(noise_type)

    def _get_noise_generator(self, noise_type):
        noise_generators = {
            'gaussian': lambda x, size: np.random.normal(scale=x, size=size)
        }
        return noise_generators[noise_type]

    def predict(self, observation, state=None, mask=None, deterministic=False):
        original_actions, states = self.agent.predict(observation, state, mask, deterministic)
        action_shape = original_actions.shape

        noise_param = self.noise_annealer()
        noise = self.noise_generator(noise_param, action_shape)
        normed_noise = original_actions * noise

        noisy_actions = original_actions + normed_noise
        return noisy_actions, states

    def reset(self):
        return self.agent.reset()

    def setup_model(self):
        pass

    def learn(self):
        raise NotImplementedError()

    def action_probability(self, observation, state=None, mask=None, actions=None):
        raise NotImplementedError()

    def save(self, save_path):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()


class HumanoidEnvWrapper(VecEnvWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.env = env

    def reset(self):
        return self.env.reset()

    def step_wait(self):
        obs, rew, done, infos = self.env.step_wait()
        num_envs = len(obs)
        for env_num in range(num_envs):
            rew[env_num] -= infos[env_num]['reward_linvel']

        return obs, rew, done, infos


def apply_env_wrapper(single_env, rew_shape_params, env_wrapper_type, scheduler):
    if rew_shape_params is not None:
        shaping_params = RewardShapingEnv.default_shaping_params
        if rew_shape_params is not None:
            config = json.load(open(rew_shape_params))
            shaping_params.update(config)

        rew_shape_anneal_frac = shaping_params.get('rew_shape_anneal_frac', 0)
        assert 0 <= rew_shape_anneal_frac <= 1
        if rew_shape_anneal_frac > 0:
            rew_shape_func = LinearAnnealer(1, 0, rew_shape_anneal_frac).get_value
        else:
            rew_shape_func = None

        scheduler.set_func('rew_shape', rew_shape_func)
        return RewardShapingEnv(single_env, shaping_params=shaping_params,
                                reward_annealer=scheduler.get_func('rew_shape'))
    else:
        wrappers = {
            'humanoid': HumanoidEnvWrapper,
            None: lambda x: x
        }
        return wrappers[env_wrapper_type](single_env)


def apply_victim_wrapper(victim, victim_noise_anneal_frac, victim_noise_param, scheduler):
    if victim_noise_anneal_frac is not None:
        assert 0 <= victim_noise_anneal_frac <= 1
        assert 0 < victim_noise_param
        noise_anneal_func = LinearAnnealer(victim_noise_param, 0,
                                           victim_noise_anneal_frac).get_value
        scheduler.set_func('noise', noise_anneal_func)
        return NoisyAgentWrapper(victim, noise_annealer=scheduler.get_func('noise'))

    else:
        return victim