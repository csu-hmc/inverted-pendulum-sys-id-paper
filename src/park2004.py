#!/usr/bin/env python

import numpy as np

from model import PlanarStandingHumanOnMovingPlatform
from measured_data import DataGenerator
import direct_identification
import indirect_collocation
import indirect_shooting
from utils import print_gains

num_nodes = 4001
duration = 20.0
ref_noise_std = 0.0  # np.deg2rad(1.0)
platform_pos_mag = 0.01
platform_accel_noise_std = 0.0  # np.deg2rad(0.25)
coordinate_noise_std = 0.0  # np.deg2rad(0.25)
speed_noise_std = 0.0  # np.deg2rad(0.25)
torque_noise_std = 0.0  # 0.5

print('Generating equations of motion.')
# We are going to scale the gains so that the values we search for with
# IPOPT are all close to 0.5 instead of the large gain values.
h = PlanarStandingHumanOnMovingPlatform(scaled_gains=0.5 * np.ones((2, 4)))
h.derive()

print('Generating simulated noisy data.')
data = DataGenerator(duration, num_nodes, ref_noise_std, platform_pos_mag,
                     model=h)
data.generate(platform_accel_noise_std, coordinate_noise_std,
              speed_noise_std, torque_noise_std)

# Direct identification
print('Direct Identification.')
direct_gains = direct_identification.identify(data.measured['u'],
                                              data.measured['x'])

# Indirect identification via direct collocation
print('Indirect Identification via Direct Collocation.')
indirect_dc_gains = indirect_collocation.identify(num_nodes, data.interval,
                                                  data.measured['x'],
                                                  data.measured['a'], h)

# Indirect identification via single shooting
print('Indirect Identification via Shooting.')
indirect_sh_gains = indirect_shooting.identify(data.time,
                                               data.measured['x'], data.rhs,
                                               data.rhs_args, h)

print_gains(h.numerical_gains.flatten(),
            direct_gains,
            indirect_dc_gains,
            indirect_sh_gains)
