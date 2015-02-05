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
from scipy.ndimage.filters import uniform_filter

from model import QuietStandingModel
from measured_data import DataGenerator
import direct_identification
import utils

filename = os.path.join(utils.config_paths(), 'identified-gains.npz')

if os.path.isfile(filename):

    with np.load(filename) as data:
        ref_noise_stds = data['ref_noise_stds']
        platform_pos_mags = data['platform_pos_mags']
        platform_acc_stds = data['platform_acc_stds']
        identified_gains = data['identified_gains']

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

numerical_gains = np.array([[950.0, 175.0, 185.0, 50.0],
                            [45.0, 290.0, 60.0, 26.0]]).flatten()

mean_platform_acc_stds = platform_acc_stds.mean(axis=0)

# Plot the results.

fig_2d, axes_2d = plt.subplots(2, 4)
axes_2d = axes_2d.flatten()

fig_ratio, axes_ratio = plt.subplots(2, 4)
axes_ratio = axes_ratio.flatten()

###fig_3d, axes_3d = plt.subplots(2, 4, subplot_kw={'projection': '3d'})
###axes_3d = axes_3d.flatten()
###
#### NOTE : Be careful with the 'indexing' option in meshgrid and make sure it
#### matches Z. The transpose below on identified_gains makes this work out.
###X, Y = np.meshgrid(ref_noise_stds, platform_acc_stds.mean(axis=0))

# identified gains is [ref_idx, acc_idx, gain_idx]
# identified gains.T is [gain_idx, acc_idx, ref_idx]

for i, Z in enumerate(identified_gains.T):

    # relative_diff is [acc_idx, ref_idx]

    relative_diff = np.abs((Z[1:, :] - numerical_gains[i]) / numerical_gains[i])

    relative_diff = uniform_filter(relative_diff, size=5, mode='constant')

    num_ids = len(mean_platform_acc_stds) * len(ref_noise_stds)
    ratios = np.empty(num_ids)
    values = np.empty(num_ids)
    for j, acc_row in enumerate(relative_diff):
        ratios[j:j + len(ref_noise_stds)] = mean_platform_acc_stds[j] / ref_noise_stds
        values[j:j + len(ref_noise_stds)] = acc_row

    axes_ratio[i].plot(ratios[~np.isnan(ratios)] / 1000.0, values[~np.isnan(ratios)], '.')
    axes_ratio[i].set_ylim((0.0, np.max(values[ratios > 200.0])))
    if i > 3:
        axes_ratio[i].set_xlabel('ACC / REF Noise / 1000')
    if i == 0 or i == 4:
        axes_ratio[i].set_ylabel('Relative error')

    #print(np.max(relative_diff))

    max_error = 0.5

    relative_diff[relative_diff > max_error] = np.nan

    # TODO : Ensure that each image is using the same color map range so
    # that one colorbar can be used for all images.
    image = axes_2d[i].imshow(relative_diff,
                              cmap=cm.Reds,
                              vmax=max_error,
                              origin='lower')
    axes_2d[i].set_title('Gain = {}'.format(numerical_gains[i]))
    default_xticks = axes_2d[i].get_xticks()
    x_labels = np.interp(default_xticks, np.arange(len(ref_noise_stds), dtype=float), ref_noise_stds)
    axes_2d[i].set_xticklabels(['{:0.2f}'.format(r) for r in np.rad2deg(x_labels)])
    if i > 3:
        axes_2d[i].set_xlabel('Reference Noise STD [deg and deg/s]')
    default_yticks = axes_2d[i].get_yticks()
    y_labels = np.interp(default_yticks, np.arange(len(platform_acc_stds.mean(axis=0)), dtype=float), platform_acc_stds.mean(axis=0))
    axes_2d[i].set_yticklabels(['{:0.2f}'.format(a) for a in y_labels])
    if i == 0 or i == 4:
        axes_2d[i].set_ylabel('Perturbation Acceleration STD [ms^-2]')

    ###axes_3d[i].plot_surface(X[1:, :], Y[1:, :], relative_diff,
                            ###cmap=cm.coolwarm, rstride=1, cstride=1,
                            ###linewidth=0, antialiased=False)

fig_2d.subplots_adjust(right=0.8)
cax = fig_2d.add_axes([0.85, 0.1, 0.075, 0.8])
plt.colorbar(mappable=image, cax=cax)

plt.show()
