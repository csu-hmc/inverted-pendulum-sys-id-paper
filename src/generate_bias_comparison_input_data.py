#!/usr/bin/env python

"""This script generates a grid of data that can be used for
identification."""

import os

import numpy as np
from progressbar import ProgressBar
from joblib import Parallel, delayed

from model import QuietStandingModel
from measured_data import DataGenerator
import utils

NUM_GAINS = 8

file_name = 'bias_comparison_input_data.npz'
file_path = os.path.join(utils.config_paths(), file_name)

if os.path.isfile(file_path):

    print('Loading precomputed input data.')

    with np.load(file_path) as data:
        # time = data['time']
        ref_noise_stds = data['ref_noise_stds']
        platform_pos_mags = data['platform_pos_mags']
        platform_acc_stds = data['platform_acc_stds']
        reference_noises = data['reference_noises']
        measured_accel = data['measured_accel']
        measured_states = data['measured_states']
        measured_joint_torques = data['measured_joint_torques']

else:

    print('Computing input data, may take a while...')

    # TODO : The following should probably be arguments to a function and/or
    # command line.
    num_nodes = 501
    duration = 5.0
    num_ref_noise_stds = 101
    num_platform_pos_mags = 101
    max_ref_noise_std = 0.04  # radians and radian/sec
    max_platform_pos_mag = 0.1  # meters

    # All measurement noise is set to zero.
    platform_accel_noise_std = 0.0
    coordinate_noise_std = 0.0
    speed_noise_std = 0.0
    torque_noise_std = 0.0

    # Generate the symbolic dynamic model.
    model = QuietStandingModel()
    model.derive()

    # Generate the input values.
    ref_noise_stds = np.linspace(0.0, max_ref_noise_std,
                                 num=num_ref_noise_stds)
    platform_pos_mags = np.linspace(0.0, max_platform_pos_mag,
                                    num=num_platform_pos_mags)

    # Create empty arrays to store all generated data.
    platform_acc_stds = np.empty((num_ref_noise_stds,
                                  num_platform_pos_mags), dtype=float)
    reference_noises = np.empty((num_ref_noise_stds, num_platform_pos_mags,
                                 num_nodes, 4), dtype=float)
    measured_accel = np.empty((num_ref_noise_stds, num_platform_pos_mags,
                               num_nodes), dtype=float)
    measured_states = np.empty((num_ref_noise_stds, num_platform_pos_mags,
                                num_nodes, 4), dtype=float)
    measured_joint_torques = np.empty((num_ref_noise_stds,
                                       num_platform_pos_mags, num_nodes, 2),
                                      dtype=float)

    # Create this object and generate the rhs once (internally), then we'll
    # just switch out the ref_noise and platform_position each time in the
    # loop without having to regenerate the rhs function.
    data = DataGenerator(duration, num_nodes, ref_noise_stds[0],
                         platform_pos_mags[0], model=model)
    data.generate(platform_accel_noise_std, coordinate_noise_std,
                  speed_noise_std, torque_noise_std)

    pbar = ProgressBar(maxval=len(ref_noise_stds))
    pbar.start()

    def gen(platform_pos_mag):

        # This is necessary so that each forked process gets the seed reset.
        np.random.seed()

        data.platform_pos_mag = platform_pos_mag

        data._generate_model_inputs()
        # Skip the rhs generation call but change out the variables
        # needed in the controller function. This can only be done if
        # the size of ref_noise and actual['a'] do not change in this
        # loop. This saves computation time.
        data.model.all_sigs[:, :] = np.hstack(
            (data.ref_noise, np.expand_dims(data.actual['a'], 1)))
        data._generate_simulation_outputs()
        data._generate_measured_outputs()

        x_n = data.actual['x_n']
        a = data.measured['a']
        x = data.measured['x']
        u = data.measured['u']

        return x_n, a, x, u

    for i, ref_noise_std in enumerate(ref_noise_stds):

        data.ref_noise_std = ref_noise_std

        res = Parallel(n_jobs=-1)(delayed(gen)(platform_pos_mag) for
                                  platform_pos_mag in platform_pos_mags)

        for j, (x_n, a, x, u) in enumerate(res):

            platform_acc_stds[i, j] = a.std()
            reference_noises[i, j, :, :] = x_n
            measured_accel[i, j, :] = a
            measured_states[i, j, :, :] = x
            measured_joint_torques[i, j, :, :] = u

        pbar.update(i)

    pbar.finish()

    np.savez(file_path,
             time=data.time,
             ref_noise_stds=ref_noise_stds,
             platform_pos_mags=platform_pos_mags,
             platform_acc_stds=platform_acc_stds,
             reference_noises=reference_noises,
             measured_accel=measured_accel,
             measured_states=measured_states,
             measured_joint_torques=measured_joint_torques)
