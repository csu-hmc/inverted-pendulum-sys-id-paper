#!/usr/bin/env python

import numpy as np


def sum_of_squares(measured_states, simulated_states):
    """

    Parameters
    ----------
    measured_states : array_like, shape(n, 4)
    simulated_states : array_like, shape(n, 4)

    Returns
    -------
    sum_of_squares : float
        The unweighted sum of the squares in the difference between the
        measured and simulated states.

    """

    return np.sum((measured_states - simulated_states) ** 2)
