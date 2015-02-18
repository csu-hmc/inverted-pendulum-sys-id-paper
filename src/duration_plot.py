#!/usr/bin/env python

"""This plot intends to answer the question of whether the duration of the
measured data affects the accuracy of the identification.

1. Generate a long data sequence with no reference noise and no
   measurement noise.
2. Compute the minimum amount of data required for each method.
3. For short to long durations of the data sequence identify the gains
   with both the direct and indirect (collocation) methods.
4. Plot the relative error in the gain identification as a function of the
   measurement duration. Also plot the computation time.

"""

import numpy as np
import logbook
import matplotlib.pyplot as plt

from model import QuietStandingModel
from measured_data import DataGenerator
import direct_identification
import indirect_collocation
import utils

sample_rate = 100.0  # hz
duration = 600.0  # s
total_num_nodes = int(sample_rate * duration) + 1
time_interval = duration / (total_num_nodes - 1)

model = QuietStandingModel(scaled_gains=0.5)
model.derive()

logbook.info('Defining the model.')
generator = DataGenerator(duration, total_num_nodes, 0.0, 0.1, model)
logbook.info('Simulating.')
# NOTE : Joblib can't pickle the DataGenerator because it has unpickable
# SymPy functions tied to the model, so the generate() call can't be cached.
# TODO : Manually cache this result.
accel_noise = 11.0 - 9.75
coord_noise = 0.068 - 0.058
speed_noise = 0.212 - 0.199
torque_noise = 120.898 - 105.078
generator.generate(accel_noise, coord_noise, speed_noise, torque_noise)

# For direct ID we need at least n time steps (n=4 states)
# For indirect maybe all you need is 2 time steps.

num_durations = 30
duration_lengths = np.logspace(np.log10(1.0), np.log10(duration),
                               num_durations)

direct_identified_gains = np.empty((num_durations,
                                    generator.model.numerical_gains.size),
                                   dtype=float)
indirect_identified_gains = np.empty_like(direct_identified_gains)

indirect_times = []

ipopt_opts = {'print_level': 0,
              'sb': "yes",
              'linear_solver': 'ma57'}

logbook.info('Identifying the gains.')
for i, dur_len in enumerate(duration_lengths):
    idx = np.argmin(np.abs(generator.time - dur_len))
    input_traj = generator.measured['u'][:idx]
    state_traj = generator.measured['x'][:idx]
    logbook.info('Identifying the gains directly.')
    direct_identified_gains[i] = direct_identification.identify(input_traj,
                                                                state_traj)

    logbook.info('Identifying the gains indirectly.')
    accel = generator.measured['a'][:idx]
    prob = indirect_collocation.setup_problem(idx, time_interval,
                                              state_traj.T.flatten(),
                                              accel, model)
    for k, v in ipopt_opts.items():
        prob.addOption(k, v)

    initial_guess = np.zeros(prob.num_free)
    # Give it the known gains as a guess, because all we care about is
    # how the optimal solution is affected by the accel and noise.
    initial_guess[-8:] = model.numerical_gains.flatten()

    @utils.timeit
    def solve():
        solution, info = prob.solve(initial_guess)
        return solution, info
    solution, info, time = solve()

    indirect_times.append(time)

    # TODO : If the solution isn't close to the known gains then it may not
    # have converged and it should be run one or more times until it does.

    indirect_identified_gains[i] = \
        model.gain_scale_factors.flatten() * solution[-8:]

known_gains = model.numerical_gains.flatten()

logbook.info('Plotting.')
fig, axes = plt.subplots(2, 4, sharex=True)
axes = axes.flatten()

for i, gains in enumerate(direct_identified_gains.T):

    rel_error = np.abs((gains - known_gains[i]) / known_gains[i])

    axes[i].plot(duration_lengths, rel_error)
    axes[i].set_xscale('log')

    if i > 3:
        axes[i].set_xlabel('Duration [s]')

    if i == 0 or i == 4:
        axes[i].set_ylabel('Relative Error')

fig, axes = plt.subplots(2, 4, sharex=True)
axes = axes.flatten()

for i, gains in enumerate(indirect_identified_gains.T):

    rel_error = np.abs((gains - known_gains[i]) / known_gains[i])

    axes[i].plot(duration_lengths, rel_error)
    axes[i].set_xscale('log')

    if i > 3:
        axes[i].set_xlabel('Duration [s]')

    if i == 0 or i == 4:
        axes[i].set_ylabel('Relative Error')

fig, ax = plt.subplots()
ax.plot(duration_lengths, indirect_times)
ax.set_xscale('log')
