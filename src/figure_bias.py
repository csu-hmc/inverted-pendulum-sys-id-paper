#!/usr/bin/env python

"""This figure tries to show how one needs have a "ratio" of external
perturbations to reference noise that is of some value > 1 (if perturbations
are normalized) to properly directly identify the controller."""

import os

import numpy as np
from scipy.ndimage.filters import uniform_filter
from progressbar import ProgressBar
from matplotlib import cm
import matplotlib.pyplot as plt
# this import is required for the projection='3d' to work
from mpl_toolkits.mplot3d.axes3d import Axes3D
import logbook

from model import QuietStandingModel
import indirect_collocation
import direct_identification
import utils

KNOWN_GAINS = np.array([[950.0, 175.0, 185.0, 50.0],
                        [45.0, 290.0, 60.0, 26.0]])

file_names = {'input_data': 'bias_comparison_input_data.npz',
              'direct_results': 'directly-identified-gains.npy',
              'indirect_results': 'indirectly-indentified-gains.npz',
              'indirect_times': 'indirect-times.npz',
              'indirect_status': 'indirect-status.npz'}
file_paths = {k: os.path.join(utils.config_paths(), v) for k, v in
              file_names.items()}

# TODO : This is a bad hack. Fix.
from generate_bias_comparison_input_data import (ref_noise_stds,
                                                 platform_pos_mags,
                                                 platform_acc_stds,
                                                 reference_noises,
                                                 measured_accel,
                                                 measured_states,
                                                 measured_joint_torques)


def identify_gains_indirectly():
    # create a Problem for each of the platform eaccelerations because that
    # is although it seems like you may be able to change out the
    # known_trajectory_map dynamically in the constrain collocator.  the obj
    # and obj_grad is easily subbed out

    if os.path.isfile(file_paths['indirect_results']):

        logbook.info('Loading precomputed indirectly identified gains.')
        identified_gains = np.load(file_paths['indirect_results'])

    else:
        logbook.info('Indirectly identifying gains.')

        n = len(ref_noise_stds)
        m = len(platform_pos_mags)

        shape = (n, m, KNOWN_GAINS.size)
        identified_gains = np.empty(shape, dtype=float)

        status_nums = np.empty((n, m), dtype=int)
        times = np.empty((n, m), dtype=float)

        model = QuietStandingModel(scaled_gains=0.5)
        model.derive()

        num_nodes = measured_states[0, 0].shape[0]
        duration = 5.0  # TODO : This should be in the generated data.
        time_interval = duration / (num_nodes - 1)

        # set the problem up with some dummy inputs
        prob = indirect_collocation.setup_problem(num_nodes, time_interval,
                                                  measured_states[0, 0].T.flatten(),
                                                  measured_accel[0, 0],
                                                  model)

        prob.addOption('print_level', 0)
        prob.addOption('sb', "yes")  # suppress IPOPT banner
        prob.addOption('linear_solver', 'ma57')
        prob.addOption('max_iter', 300)
        # 3 seconds will take 8 hrs for 10200 trials
        # 5 seconds will take 14 hrs
        prob.addOption('max_cpu_time', 6.0)

        acc_sym = model.specifieds['platform_acceleration']
        initial_guess = np.zeros(prob.num_free)
        # Give it the known gains as a guess, because all we care about is
        # how the optimal solution is affected by the accel and noise.
        initial_guess[-8:] = model.numerical_gains.flatten()

        f = open('status.csv', 'w')
        f.write('i,j,status,status_msg\n')

        logbook.info('Staring loop.')

        pbar = ProgressBar(maxval=n * m)
        pbar.start()

        count = 0
        for i in range(n):
            for j in range(m):

                x_meas_vec = measured_states[i, j].T.flatten()
                initial_guess[:-8] = x_meas_vec
                prob.obj = indirect_collocation.nlp_obj(
                    num_nodes, time_interval, x_meas_vec)
                prob.obj_grad = indirect_collocation.nlp_obj_grad(
                    num_nodes, time_interval, x_meas_vec)
                prob.collocator.known_trajectory_map[acc_sym] = measured_accel[i, j]
                # TODO : Time this call.
                @utils.timeit
                def solve():
                    solution, info = prob.solve(initial_guess)
                    return solution, info
                solution, info, time = solve()
                times[i, j] = time
                status_nums[i, j] = int(info['status'])
                line = '{},{},{},{}\n'.format(i, j, info['status'], info['status_msg'])
                f.write(line)
                # TODO : Capture if it doesn't find a solution.
                identified_gains[i, j, :] = \
                    model.gain_scale_factors.flatten() * solution[-8:]

                pbar.update(count)
                count += 1

        logbook.info('Loop done.')

        f.close()

        pbar.finish()

        np.save(file_paths['indirect_results'], identified_gains)
        np.save(file_paths['indirect_status'], status_nums)
        np.save(file_paths['indirect_times'], times)

    return identified_gains


def identify_gains_directly():

    if os.path.isfile(file_paths['direct_results']):

        print('Loading precomputed directly identified gains.')
        identified_gains = np.load(file_paths['direct_results'])

    else:
        print('Directly identifying gains.')

        n = len(ref_noise_stds)
        m = len(platform_pos_mags)

        shape = (n, m, KNOWN_GAINS.size)
        identified_gains = np.empty(shape, dtype=float)

        pbar = ProgressBar(maxval=len(ref_noise_stds) * len(platform_pos_mags))
        pbar.start()

        count = 0

        for i in range(n):
            for j in range(m):

                direct_gains = direct_identification.identify(
                    measured_joint_torques[i, j],
                    measured_states[i, j])

                identified_gains[i, j, :] = direct_gains

                pbar.update(count)
                count += 1

        pbar.finish()

        np.save(file_paths['direct_results'], identified_gains)

    return identified_gains


def relative_error(identified_gains):
    """Returns an array that contains the absolute value of the relative
    error of the identified gains with respect to the known gains.

    Parameters
    ==========
    identified_gains : ndarray, shape(n, m, 8)

    Returns
    =======
    error : ndarray, shape(n, m, 8)


    """

    known_gains = KNOWN_GAINS.flatten()

    error = np.empty_like(identified_gains.T)

    # identified gains is [ref_idx, acc_idx, gain_idx]
    # identified gains.T is [gain_idx, acc_idx, ref_idx]

    # for each gain
    for k, gain in enumerate(identified_gains.T):

        # gain is [acc_idx, ref_idx]

        error[k] = np.abs((gain - known_gains[k]) /
                          known_gains[k])

    return error.T


def plot_gain_error_vs_acc_and_ref_noise_2d(ref_noise_stds,
                                            platform_acc_stds,
                                            relative_error,
                                            filter=False):

    max_error = 1.0

    # copy the data so we don't booger it up
    relative_error = relative_error.copy()

    known_gains = KNOWN_GAINS.flatten()

    fig, axes = plt.subplots(2, 4)
    axes = axes.flatten()

    for k, gain_error in enumerate(relative_error.T):

        if filter:
            gain_error = uniform_filter(gain_error, size=5, mode='constant')

        # Don't plot error above 100%.
        gain_error[gain_error > max_error] = np.nan

        # gain_error is indexed [j: acc_idx, i: ref_idx]
        # imshow will put the acc on the y and ref on the x with the origin
        # at the lower left
        cmap = cm.Reds
        # plot nans (masked values) with a green square
        cmap.set_bad('g', 1.)
        image = axes[k].imshow(np.ma.array(gain_error,
                                           mask=np.isnan(gain_error)),
                               cmap=cmap,
                               vmax=max_error,
                               interpolation='none',
                               origin='lower')

        axes[k].set_title('Gain = {}'.format(known_gains[k]))

        default_xticks = axes[k].get_xticks()
        x_labels = np.interp(default_xticks,
                             np.arange(len(ref_noise_stds), dtype=float),
                             ref_noise_stds)
        axes[k].set_xticklabels(['{:0.2f}'.format(r) for r in
                                np.rad2deg(x_labels)])

        if k > 3:
            axes[k].set_xlabel('Reference Noise STD [deg and deg/s]')

        default_yticks = axes[k].get_yticks()
        y_labels = np.interp(default_yticks,
                             np.arange(len(platform_acc_stds.mean(axis=0)),
                                       dtype=float),
                             platform_acc_stds.mean(axis=0))
        axes[k].set_yticklabels(['{:0.2f}'.format(a) for a in y_labels])

        if k == 0 or k == 4:
            axes[k].set_ylabel('Perturbation Acceleration STD [ms^-2]')

    fig.subplots_adjust(right=0.9)
    # [Left Bottom Width Height]
    cax = fig.add_axes([0.95, 0.1, 0.025, 0.8])
    plt.colorbar(mappable=image, cax=cax)

    return fig, axes


def plot_gain_error_vs_acc_ref_noise_ratio(ref_noise_stds,
                                           platform_acc_stds,
                                           relative_error, filter=False):
    """Returns a figure and its axes.

    Parameters
    ==========
    ref_noise_stds : ndarray, shape(n,)
    platform_acc_stds : ndarray, shape(n, m)
    relative_error : ndarray, shape(n, m, p)

    """

    known_gains = KNOWN_GAINS.flatten()

    # one subplot per gain
    fig, axes = plt.subplots(2, 4)
    axes = axes.flatten()

    # platform_acc_stds is indexed [i: ref_idx, j: acc_idx]
    n, m = platform_acc_stds.shape
    # this creates an n, m array such that the ref noise vector is repeated
    # in reverse along m columns
    rep = np.repeat(ref_noise_stds[::-1].reshape(n, 1), m, axis=1)
    assert rep.shape == (n, m)
    rep[rep < 1e-10] = np.nan  # avoid divide by zeros
    # ratios is indexed [j: acc_idx, i: ref_idx]
    ratios = np.transpose(platform_acc_stds / rep)

    # relative_error.T is [k: gain_err_idx, j: acc_idx, i: ref_idx]
    for k, gain_error in enumerate(relative_error.T):

        if filter:
            gain_error = uniform_filter(gain_error, size=5, mode='constant')

        # gain_error is indexed [j: acc_idx, i: ref_idx]

        assert ratios.shape == gain_error.shape

        axes[k].set_title('Gain = {}'.format(known_gains[k]))

        axes[k].plot(ratios.flatten() / 1000.0,
                     gain_error.flatten(), '.')

        axes[k].set_ylim((0.0, 1.0))

        if k > 3:
            axes[k].set_xlabel('ACC / REF / 1000')

        if k == 0 or k == 4:
            axes[k].set_ylabel('Relative error')

    return fig, axes


def plot_gain_error_vs_acc_ref_noise_3d(ref_noise_stds,
                                        platform_acc_stds,
                                        relative_error):

    fig, axes = plt.subplots(2, 4, subplot_kw={'projection': '3d'})
    axes = axes.flatten()

    # NOTE : Be careful with the 'indexing' option in meshgrid and make sure it
    # matches Z. The transpose below on identified_gains makes this work out.
    X, Y = np.meshgrid(ref_noise_stds, platform_acc_stds.mean(axis=0))

    # identified gains is [ref_idx, acc_idx, gain_idx]
    # identified gains.T is [gain_idx, acc_idx, ref_idx]

    for i, Z in enumerate(identified_gains.T):

        # Skip the first index because it is always super high.
        axes[i].plot_surface(X[1:, :], Y[1:, :], relative_error,
                             cmap=cm.coolwarm, rstride=1, cstride=1,
                             linewidth=0, antialiased=False)

    return fig, axes
