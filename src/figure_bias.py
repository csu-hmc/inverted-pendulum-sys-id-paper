#!/usr/bin/env python

"""This figure tries to show how one needs have a "ratio" of external
perturbations to reference noise that is of some value > 1 to properly
directly identify the controller."""

import os

import numpy as np
from progressbar import ProgressBar
from matplotlib import cm
import matplotlib.pyplot as plt
# this import is required for the projection='3d' to work
from mpl_toolkits.mplot3d.axes3d import Axes3D

from model import QuietStandingModel
from measured_data import DataGenerator
import direct_identification
import utils

filename = os.path.join(utils.config_paths(), 'identified-gains.npz')

if os.path.isfile(filename):

    with np.load(filename) as data:
        ref_noise_stds = ['ref_noise_stds']
        platform_pos_mags = ['platform_pos_mags']
        platform_acc_stds = data['platform_acc_stds']
        identified_gains = ['identified_gains']

else:

    num_nodes = 501
    duration = 5.0

    platform_accel_noise_std = 0.0
    coordinate_noise_std = 0.0
    speed_noise_std = 0.0
    torque_noise_std = 0.0

    # Generate the symbolic dynamic model.
    model = QuietStandingModel()
    model.derive()

    ref_noise_stds = np.linspace(0.0, 0.03, num=51)
    platform_pos_mags = np.linspace(0.0, 0.3, num=51)
    platform_acc_stds = np.empty((51, 51), dtype=float)

    shape = (len(ref_noise_stds), len(platform_pos_mags), 8)
    identified_gains = np.empty(shape, dtype=float)

    pbar = ProgressBar(maxval=len(ref_noise_stds) * len(platform_pos_mags))
    pbar.start()

    for i, ref_noise_std in enumerate(ref_noise_stds):
        for j, platform_pos_mag in enumerate(platform_pos_mags):

            #print('=' * 20)
            #print('Iteration = {}'.format(2 * i + j))
            #print('Generating simulated noisy data for:')
            #print('Reference noise std = {}'.format(ref_noise_std))
            #print('Platform position magnitude  = {}'.format(platform_pos_mag))

            data = DataGenerator(duration, num_nodes, ref_noise_std,
                                platform_pos_mag, model=model)
            data.generate(platform_accel_noise_std, coordinate_noise_std,
                        speed_noise_std, torque_noise_std)

            os.system('rm multibody_system*')

            platform_acc_stds[i, j] = data.measured['a'].std()

            direct_gains = direct_identification.identify(data.measured['u'],
                                                        data.measured['x'])
            identified_gains[i, j, :] = direct_gains

            pbar.update(2 * i + j)

    pbar.finish()

    np.savez(filename, identified_gains=identified_gains,
                       ref_noise_stds=ref_noise_stds,
                       platform_pos_mags=platform_pos_mags,
                       platform_acc_stds=platform_acc_stds)

# Plot the results.

fig, axes = plt.subplots(2, 4, subplot_kw={'projection': '3d'})
axes = axes.flatten()

# NOTE : Be careful with the 'indexing' option in meshgrid and make sure it
# matches Z. The transpose below on identified_gains makes this work out.
X, Y = np.meshgrid(ref_noise_stds, platform_acc_stds.mean(axis=0))

for i, Z in enumerate(identified_gains.T):
    axes[i].plot_surface(X[1:, :], Y[1:, :], Z[1:, :], cmap=cm.coolwarm,
                         rstride=1, cstride=1, linewidth=0,
                         antialiased=False)
