#!/usr/bin/env python

import os

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import golden

from model import QuietStandingModel
from measured_data import DataGenerator
import indirect_collocation
import utils

paths = utils.config_paths()

sample_rate = 300.0  # hz
duration = 20.0  # s
num_nodes = int(sample_rate * duration) + 1
time_interval = duration / (num_nodes - 1)

ref_noise = 0.0  # np.deg2rad(1.0)
platform_pos_mag = 0.05  # 5 cm

accel_noise = (11.0 - 9.75) / 3.0
coord_noise = (0.068 - 0.058) / 2.0
speed_noise = (1.387 - 1.249) / 2.0
torque_noise = (120.898 - 105.078) / 2.0

print('Generating equations of motion.')
# Scale the gains so that the values we search for with IPOPT are all close
# to 0.5 instead of the large gain values.
model = QuietStandingModel(scaled_gains=0.5 * np.ones((2, 4)))
model.derive()

print('Generating simulated noisy data.')
data = DataGenerator(duration, num_nodes, ref_noise, platform_pos_mag,
                     model=model)
data.generate(accel_noise, coord_noise, speed_noise, torque_noise)

# Indirect identification via direct collocation
print('Indirect Identification via Direct Collocation.')
prob = indirect_collocation.setup_problem(num_nodes, data.interval,
                                          data.measured['x'],
                                          data.measured['a'], model)

initial_guess = np.zeros(prob.num_free)

solution, info = prob.solve(initial_guess)

identified_states = solution[:-8].reshape(4, num_nodes).T
identified_gains = (model.gain_scale_factors.flatten() *
                    solution[-8:]).reshape(2, 4)

gain_relative_error = ((identified_gains - model.numerical_gains) /
                       model.numerical_gains * 100.0)

print(gain_relative_error)

template = \
r"""\begin{{tabular}}{{lrrrr}}
  \toprule
        & $\theta_a$ & $\theta_h$ & $\omega_a$ & $\omega_h$ \\
  \midrule
  $T_a$ & {:1.3f} & {:1.3f} & {:1.3f} & {:1.3f} \\
  $T_h$ & {:1.3f} & {:1.3f} & {:1.3f} & {:1.3f}  \\
  \bottomrule
\end{{tabular}}"""

with open(os.path.join(paths['tables_dir'],
                       'sample-relative-error.tex'), 'w') as f:
          f.write(template.format(*gain_relative_error.flatten()))

# Plot measured state trajectories and identified state trajectories.

# This is the  column width for the abstract. Should change if this is ever
# in the paper.
abstract_col_width = 257.61894  # pt
inches_per_pt = 1.0 / 72.27
fig_width = inches_per_pt * abstract_col_width

params = {'backend': 'ps',
          'axes.labelsize': 8,
          'axes.titlesize': 10,
          'font.size': 10,
          'legend.fontsize': 6,
          'xtick.labelsize': 6,
          'ytick.labelsize': 6,
          'text.usetex': True,
          'font.family': 'serif',
          'font.serif': ['Computer Modern'],
          'figure.figsize': (fig_width, fig_width / golden),
          }

plt.rcParams.update(params)
fig, axes = plt.subplots(2, 1, sharex=True)

plot_dur = 3.0 * sample_rate

# coordinates
axes[0].plot(data.time[:plot_dur],
             np.rad2deg(data.measured['x'][:plot_dur, :2]), '.k',
             markersize=1.0, label='_nolegend_')
axes[0].plot(data.time[:plot_dur],
             np.rad2deg(identified_states[:plot_dur, :2]), '-', alpha=0.75)
axes[0].set_ylabel('Angle [deg]')
axes[0].legend([r'$\theta_a$', r'$\theta_h$'])

# speeds
axes[1].plot(data.time[:plot_dur],
             np.rad2deg(data.measured['x'][:plot_dur, 2:]), '.k',
             markersize=1.0, label='_nolegend_')
axes[1].plot(data.time[:plot_dur],
             np.rad2deg(identified_states[:plot_dur, 2:]), '-', alpha=0.75)
axes[1].set_ylabel('Angluar Rate [deg/s]')
axes[1].set_xlabel('Time [s]')
axes[1].legend([r'$\omega_a$', r'$\omega_h$'])

plt.tight_layout()

fig.savefig(os.path.join(paths['figures_dir'], 'trajectory-comparison.pdf'))
