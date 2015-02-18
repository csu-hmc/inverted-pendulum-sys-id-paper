#!/usr/bin/env python

"""This shows how the data generation can be parallelized. For 16 runs, I'm
getting twice the speed up as compared to the sequential method."""

from multiprocessing import Pool

import numpy as np
from joblib import Parallel, delayed

from model import QuietStandingModel
from measured_data import DataGenerator
from utils import timeit

num_nodes = 51
duration = 5.0

ref_noise_std = 0.03
platform_accel_noise_std = 0.0
coordinate_noise_std = 0.0
speed_noise_std = 0.0
torque_noise_std = 0.0

# Generate the symbolic dynamic model.
model = QuietStandingModel()
model.derive()

num = 12


def gen(platform_pos_mag):

    # This involves generating the rhs function and is slower.
    data = DataGenerator(duration, num_nodes, ref_noise_std,
                         platform_pos_mag, model=model)
    # This step is fast.
    data.generate(platform_accel_noise_std, coordinate_noise_std,
                  speed_noise_std, torque_noise_std)

    # NOTE : You can't return the data object here because something inside
    # it can't be pickled, so I return the dictionary instead.
    return data.measured

platform_pos_mags = np.linspace(0.0, 0.3, num=num)

pool = Pool()


@timeit
def run_joblib():
    return Parallel(n_jobs=-1)(delayed(gen)(platform_pos_mag) for
                               platform_pos_mag in platform_pos_mags)


@timeit
def run_multiprocessing():
    return pool.map(gen, [p for p in platform_pos_mags])


@timeit
def run_sequential():
    for p in platform_pos_mags:
        gen(p)


if __name__ == "__main__":
    run_sequential()
    run_multiprocessing()
    run_joblib()
