#!/usr/bin/env python

import numpy as np
from numpy.random import normal
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from opty.utils import sum_of_sines

from model import QuietStandingModel

# TODO : should all noises be a on a per variable basis?
# TODO: ref_noise_std should probably be broken up like coordinate_noise_std
# and speed_noise_std
# TODO : Maybe only pass in the right hand side function to this instead of
# the whole model.


class DataGenerator(object):

    def __init__(self, duration, num_samples, ref_noise_std,
                 platform_pos_mag, model=None):
        """

        Parameters
        ==========
        duration : float
            The duration of the data in seconds.
        num_samples : integer
            The number of equally spaced samples.
        ref_noise_std : float
            The standard deviation of the Gaussian noise applied to the
            reference signal in radians, which in this case is zero for all
            states.
        platform_pos_mag : float
            The magnitude of the sine motion of the platform in meters.
        model : instance of QuietStandingModel
            This should be a model which has already be derived.

        Notes
        =====
        The resulting data has random elements, both in the platform
        acceleration signal and the noise, so the outputs are not invariant
        with respect to the inputs.

        """

        # The rhs generation depends on the following four variables.
        self.duration = duration
        self.num_samples = num_samples
        self.ref_noise_std = ref_noise_std
        self.platform_pos_mag = platform_pos_mag

        if model is None:
            self.model = QuietStandingModel()
            self.model.derive()
        else:
            self.model = model

        self.actual = {}
        self.measured = {}

    def _generate_model_inputs(self):

        self.interval = self.duration / (self.num_samples - 1)
        self.time = np.linspace(0.0, self.duration, num=self.num_samples)

        # The person is trying to track a nominal state of [0, 0, 0, 0],
        # i.e. angles and rates are zero, but may not be able to sense the
        # error in their trajectory perfectly, so this adds some noise to
        # the reference tracking which is ultimately fed into the controller
        # and corrupts the output.
        if np.allclose(0.0, self.ref_noise_std):
            self.ref_noise = np.zeros((len(self.time), 4))
        else:
            self.ref_noise = normal(scale=self.ref_noise_std,
                                    size=(len(self.time), 4))

        # Generate a random platform acceleration input.
        nums = [7, 11, 16, 25, 38, 61, 103, 131, 151, 181, 313, 523]
        freq = 2.0 * np.pi * np.array(nums, dtype=float) / 240.0

        pos, vel, accel = sum_of_sines(self.platform_pos_mag, freq,
                                       self.time)

        self.actual['a'] = accel

        #print('Generating right hand side function.')
        self.rhs, self.r, self.p = \
            self.model.closed_loop_ode_func(self.time, self.ref_noise, accel)

    def _generate_simulation_outputs(self):

        #print('Integrating equations of motion.')
        # The initial conditions of the states are always zero.
        x = odeint(self.rhs, np.zeros(4), self.time, args=(self.r, self.p))

        # Back out the torques used in the control.
        # N x 4 = ((2 x 4) * (4 x N)).T
        u = np.dot(self.model.numerical_gains,
                   (self.ref_noise - x).T).T

        self.actual['x'] = x
        self.actual['u'] = u

    def _generate_measured_outputs(self):

        # Add measurement noise to the kinematic data.
        if np.allclose(0.0, self.platform_accel_noise_std):
            self.measured['a'] = self.actual['a']
        else:
            self.measured['a'] = self.actual['a'] + normal(
                scale=self.platform_accel_noise_std,
                size=self.actual['a'].shape)

        x = self.actual['x']
        if np.allclose(0.0, self.coordinate_noise_std):
            coord_noise = np.zeros_like(x[:, :2])
        else:
            coord_noise = normal(scale=self.coordinate_noise_std,
                                 size=x[:, :2].shape)
        if np.allclose(0.0, self.speed_noise_std):
            speed_noise = np.zeros_like(x[:, 2:])
        else:
            speed_noise = normal(scale=self.speed_noise_std,
                                 size=x[:, 2:].shape)
        x_noise = np.hstack((coord_noise, speed_noise))
        x_meas = x + x_noise

        # Add measurement noise to the joint torques.
        u = self.actual['u']
        if np.allclose(0.0, self.torque_noise_std):
            u_meas = u
        else:
            u_meas = u + normal(scale=self.torque_noise_std, size=u.shape)

        self.measured['x'] = x_meas
        self.measured['u'] = u_meas

    def generate(self, platform_accel_noise_std, coordinate_noise_std,
                 speed_noise_std, torque_noise_std):

        """
        Parameters
        ==========

        platform_accel_noise_std : float
            The standard deviation of the Gaussian noise in meters applied
            to the actual acceleration to create the measured acceleration.
        coordinate_noise_std : float
            The standard deviation of the Gaussian noise in radians applied
            to the actual angular generalized coordinates.
        speed_noise_std : float
            The standard deviation of the Gaussian noise in radians applied
            to the actual angular rate generailized speeds.
        torque_noise_std : float
            The standard deviation of the Gaussian noise in N-m applied to
            the actual joint torques to create the measured joint torques.
        """

        # Measurement noise, doesn't require a model recomputation.
        self.platform_accel_noise_std = platform_accel_noise_std
        self.coordinate_noise_std = coordinate_noise_std
        self.speed_noise_std = speed_noise_std
        self.torque_noise_std = torque_noise_std

        self._generate_model_inputs()
        self._generate_simulation_outputs()
        self._generate_measured_outputs()

    def plot(self):

        fig, axes = plt.subplots(3, 1, sharex=True)

        axes[0].plot(self.time, self.measured['x'], 'k.',
                     self.time, self.actual['x'])
        axes[0].set_ylabel('States')

        axes[1].plot(self.time, self.measured['u'], 'k.',
                     self.time, self.actual['u'])
        axes[1].set_ylabel('Joint Torques')

        axes[2].plot(self.time, self.measured['a'], 'k.',
                     self.time, self.actual['a'])
        axes[2].set_ylabel('Platform Acceleration')
        axes[2].set_xlabel('Time [s]')

        plt.show()
