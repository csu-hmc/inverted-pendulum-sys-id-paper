"""

Here we we want to show the computational time required for each of the
methods.

The same inputs should be used for each method.

initial guess is only needed for the indirect methods
collocation requires guessing the states and the gains
shooting only requies guessing the gains

for the indirect methods we should show different initial guesses:

1. give the known gains
2. give all zeros
3. given random values from 0.0 to 1.0.

I need to have the same solution tolerance set for both indirect methods

"""

import logbook
import numpy as np

from model import QuietStandingModel
from measured_data import DataGenerator
import direct_identification
import indirect_collocation
import utils

sample_rate = 100.0  # hz
duration = 60.0  # s
total_num_nodes = int(sample_rate * duration) + 1
time_interval = duration / (total_num_nodes - 1)

logbook.info('Defining the model.')
model = QuietStandingModel(scaled_gains=0.5)
model.derive()

logbook.info('Simulating.')
generator = DataGenerator(duration, total_num_nodes, 0.0, 0.05, model)
accel_noise = 11.0 - 9.75
coord_noise = 0.157 - 0.118
speed_noise = 1.997 - 1.818
torque_noise = 120.898 - 105.078
generator.generate(accel_noise, coord_noise, speed_noise, torque_noise)

logbook.info('Timing direct identification.')
ider = direct_identification.ControllerIdentifier(generator.measured['u'],
                                                  generator.measured['x'])

@utils.timeit
def identify():
    return ider.identify()

gains, direct_time = identify()

logbook.info('Timing indirect identification with collocation.')
prob = indirect_collocation.setup_problem(total_num_nodes, time_interval,
                                          generator.measured['x'],
                                          generator.measured['a'], model)
prob.addOption('linear_solver', 'ma57')

initial_guess = np.zeros(prob.num_free)

@utils.timeit
def identify():
    return prob.solve(initial_guess)

res, indirect_collocation_time = identify()
