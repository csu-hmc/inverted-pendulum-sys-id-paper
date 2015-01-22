#!/usr/bin/env python

import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize
from opty.direct_collocation import Problem
from opty.utils import sum_of_sines
import cma

from model import PlanarStandingHumanOnMovingPlatform
from direct_identification import ControllerIdentifier
from shooting import objective


print('Generating equations of motion.')
# We are going to scale the gains so that the values we search for with
# IPOPT are all close to 0.5 instead of the large gain values.
h = PlanarStandingHumanOnMovingPlatform(scaled_gains=0.5 * np.ones((2, 4)))
h.derive()

num_nodes = 4000
duration = 20.0
interval = duration / (num_nodes - 1)
time = np.linspace(0.0, duration, num=num_nodes)

# ref noise seems to introduce error in the parameter id
ref_noise = np.random.normal(scale=np.deg2rad(1.0), size=(len(time), 4))
#ref_noise = np.zeros((len(time), 4))

# Generate a random platform acceleration input.
nums = [7, 11, 16, 25, 38, 61, 103, 131, 151, 181, 313, 523]
freq = 2.0 * np.pi * np.array(nums, dtype=float) / 240.0
pos, vel, accel = sum_of_sines(0.01, freq, time)
accel_meas = accel + np.random.normal(scale=np.deg2rad(0.25),
                                        size=accel.shape)

print('Generating right hand side function.')
rhs, rhs_args = h.closed_loop_ode_func(time, ref_noise, accel)

print('Integrating equations of motion.')
x0 = np.zeros(4)
x = odeint(rhs, x0, time, args=(rhs_args,))

# Back out the torques used in the control and add noise.
# N x 4 = ((2 x 4) * (4 x N)).T
u = -np.dot(h.numerical_gains, x.T).T
u_meas = u + np.random.normal(scale=0.5, size=u.shape)

# Add measurement noise to the kinematic data.
x_meas = x + np.random.normal(scale=np.deg2rad(0.25), size=x.shape)
